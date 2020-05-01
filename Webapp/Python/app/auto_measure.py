from cages import updateCage, updateCages
from sql import getSetting
from time import sleep


def main():
    # Loop om het half uur over alle Arduino's (max. 126?)
    # Vraag data op van Arduino (of wacht totdat er iets van om het even welke Arduino wordt ontvangen)
    # Decodeer de data
    # Voeg data toe aan database (incl. datum, tijd, kooinr., reknr., ...)
    # Voeg melding toe (die wordt weergegeven in de webapplicatie).
    # end loop
    try:
        while True:
            measureInterval = int(getSetting("measure_interval"))  # get interval to measure from database
            updateCages("auto")
            print("Sleeping for", measureInterval, "seconds...")
            sleep(measureInterval)

    except KeyboardInterrupt:
        print("Program exiting...")
        pass


main()