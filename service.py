from plyer import vibrator, notification
from time import sleep
from random import randint as r
from jnius import autoclass

# Restarts the service as soon as the script ends.
PythonService = autoclass('org.kivy.android.PythonService').mService
PythonService.mService.setAutoRestartService(True)

msg = ['are', 'running', 'you', 'please drink', 'maybe', 'swallow it', 'your water', 'forgot', '?', '!']
msg_length = r(3, 6)
final_msg = ''
i = 0
while i < msg_length:
    i += 1
    final_msg += ' ' + msg.pop(r(0, len(msg)))


# Notify user if msg_available is true, notify user
notification.notify(title='New Message', message=final_msg)
# vibrator.vibrate(time=.1)


# Adjust sleep depending on duration of your service script
sleep(2)

# PythonService.NotificationManager.cancel(1)
