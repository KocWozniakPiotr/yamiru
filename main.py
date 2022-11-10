from threading import Thread
import kivy
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.utils import platform
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition, NoTransition
import startup

kivy.require("2.1.0")
if platform != 'android':
    Window.size = 360, 740
else:
    Window.maximize()
displaySize = Window.system_size
displayW = displaySize[0]
displayH = displaySize[1]
intro_screen = False


# INTRO LAYOUT
########################################


class Loader(Screen):
    xx = displayW
    yy = displayH

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_frame = 0
        self.loading_max = 5
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
            print('wtf')
        finally:
            # default timeout 0.08
            Clock.schedule_interval(self.progress_check, 0.08)
            pass  # Clock.schedule_interval(self.progress_check, 0.08)

    def progress_check(self, dt):
        # placing bigger files like 1.5-2MB ath the first 1-2 frames of loading will glitch with fullscreen
        # FOR THE MOST PART JUST AVOID PUTTING ANYTHING INSIDE FIRST FRAME !!!
        if self.loading_frame <= self.loading_max:
            if self.loading_frame == 2:
                self.sound_intro = SoundLoader.load('sfx/intro.ogg')
                self.click = SoundLoader.load('sfx/click.ogg')
                self.pop_click = SoundLoader.load('sfx/pop_click.ogg')
            elif self.loading_frame == 3:
                self.manager.get_screen("creation").ids.kitty.source = 'img/code.zip'
            elif self.loading_frame == 4:
                self.manager.get_screen("setup").ids.logo.source = 'img/lol.zip'
            elif self.loading_frame == 5:
                self.manager.get_screen("restore").ids.doggy.source = 'img/code2.zip'

            self.manager.get_screen("loader").ids.dupa.source = f'img/loading/{self.loading_frame}.png'
            self.loading_frame += 1
        else:
            if platform == 'android':
                self.sound_intro.loop = True
                self.sound_intro.volume = 0.3
                self.sound_intro.play()
            self.manager.transition = FadeTransition()
            self.manager.current = 'setup'
            self.manager.transition = SlideTransition()
            Clock.unschedule(self.progress_check)


class SetupWindow(Screen):
    xx = displayW
    yy = displayH
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def new_player_btn(self):
        # client.t_server_connect.start()
        if platform == 'android':
            self.manager.get_screen('loader').click.play()

    def returning_player_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()


class CreationWindow(Screen):
    xx = displayW
    yy = displayH
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

    def create_backup_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()
            if self.manager.get_screen('creation').ids.allow_id.active:
                self._output = 'starting backup...'
            else:
                self._output = 'skipping backup, creating account...'

    def back_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()


class RestoreWindow(Screen):
    xx = displayW
    yy = displayH

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def restore_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()
            # startup.restore_backup()

    def back_btn(self):
        if platform == 'android':
            self.manager.get_screen('loader').click.play()


# GAME LAYOUT
########################################


class GameLoader(Screen):
    xx = displayW
    yy = displayH

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_frame = 0
        self.loading_max = 5
        self.click = None
        self._t = Thread(target=self.run_scheduler)
        self._t.start()

    def run_scheduler(self):
        try:
            # default timeout 0
            Clock.schedule_once(self.progress_check, 0)
        except:
            print('wtf')
        finally:
            # default timeout 0.08
            Clock.schedule_interval(self.progress_check, 0.08)
            pass  # Clock.schedule_interval(self.progress_check, 0.08)

    def progress_check(self, dt):
        # placing bigger files like 1.5-2MB ath the first 1-2 frames of loading will glitch with fullscreen
        # FOR THE MOST PART JUST AVOID PUTTING ANYTHING INSIDE FIRST FRAME !!!
        if self.loading_frame <= self.loading_max:
            if self.loading_frame == 2:
                self.click = SoundLoader.load('sfx/click.ogg')
            elif self.loading_frame == 3:
                pass
            elif self.loading_frame == 4:
                pass
            elif self.loading_frame == 5:
                pass

            self.manager.get_screen("game_loader").ids.dupa.source = f'img/loading/{self.loading_frame}.png'
            self.loading_frame += 1
        else:
            self.manager.transition = FadeTransition()
            self.manager.current = 'update'
            self.manager.transition = SlideTransition()
            Clock.unschedule(self.progress_check)


class Update(Screen):
    xx = displayW
    yy = displayH


class Game(Screen):
    xx = displayW
    yy = displayH


########################################


class WindowManager(ScreenManager):
    pass


if startup.config_active():
    Builder.load_file('game_section.kv')
    intro_screen = False
else:
    Builder.load_file('loading_section.kv')
    intro_screen = True

if platform != 'android':
    # Builder.load_file('game_section.kv')
    # intro_screen = False
    pass


class MainApp(App):

    def build(self):
        self.sm = ScreenManager(transition=NoTransition())
        if intro_screen:
            fake_screen = Screen(name='fake_screen')
            self.sm.add_widget(fake_screen)
            loader = Loader()
            self.sm.add_widget(loader)
            setup = SetupWindow()
            self.sm.add_widget(setup)
            creation = CreationWindow()
            self.sm.add_widget(creation)
            restore = RestoreWindow()
            self.sm.add_widget(restore)
            Clock.schedule_once(self.switch_to_loader)
        else:
            fake_screen = Screen(name='fake_screen')
            fake_screen.canvas.clear()
            self.sm.add_widget(fake_screen)
            game_loader = GameLoader()
            self.sm.add_widget(game_loader)
            update = Update()
            self.sm.add_widget(update)
            game = Game()
            self.sm.add_widget(game)
            Clock.schedule_once(self.switch_to_loader)
        return self.sm

    def switch_to_loader(self, *args):
        if intro_screen:
            self.sm.current = 'loader'
        else:
            self.sm.current = 'game_loader'


MainApp().run()
