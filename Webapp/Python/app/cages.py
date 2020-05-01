from sql import addMeasurementToDB, addNotification, setNotificationFlag, getNotificationFlag, updateSetting, \
    getSetting, getCages, getCageInfo
from arduino import Arduino
import serial

def updateCage(cageID, method="manual"):
    """
    Ask Cage with ID cageID for measuremnts, save the results in the database and add a notification if necessary.
    :param cageID:
    :param method: the way this function was executed: manual, auto
    :return: None
    """
    waterLimit = int(getSetting("water_limit"))  # get water limit from database
    print("Reading cage info of cage", cageID, "...")
    cageInfo = getCageInfo(cageID)
    try:
        print("Reading from arduino on port", cageInfo.port, "...")
        arduino = Arduino(cageID, port=cageInfo.port)
        cage, foodStatus, waterLevel = arduino.receiveMeasurements()
        # add measurements to database
        print("Adding results to DB...")
        addMeasurementToDB(cage, not foodStatus, waterLevel, method)
        if getNotificationFlag(cage, "warning"):
            message = "Cage " + cage + " is reconnected."
            addNotification(cage, message, "warning")
        if waterLevel < waterLimit:
            arduino.turnOnWaterLED()
            if not getNotificationFlag(cage, "water"):
                setNotificationFlag(cage, "water", True)
                message = "Cage " + cage + " is out of water."
                addNotification(cage, message, "water")
        else:
            setNotificationFlag(cage, "water", False)
        if foodStatus:
            arduino.turnOnFoodLED()
            if not getNotificationFlag(cage, "food"):
                setNotificationFlag(cage, "food", True)
                message = "Cage " + cage + " is out of food."
                addNotification(cage, message, "food")
        else:
            setNotificationFlag(cage, "food", False)
        setNotificationFlag(cageID, "warning", False)
    except serial.serialutil.SerialException:
        message = "Cage " + cageID + " does not respond. Please check the connection."
        print("Error:", message)
        if not getNotificationFlag(cageID, "warning"):
            addNotification(cageID, message, "warning")
            setNotificationFlag(cageID, "warning", True)
        return False
    except AttributeError:
        raise ValueError(cageID + " is not a valid cage id")


def updateCages(method="manual"):
    """
    Loop over all cages and update measurements in database.
    :return: None
    """
    cages = getCages()
    for i in range(len(cages)):
        cageID = cages[i].cage_id
        updateCage(cageID, method)