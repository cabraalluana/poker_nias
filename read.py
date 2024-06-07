from main import main

main()

# rodar competição aumaticamente

import schedule
import time as tm

schedule.every().day.at("15:02").do(main)

while True:
    schedule.run_pending()
    tm.sleep(1)