import random
import webbrowser
from platform import platform
from threading import Thread
from kivy.app import App
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from scripts.client import ClientConnection
from scripts.startup import ConfigManager
from scripts.android_permissions import *
from scripts.backup import *
from kivy.core.audio import SoundLoader
import ffpyplayer

if platform != 'android':
    import tkinter

    root = tkinter.Tk()

    scaling = 1  # 1.0
    display_x = root.winfo_screenwidth()
    display_y = root.winfo_screenheight()
    _x, _y = (display_y / 2.5)* scaling, (display_x / 2.5)* scaling
    #_x, _y = 540*scaling, 1200*scaling
    Window.size = _x, _y
    Window.left = (display_x / 2) - (_x / 2)
    Window.top = display_y / 8
    print(f'{_x} {_y}')
else:
    from kvdroid.tools.metrics import Metrics

    screen = Metrics()
    _x = int(screen.resolution()[5:])
    _y = int(screen.resolution()[:4])

cfg = ConfigManager()
if cfg.active():
    in_game = True
else:
    in_game = False

cc = ClientConnection()


class Loader(Screen):
    xx = _x
    yy = _y

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.char_list = []
        self.target_screen = ''
        self._opacity = 0
        self.velocity = 0
        self.loading_frame = 0
        self.loading_max = 10
        self.sound_intro = None
        self.click = None
        self.pop_click = None
        self.error = None
        self.key_press = None
        self.logging = None
        self._t = Thread(target=self.run_scheduler)
        self._t.start()

    def run_scheduler(self):
        try:
            # default timeout 0
            Clock.schedule_once(self.progress_check, 0)
        finally:
            # default timeout 0.08
            Clock.schedule_interval(self.progress_check, 0.08)

    def progress_check(self, dt):
        # placing bigger files like 1.5-2MB ath the first 0-2 frames of loading will glitch/freeze full-screen
        # FOR THE MOST PART JUST AVOID PUTTING ANYTHING INSIDE FIRST FRAME !!!
        if self.loading_frame <= self.loading_max:
            if self.loading_frame == 2:

                if platform == 'android':
                    from kvdroid.tools import immersive_mode
                    _t = Thread(target=immersive_mode)
                    _t.start()
                self.logging = SoundLoader.load('sfx/logging.ogg')
                self.sound_intro = SoundLoader.load('sfx/intro.ogg')

                self.click = SoundLoader.load('sfx/click.ogg')
                self.pop_click = SoundLoader.load('sfx/pop_click.ogg')
                self.error = SoundLoader.load('sfx/error.ogg')

            elif self.loading_frame == 8:
                self.manager.get_screen("creation").ids.kitty.source = 'img/backup.png'
            elif self.loading_frame == 9:

                self.key_press = SoundLoader.load('sfx/key_press.ogg')


                self.manager.get_screen('main').ids.logo.source = 'img/lol.zip'
                char6 = Image(f'img/char/char6.png')
                self.manager.get_screen('setup').ids.skin.source = char6.filename
            elif self.loading_frame == 10:
                self.manager.get_screen("restore").ids.doggy.source = 'img/recover.png'

            self.manager.get_screen("loader").ids.dupa.source = f'img/loading/{self.loading_frame}.png'
            self.loading_frame += 1

        else:
            self.sound_intro.loop = True
            self.sound_intro.volume = 0.3
            self.sound_intro.play()
            if in_game:
                self.manager.transition = FadeTransition()
                self.manager.current = 'entering_game'
                self.manager.get_screen('entering_game').connect_me()
            else:
                self.manager.transition = FadeTransition()
                self.manager.current = 'main'
                self.manager.transition = SlideTransition()
            Clock.unschedule(self.progress_check)

    def start_warning_window_for_screen(self, target, fade_out):
        self.target_screen = target
        if self._opacity <= 0:
            if fade_out:
                self.manager.get_screen('loader').error.play()
                self._opacity = 1
                self.velocity = 0
                Clock.schedule_interval(self.fade_out_button, 0.05)
            else:
                self.manager.get_screen('loader').error.play()
                self._opacity = 1
                self.manager.get_screen(self.target_screen).ids.warn.opacity = self._opacity

    def fade_out_button(self, dt):
        self.manager.get_screen(self.target_screen).ids.warn.opacity = self._opacity
        if self._opacity > 0.0:
            self._opacity -= 0.001 * self.velocity
            if self.velocity < 600:
                self.velocity += 1
            return self._opacity
        else:
            Clock.unschedule(self.fade_out_button)


