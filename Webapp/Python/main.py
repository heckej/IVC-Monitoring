from arduino import Arduino
# import methodes en instellingen om verbinding te maken met SQL-database

def main():
    # Loop om het half uur over alle Arduino's (max. 126?)
        # Vraag data op van Arduino (of wacht totdat er iets van om het even welke Arduino wordt ontvangen)
        # Decodeer de data
        # Voeg data toe aan database (incl. datum, tijd, kooinr., reknr., ...)
        # Voeg melding toe (die wordt weergegeven in de webapplicatie).
    # end loop

    # ALTERNATIEF:
    # Alle Arduino's sturen om het half uur data (niet per se op hetzelfde moment).
    # Controleer voortdurend of er iets wordt ontvangen.
    pass

main()