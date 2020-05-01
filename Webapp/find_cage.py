# import methodes om data te ontvangen/versturen van/naar Arduino

# reknr., kooinr.?
# vorm boodschap om LED van de kooi te doen flikkeren gedurende 30s
# verstuur boodschap
# controleer bevestiging
# stuur opnieuw indien geen bevestiging binnen ... s -> MOGELIJK????

# PROBLEEM!!!! Er kan interferentie optreden als meerdere pytonprogramma's de I2C-connectie (tegelijk) uitlezen!!
# OPLOSSING: slechts 1 programma toestaan dat I2C uitleest -> moet kunnen beslissen op basis van boodschap wat verder
# moet gebeuren