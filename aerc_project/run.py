import os
import webbrowser
import asyncio
import time
from threading import Thread


# RUNSERVER
async def runserver():
    os.system("python manage.py runserver_plus --cert-file cert.pem --key-file key.pem")

# OPEN BROWSER
def openproject():
    time.sleep(5)
    webbrowser.open_new_tab("https://127.0.0.1:8000/")

# EXECUTE PROGRAM
async def main():
    task = asyncio.create_task(runserver())
    t = Thread(target = openproject)
    t.start()
    await task

asyncio.run(main())