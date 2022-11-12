import webbrowser
from threading import Thread
import kivy
from kivy._event import partial
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition, NoTransition
from scripts import client
from startup import ConfigManager
from scripts.client import ClientConnection

kivy.require("2.1.0")
if platform != 'android':
    display_x, display_y = 1920, 1080
    _x, _y = 400, 800
    Window.size = _x, _y
    Window.left = (display_x / 2) - (_x / 2)
    Window.top = display_y / 8
else:
    from kvdroid.tools.metrics import Metrics

    screen = Metrics()
    _x = int(screen.resolution()[5:])
    _y = int(screen.resolution()[:4])

in_game = False


# INTRO LAYOUT
########################################


class Loader(Screen):
    xx = _x
    yy = _y

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_frame = 0
        self.loading_max = 10
        self.sound_intro = None
        self.click = None
        self.pop_click = None
        self._t = Thread(target=self.run_scheduler)
        self._t.start()

    def run_scheduler(self):
        try:
            # default timeout 0
            Clock.schedule_once(self.progress_check, 0)
        except:
            pass
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
                # change_statusbar_color("#0C0420", "white")
                # navbar_color("#0C0420")
                self.sound_intro = SoundLoader.load('sfx/intro.ogg')
                self.click = SoundLoader.load('sfx/click.ogg')
                self.pop_click = SoundLoader.load('sfx/pop_click.ogg')
            elif self.loading_frame == 8:
                self.manager.get_screen("creation").ids.kitty.source = 'img/code.zip'
            elif self.loading_frame == 9:
                self.manager.get_screen("setup").ids.logo.source = 'img/lol.zip'
            elif self.loading_frame == 10:
                self.manager.get_screen("restore").ids.doggy.source = 'img/code2.zip'

            self.manager.get_screen("loader").ids.dupa.source = f'img/loading/{self.loading_frame}.png'
            self.loading_frame += 1
        else:
            if platform == 'android':
                self.sound_intro.loop = True
                self.sound_intro.volume = 0.3
                self.sound_intro.play()
            if in_game:
                self.manager.transition = FadeTransition()
                self.manager.current = 'game'
                self.manager.get_screen('game').connect_me()
            else:
                self.manager.transition = FadeTransition()
                self.manager.current = 'setup'
                self.manager.transition = SlideTransition()
            Clock.unschedule(self.progress_check)


class SetupWindow(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def new_player_btn(self):
        _displaySize = Window.system_size
        # client.t_server_connect.start()
        if platform == 'android':
            self.manager.get_screen('loader').click.play()

    def returning_player_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()


class CreationWindow(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def checkbox_allow_btn(self, instance, value):
        if not value:
            self.manager.get_screen('creation').ids.allow_id.active = True
        if platform == 'android': self.manager.get_screen('loader').pop_click.play()

    def checkbox_deny_btn(self, instance, value):
        if not value:
            self.manager.get_screen('creation').ids.deny_id.active = True
        if platform == 'android': self.manager.get_screen('loader').pop_click.play()

    def create_account_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()
        if self.manager.get_screen('creation').ids.allow_id.active:
            self.manager.transition = FadeTransition()
            self.manager.current = 'game'
            self.manager.get_screen('game').connect_me()
        else:
            self._output = 'not  available'

    def back_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()


class RestoreWindow(Screen):
    xx = _x
    yy = _y

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def restore_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()
            # startup.restore_backup()

    def back_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()


class Game(Screen):
    xx = _x
    yy = _y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cc = ClientConnection()
        self.button_exist = False

    def connect_me(self):
        Clock.schedule_interval(self.update_status, 0.08)
        _t = Thread(target=self.cc.server_connect)
        _t.start()

    def update_status(self, dt):
        self._output = self.cc.server_status
        if self.cc.update_available and not self.button_exist:
            update_btn = Button()
            update_btn.text = 'update available'
            update_btn.size = self.xx, self.yy / 12
            update_btn.on_press = lambda: webbrowser.open('https://asyllion.com')
            self.manager.get_screen('game').add_widget(update_btn)
            self.button_exist = True


class WindowManager(ScreenManager):
    pass


cfg = ConfigManager()
if cfg.active():
    in_game = True

Builder.load_file('loading_section.kv')


class MainApp(App):

    def build(self):
        sm = ScreenManager(transition=NoTransition())
        loader = Loader()
        sm.add_widget(loader)
        setup = SetupWindow()
        sm.add_widget(setup)
        creation = CreationWindow()
        sm.add_widget(creation)
        restore = RestoreWindow()
        sm.add_widget(restore)
        game = Game()
        sm.add_widget(game)
        return sm


MainApp().run()
