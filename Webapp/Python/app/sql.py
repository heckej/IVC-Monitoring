import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, Text
from time import localtime, strftime, sleep
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

#engine = create_engine("mysql://root:@127.0.0.1/ivc-monitoring",echo = True)
# uncomment next line to use on raspberry pi sql server
connected = False
while not connected:
    try:
        engine = create_engine("mysql://ivc:ivcmonitoring@127.0.0.1/ivcmonitoring",echo = True)
        connected = True
    except Exception as error:
        connected = False
        print(error)
        sleep(1)
meta = MetaData()

measurements = Table(
    'measurements', meta,
    Column('measure_id', Integer, primary_key=True),
    Column('cage_id', String(3)),
    Column('measure_datetime', DateTime, default=strftime("%Y-%m-%d %H:%M:%S", localtime()), nullable=False),
    Column('food_status', Boolean),
    Column('water_level', Integer)
)

def addMeasurementToDB(cageID, foodStatus, waterLevel, measure_type):
    """
    Add row with foodStatus and waterLevel to the database
    :param cageID: str
    :param foodStatus: bool
    :param waterLevel: int
    :param measure_type: str: the way a the results were received: manual, auto [interval]
    :return:
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    data = Measurements(cage_id=cageID, food_status=foodStatus, water_level=waterLevel, measure_datetime=strftime("%Y-%m-%d %H:%M:%S", localtime()), measure_type=measure_type)
    session.add(data)
    session.commit()

def addNotification(cageID, message, notif_type):
    """
    Add a new notification to the database
    :param message:
    :param type:
    :return:
    """
    if notif_type not in ['food', 'water', 'warning']:
        raise ValueError("The value of type should be either 'food', 'water' or 'warning'.")
    else:
        Session = sessionmaker(bind=engine)
        session = Session()
        data = Notifications(cage_id=cageID, message=message, notif_type=notif_type, notif_datetime=strftime("%Y-%m-%d %H:%M:%S", localtime()))
        session.add(data)
        session.commit()

def setNotificationFlag(cageID, notif_type, value):
    """
    Set notification flag of food or water to either True or False depending on whether there's already added one
    after detecting a shortage since the last supply
    :param cageID:
    :param type: str 'food' or 'water'
    :return: None
    """
    try:
        value = bool(value)
    except ValueError:
        raise ValueError("'value' should be a boolean.")
    if notif_type not in ['food', 'water', 'warning']:
        raise ValueError("The value of type should be either 'food' or 'water'.")
    else:
        Session = sessionmaker(bind=engine)
        session = Session()
        cage = session.query(CageSettings).filter_by(cage_id=cageID).first()
        print(cage)
        if notif_type == "water":
            cage.notif_water = value
        elif notif_type == "warning":
            cage.notif_warning = value
        else:
            cage.notif_food = value
        session.commit()

def getNotificationFlag(cageID, notif_type):
    """
    Return notification flag of food or whether for a given cage
    :param cageID:
    :param type:
    :return:
    """
    if notif_type not in ['food', 'water', 'warning']:
        raise ValueError("The value of type should be either 'food' or 'water'.")
    else:
        Session = sessionmaker(bind=engine)
        session = Session()
        cage = session.query(CageSettings).filter_by(cage_id=cageID).first()
        if notif_type == "water":
            return bool(int(cage.notif_water))
        elif notif_type == "warning":
            return bool(int(cage.notif_warning))
        else:
            return bool(int(cage.notif_food))

def updateSetting(name, value):
    """
    Add setting or update existing one
    :param name: 
    :param value: 
    :return: 
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    setting = session.query(Settings).filter_by(setting=name).first()
    try:
        # This should work in case it's an existing setting
        setting.value = value
    except AttributeError:
        # The setting doesn't exist yet
        data = Settings(name, value)
        session.add(data)
    session.commit()

def getSetting(name):
    """
    Get setting value
    :param name:
    :return:
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    setting = session.query(Settings).filter_by(setting=name).first()
    try:
        # This should work in case it's an existing setting
        value = setting.value
        return value
    except AttributeError:
        return None

def getSettings():
    Session = sessionmaker(bind=engine)
    session = Session()
    settings = session.query(Settings).all()
    return settings

def getCages():
    """
    Get information on all cages
    :return:
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    cages = session.query(CageSettings).all()
    return cages

def getCageInfo(cageID):
    """
    Get information on one specific cage
    :return:
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    cage = session.query(CageSettings).filter_by(cage_id=cageID).first()
    return cage

def resetApp():
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Measurements).delete()
    reset = text('ALTER TABLE tbl AUTO_INCREMENT = 100;')
    session.execute(reset)


class Measurements(Base):
    __tablename__ = 'measurements'
    measure_id = Column(Integer, primary_key = True)
    cage_id = Column(String(3))
    measure_datetime = Column(DateTime, default=strftime("%Y-%m-%d %H:%M:%S", localtime()), nullable=False)
    food_status = Column(Boolean)
    water_level = Column(Integer)
    measure_type = Column("type", String(10))

    def __init__(self, cage_id, food_status, water_level, measure_datetime, measure_type):
        self.cage_id = cage_id
        self.food_status = food_status
        self.water_level = water_level
        self.measure_datetime = measure_datetime
        self.measure_type = measure_type


class CageSettings(Base):
    __tablename__ = "cage_settings"
    id = Column(Integer, primary_key = True)
    cage_id = Column(String(3), unique=True)
    port = Column(String(65), unique=True)
    notif_food = Column(Boolean)
    notif_water = Column(Boolean)
    notif_warning = Column(Boolean)
    description = Column(Text(1024))
    get_notif = Column(Boolean)
    def __init__(self, cage_id, port, description="", notifications=True, notification_food=False, notification_water=False, notification_warning=False):
        self.cage_id = cage_id
        self.port = port
        self.notif_food = notification_food
        self.notif_water = notification_water
        self.notif_warning = notification_warning
        self.description = description
        self.get_notif = notifications




class Notifications(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key = True)
    cage_id = Column(String(3))
    notif_datetime = Column(DateTime, default=strftime("%Y-%m-%d %H:%M:%S", localtime()), nullable=False)
    msg = Column(String(140))
    notif_type = Column("type", String(65))

    def __init__(self, cage_id, message, notif_type, notif_datetime):
        self.cage_id = cage_id
        self.msg = message
        self.notif_type = notif_type
        self.notif_datetime = notif_datetime


class Settings(Base):
    __tablename__ = "settings"
    setting_id = Column(Integer, primary_key = True)
    setting = Column(String(100))
    value = Column(String(65))

    def __init__(self, setting, value):
     self.setting = setting
     self.value = value


connected = False
while not connected:
    try:
        Base.metadata.create_all(engine)
        connected = True
    except Exception as error:
        connected = False
        print(error)
        sleep(1)