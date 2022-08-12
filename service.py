from plyer import vibrator, notification
from time import sleep
from jnius import autoclass

PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)


while True:
    vibrator.vibrate(time=.1)
    sleep(2)




