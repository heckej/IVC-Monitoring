import serial, time

class Arduino:
    def __init__(self, id, port="/dev/ttyACM0", baudrate=9600, timeout=0):
        self._id = id
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._ser = serial.Serial(port, baudrate, timeout=timeout)  # port should be something like /dev/... for RPi
        time.sleep(2)
        if self._ser.inWaiting() > 0:
            msg = self._ser.readline().decode().strip("\r\n")
            if msg == self._id + " ready":
                # Arduino is ready to listen
                print("Arduino is ready")
            else:
                print(msg)
        else:
            print("Unknown whether Arduino is ready or not")

    def receiveMeasurements(self):
        """
        Check for messages and decode
        Messages are encoded using the following pattern: cage:foodStatus:waterLevelWith4Decimals\r\n
        e.g. cage A1 needs food and has a waterlevel of 300: A1:0:0300\r\n
        The cage number is between A1 and H10.
        :return: str cage, bool foodStatus, int waterLevel; None in case there's nothing to read
        """
        self.sendCommand("measure","")
        time.sleep(1)
        if self._ser.inWaiting() > 0:
            msg = self._ser.readline()  # get message from Arduino (in bytes)
            while self._ser.inWaiting() > 0:
                msg += self._ser.readline() # get message from Arduino (in bytes)
            print("msg py:", msg)
            msg = msg.decode() # decode the message from bytes to string
            print("msg py dec:", msg)
            msg = msg.strip("\r\n") # remove EOL symbols
            print("msg py str:", msg)
            #firstLineBreak = msg.find("\n")
            #msg = msg[firstLineBreak+1:]
            #lastLineBreak = msg.find("\r\n")
            #msg = msg[:lastLineBreak]
            parts = msg.split(":")
            print(parts)
            cage = parts[0]
            foodStatus = bool(parts[1])
            waterLevel = int(parts[2])
            return cage, foodStatus, waterLevel
        else:
            return None

    def sendCommand(self, cmd, val=""):
        """
        Send a command to the Arduino
        :param cmd: str the command description
        :param val: str if necessary extra value
        :return: none
        """
        msg = "cmd:" + str(cmd) + "&" + "val:" + str(val) + ";"
        msg = msg.encode()
        print(msg)
        self._ser.write(msg)
        self._ser.flushOutput()

    def turnOnFoodLED(self):
        """
        Send command to Arduino to turn on food LED
        :return: none
        """
        self.sendCommand("turnOn", "food")

    def turnOnWaterLED(self):
        """
        Send command to Arduino to turn on water LED
        :return: none
        """
        self.sendCommand("turnOn", "water")

    def blinkLED(self, delay):
        """
        Send command to Arduino to let LED blink
        COMMAND NOT IMPLEMENTED ON ARDUINO
        :param delay: int: time to let LED blink
        :return: none
        """
        self.sendCommand("blink", delay)

    def getCage(self):
        """
        Get cage id
        :return:
        """
        return self._id