class MainWindow(Screen):
    xx = _x
    yy = _y

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def new_player_btn(self):
        _displaySize = Window.system_size
        self.manager.get_screen('loader').click.play()

    def returning_player_btn(self):
        self.manager.get_screen('loader').click.play()


class CreationWindow(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_confirmed = False
        self.worker_running = False

    def update_permission_status(self, dt):
        if check_permissions():
            s = search_backups()
            if s == 'exist':
                self._output = 'backup  already  exists  in  pictures  directory' + '\n' + 'try  restoring  your  ' \
                                                                                           'profile  from  it '
                self.manager.get_screen('loader').start_warning_window_for_screen('creation', False)
                self.button_confirmed = False
            elif s == 'empty':
                cfg.allow_backup = True
                self.manager.transition = FadeTransition()
                self.manager.current = 'entering_game'
                self.manager.get_screen('entering_game').connect_me()
            Clock.unschedule(self.update_permission_status)
            self.worker_running = False

    def checkbox_allow_btn(self, instance, value):
        if not value:
            self.manager.get_screen('creation').ids.allow_id.active = True
        self.manager.get_screen('loader').key_press.play()

    def checkbox_deny_btn(self, instance, value):
        if not value:
            self.manager.get_screen('creation').ids.deny_id.active = True
        self.manager.get_screen('loader').key_press.play()


    def create_account_btn(self):
        self.manager.get_screen('loader').click.play()
        if self.manager.get_screen('creation').ids.allow_id.active:
            if not self.button_confirmed:
                self.button_confirmed = True
                if not self.worker_running:
                    self.worker_running = True
                    Clock.schedule_interval(self.update_permission_status, 0.5)
                ask_for_permission()
        else:
            cfg.allow_backup = False
            self.manager.transition = FadeTransition()
            self.manager.current = 'entering_game'
            self.manager.get_screen('entering_game').connect_me()

    def back_btn(self):
        self.manager.get_screen('loader').click.play()


class RestoreWindow(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_confirmed = False
        self.worker_running = False

    def check_for_restore_backup_permission(self, dt):
        if check_permissions():
            result = restore_from_backup()
            if result == 'failed':
                self._output = 'no  backup  found  in  Pictures  directory' + '\n' + 'its  name  should  be  ' \
                                                                                     'ASYLLION_BACKUP.png '
                self.manager.get_screen('loader').start_warning_window_for_screen('restore', False)
                self.button_confirmed = False
            else:
                cfg.config.read('../settings.ini')
                cfg.config.set('Startup', 'Secret', restore_from_backup())
                with open('../settings.ini', 'w') as current_config:
                    cfg.config.write(current_config)
                cfg.allow_backup = False
                self.manager.transition = FadeTransition()
                self.manager.current = 'entering_game'
                self.manager.get_screen('entering_game').connect_me()
            Clock.unschedule(self.check_for_restore_backup_permission)
            self.worker_running = False

    def restore_btn(self):
        self.manager.get_screen('loader').click.play()
        if not self.button_confirmed:
            self.button_confirmed = True
            if not self.worker_running:
                self.worker_running = True
                Clock.schedule_interval(self.check_for_restore_backup_permission, 0.5)
            ask_for_permission()

    def back_btn(self):
        self.manager.get_screen('loader').click.play()


class UpdateScreen(Screen):
    xx = _x
    yy = _y

    def update_btn(self):
        self.manager.get_screen('loader').click.play()
        webbrowser.open('https://asyllion.com')


class EnteringGame(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def connect_me(self):
        Clock.schedule_interval(self.update_status, 0.08)
        _t = Thread(target=cc.server_connect)
        _t.start()

    def update_status(self, dt):
        if cc.update_available:
            self.manager.current = 'update'
            Clock.unschedule(self.update_status)

        else:
            if cc.user == 'setup' or cc.user == 'creating':
                self.manager.current = 'setup'
                if cfg.allow_backup:
                    backup_data(cfg.config.get('Startup', 'Secret'))
                Clock.unschedule(self.update_status)

            elif cc.user == 'entering':
                self.manager.current = 'ingame'
                self.manager.get_screen('loader').sound_intro.stop()
                self.manager.get_screen('loader').logging.play()
                Clock.unschedule(self.update_status)

            elif cc.current_status is not None:
                self.manager.current = 'entering_game'
                self._output = cc.current_status
                self.manager.get_screen('loader').start_warning_window_for_screen('entering_game', False)
                Clock.unschedule(self.update_status)


class SetupScreen(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.profession = None
        self.player_skin = 6
        self.awaiting_validation = False

    def get_response(self, dt):
        if self.awaiting_validation:
            response = cc.update_server_message()
            if response is not '':
                Clock.unschedule(self.get_response)
                self.awaiting_validation = False
                if response != 'passed':
                    self._output = response
                    self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                else:
                    self.manager.get_screen('loader').sound_intro.stop()
                    self.manager.get_screen('loader').logging.play()
                    self.manager.current = 'ingame'

    def profession_btn(self, _profession):
        self.manager.get_screen('loader').key_press.play()

        self.profession = _profession
        if _profession == 0:
            self.manager.get_screen('setup').ids.selected.pos_hint = {'x': 0}
            self.manager.get_screen('setup').ids.status.text = 'melee  combat  profession  with \n great  defence  and  attack  abilities'
        elif _profession == 1:
            self.manager.get_screen('setup').ids.status.text = 'crafting  type  profession  with \n great  stamina  and  range  attack  abilities'
            self.manager.get_screen('setup').ids.selected.pos_hint = {'center_x': .5}
        elif _profession == 2:
            self.manager.get_screen('setup').ids.status.text = 'magic  combat  profession  with \n great  looting  abilities  and  good  attack'
            self.manager.get_screen('setup').ids.selected.pos_hint = {'right': 1}

    def skin_btn(self):
        self.manager.get_screen('loader').click.play()

        if self.player_skin < 6:
            self.player_skin += 1
        else:
            self.player_skin = 1
        self.manager.get_screen("setup").ids.skin.source = f'img/char/char{self.player_skin}.png'


    def validate_btn(self, nick):
        self.manager.get_screen('loader').click.play()

        if self.profession is None:
            self._output = 'please  choose  one  of  professions'
            self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
            return

        if not self.awaiting_validation:
            if len(nick) >= 4:
                if len(nick) > 16:
                    self._output = 'only  16  characters  allowed'
                    self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                    return
                elif not str.isalpha(nick):
                    self._output = 'characters  can  only  be  alphabet  letters' + '\n' + 'without  spaces'
                    self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                    return
                else:
                    cc.sender.send_nickname(self.profession, self.player_skin, nick)
                    Clock.schedule_interval(self.get_response, 0.1)
                    self.awaiting_validation = True
            elif 0 <= len(nick) < 4:
                self._output = 'use  minimum  4  characters'
                self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                return


class IngameScreen(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class WindowManager(ScreenManager):
    pass


class MainApp(App):

    def build(self):
        return Builder.load_file('kv/loading_section.kv')



MainApp().run()
