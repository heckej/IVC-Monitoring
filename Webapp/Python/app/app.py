import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, request, flash, url_for, redirect, render_template, jsonify, json, make_response
from flask_sqlalchemy import SQLAlchemy
from time import gmtime, strftime, sleep
from sql import getSetting, getCageInfo, getCages, updateSetting
from collections import OrderedDict
from cages import updateCage, updateCages
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
connected = False
while not connected:
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ivc:ivcmonitoring@127.0.0.1/ivcmonitoring'
        app.config['MYSQL_USER'] = 'ivc'
        app.config['MYSQL_PASSWORD'] = 'ivcmonitoring'
        app.config['MYSQL_DB'] = 'ivcmonitoring'
        """app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/ivc-monitoring'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = ''
        app.config['MYSQL_DB'] = 'ivc-monitoring'"""
        app.config['SECRET_KEY'] = "random string"

        db = SQLAlchemy(app)
        connected = True
    except Exception as error:
        connected = False
        print(error)
        sleep(1)
class settings(db.Model):
    id = db.Column('settings_id', db.Integer, primary_key = True)
    setting = db.Column(db.String(100))
    value = db.Column(db.String(65))


    def __init__(self, setting, value):
     self.setting = setting
     self.value = value



class cage_settings(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    cage_id = db.Column(db.String(3), unique=True)
    notif_food = db.Column(db.Boolean)
    notif_water = db.Column(db.Boolean)
    notif_warning = db.Column(db.Boolean)
    port = db.Column(db.String(65))
    description = db.Column(db.Text(1024))
    get_notif = db.Column(db.Boolean)
    def __init__(self, cage_id, port, description="", notifications=True, notification_food=False, notification_water=False, notification_warning=False):
        self.cage_id = cage_id
        self.port = port
        self.notif_food = notification_food
        self.notif_water = notification_water
        self.notif_warning = notification_warning
        self.description = description
        self.get_notif = notifications




class notifications(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    cage_id = db.Column(db.String(3))
    notif_datetime = db.Column(db.DateTime, default=strftime("%Y-%m-%d %H:%M:%S", gmtime()), nullable=False)
    msg = db.Column(db.String(140))
    notif_type = db.Column("type", db.String(65))

    def __init__(self, cage_id, message, notif_type, notif_datetime):
        self.cage_id = cage_id
        self.msg = message
        self.notif_type = notif_type
        self.notif_datetime = notif_datetime

class measurements(db.Model):
    measure_id = db.Column(db.Integer, primary_key = True)
    cage_id = db.Column(db.String(3))
    measure_datetime = db.Column(db.DateTime, default=strftime("%Y-%m-%d %H:%M:%S", gmtime()), nullable=False)
    food_status = db.Column(db.Boolean)
    water_level = db.Column(db.Integer)
    measure_type = db.Column("type", db.String(10))

    def __init__(self, cage_id, food_status, water_level, measure_datetime, measure_type):
        self.cage_id = cage_id
        self.food_status = food_status
        self.water_level = water_level
        self.measure_datetime = measure_datetime
        self.measure_type = measure_type


@app.route('/', methods=['POST'])
def show_all():
    #flash(settings.query.filter_by(setting = "limit").all())
    cages = {}
    result = cage_settings.query.filter((cage_settings.notif_food == True) | (cage_settings.notif_water == True)).all()
    #return str(len(result))
    for i in range(len(result)):
        cage_id = result[i].cage_id
        cages[cage_id] = dict()
        #cages[cage] = (result[i].notification_food, result[i].notification_water)
        cages[cage_id]["food"] = result[i].notif_food
        cages[cage_id]["water"] = result[i].notif_water
    return jsonify(cages)
    #return jsonify(cage=result.cage_id, food=result.notification_food, water=result.notification_water)
    #return render_template('settings.html', setting=result[0])

@app.route("/cages")
def cages():
    r = make_response(render_template('cages.html', cages=cage_settings.query.all()))
    r.headers.set('Access-Control-Allow-Origin', "*")
    return r

@app.route("/cage/<cage_id>")
def cage(cage_id):
    if cage_id == "all":
        return redirect(url_for('cages'))
    cageSettings = cage_settings.query.filter(cage_settings.cage_id == cage_id).first()
    try:
        port = cageSettings.port
    except (KeyError, AttributeError):
        # In case the cage ID is unknown
        return redirect(url_for('registerCage', cage_id=cage_id))

    measure = measurements.query.filter(measurements.cage_id == cage_id).order_by(measurements.measure_datetime.desc()).first()
    measureAll = measurements.query.filter(measurements.cage_id == cage_id).order_by(measurements.measure_datetime.desc()).all()
    notifs = notifications.query.filter(notifications.cage_id == cage_id).order_by(notifications.notif_datetime.desc()).all()
    notifState = cage_settings.query.filter(cage_settings.cage_id == cage_id).first()
    try:
        if measure.water_level < int(getSetting('water_limit')):
            waterShortage = True
        else:
            waterShortage = False
        foodShortage = not measure.food_status
        lastMeasure = measure.measure_datetime
    except (KeyError, AttributeError):
        waterShortage = None
        foodShortage = None
        lastMeasure = "never"

    cage_info = dict()
    cage_info['cage_id'] = cage_id
    cage_info['last_update'] = lastMeasure
    cage_info['water'] = waterShortage
    cage_info['food'] = foodShortage
    cage_info['notifications'] = dict()
    for i in range(len(notifs)):
        notif_id = notifs[i].id
        cage_info['notifications'][notif_id] = dict()
        cage_info['notifications'][notif_id]['datetime'] = notifs[i].notif_datetime
        cage_info['notifications'][notif_id]['message'] = str(notifs[i].msg)
        cage_info['notifications'][notif_id]['type'] = str(notifs[i].notif_type)
    cage_info['notifications'] = OrderedDict(sorted(cage_info['notifications'].items(), reverse=True))

    j = 0
    if len(measureAll) > 0:
        while len(measureAll) > j and bool(measureAll[j].food_status):
            print(j)
            print(measureAll[j].food_status)
            j += 1
        while j < len(measureAll) and not bool(measureAll[j].food_status):
            print(j)
            print(measureAll[j].food_status)
            j += 1

        j -= 1

    try:
        supplyDatetime = measureAll[j].measure_datetime
        if supplyDatetime == lastMeasure:
            supplyDatetime = "never"
    except (KeyError, IndexError):
        supplyDatetime = "never"

    cage_info['last_supply'] = supplyDatetime

    """for j in range(len(measureAll)):
        if not firstZero:
            if measureAll[j].measure_datetime == 0:
                firstZero = True
        else:
            if measureAll[j].measure_datetime == 1:
                j -= 1
                break"""

    r = make_response(render_template('cage_details.html', cage=cage_info))
    r.headers.set('Access-Control-Allow-Origin', "*")
    return r

@app.route("/cage/<cage_id>/updates", methods=['POST'])
def cageUpdates(cage_id):
    measure = measurements.query.filter(measurements.cage_id == cage_id).order_by(measurements.measure_datetime.desc()).first()
    notif = notifications.query.filter(notifications.cage_id == cage_id).order_by(
        notifications.notif_datetime.desc()).first()
    #result = cage_settings.query.filter((cage_settings.notif_food == True) | (cage_settings.notif_water == True)).all()
    # return str(len(result))
    update = dict()
    update["cage_id"] = cage_id
    try:
        # cages[cage] = (result[i].notification_food, result[i].notification_water)
        update["food"] = not bool(measure.food_status) # False means no food: shortage, True means food: no shortage
        if measure.water_level < int(getSetting('water_limit')):
            update["water"] = True
        else:
            update["water"] = False
        update["notification"] = dict()
        update["notification"]["msg"] = notif.msg
        update["notification"]["datetime"] = notif.notif_datetime
        update["notification"]["id"] = notif.id
        update["notification"]["type"] = notif.notif_type
    except (KeyError, AttributeError) as error:
        update["food"] = None
        update["water"] = None
        update["error"] = True
        update["error_msg"] = str(error)
    return jsonify(update)

@app.route("/updates")
def updates():
    tod = datetime.datetime.now()
    d = datetime.timedelta(days=50)
    dateLimit = str(tod - d)

    notifs = notifications.query.filter(notifications.notif_datetime >= dateLimit).order_by(notifications.notif_datetime.desc()).all()
    notifInfo = dict()
    for i in range(len(notifs)):
        notif_id = notifs[i].id
        notifInfo[notif_id] = dict()
        notifInfo[notif_id]['datetime'] = notifs[i].notif_datetime
        notifInfo[notif_id]['message'] = str(notifs[i].msg)
        notifInfo[notif_id]['type'] = str(notifs[i].notif_type)
        notifInfo[notif_id]['cage_id'] = notifs[i].cage_id
        notifInfo = OrderedDict(sorted(notifInfo.items(), reverse=True))

    r = make_response(render_template('notifications.html', notifications=notifInfo))
    r.headers.set('Access-Control-Allow-Origin', "*")
    return r

@app.route("/refresh/<cage_id>", methods=['POST', 'GET'])
def refresh(cage_id):
    msg = dict()
    msg['msg'] = "Cages up to date"
    msg['cage_id'] = cage_id
    if cage_id == "all":
        updateCages()
        print("all")
    else:
        try:
            if not updateCage(cage_id):
                updated = False
        except Exception as error:
            msg['msg'] = cage_id + " is not a valid cage id."
            msg['error'] = str(error)
            print(msg)
    return redirect(url_for('cage', cage_id=cage_id), code=307)
    # return jsonify(msg)

@app.route("/register/<cage_id>")
def registerCage(cage_id):
    return "This page isn't ready yet."

@app.route("/register")
def register():
    return "This page isn't ready yet."

@app.route("/settings", methods=['GET', 'POST'])
def settingsPage():
    updated = False
    reset = False
    form = request.form
    if request.method == 'POST':
        if "setting-water_limit" in form:
            updated = True
            updateSetting('water_limit', form["setting-water_limit"])
            updateSetting('measure_interval', form["setting-measure_interval"])
        elif "reset" in form:
            resetApp()
            reset = True

    water_limit = getSetting('water_limit')
    measure_interval = getSetting('measure_interval')
    return render_template('settings.html', water_limit=water_limit, measure_interval=measure_interval, updated=updated, reset=reset)

"""
@app.route('/setting/add')
def new():
    setting = settings("limit", 200)

    db.session.add(setting)
    db.session.commit()
    flash('Record was successfully added')
    return redirect(url_for('show_all'))"""



"""
@app.route('/new')
def new():
    notification_food = cage_settings(True)

    db.session.add(notifications_food)
    db.session.commit()
    flash('Record was successfully added')


    notification_water = cage_settings()

    db.session.add(notifications_water)
    db.session.commit()
    flash('Record was successfully added')


    return redirect(url_for('show_all'))


@app.route('/new')
def new():
    notification_food = notifications()

    db.session.add(notification_food)
    db.session.commit()
    flash('Record was successfully added')


    notification_water = notifications()

    db.session.add(notification_water)
    db.session.commit()
    flash('Record was successfully added')


    return redirect(url_for('show all'))
"""
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=5000, host='0.0.0.0')




