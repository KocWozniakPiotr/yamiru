import webbrowser
from platform import platform
from threading import Thread
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from scripts.client import ClientConnection
from scripts.startup import ConfigManager
from scripts.android_permissions import *
from scripts.backup import *
from kivy.core.audio import SoundLoader

if platform != 'android':
    import ffpyplayer
    import tkinter

    root = tkinter.Tk()

    scaling = 0.5  # 1.0
    display_x = root.winfo_screenwidth()
    display_y = root.winfo_screenheight()
    screen_x,screen_y = (display_y / 2.5)* scaling, (display_x / 2.5)* scaling
    #screen_x, screen_y = 1080*scaling, 2340*scaling
    Window.size =screen_x,screen_y
    Window.left = (display_x / 2) - (screen_x / 2)
    Window.top = display_y / 8
    print(f'{screen_x} {screen_y}')
else:
    from kvdroid.tools.metrics import Metrics

    screen = Metrics()
    screen_x = int(screen.resolution()[5:])
    screen_y = int(screen.resolution()[:4])


cfg = ConfigManager()
if cfg.active():
    in_game = True
else:
    in_game = False

cc = ClientConnection()


class Loader(Screen):
    xx =screen_x
    yy =screen_y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_scene = ''
        self.clock_stopped = False
        self.intro_to_game = False
        self.loader_already_running = False
        self.char_list = []
        self.target_screen = ''
        self._opacity = 0
        self.velocity = 0
        self.loading_frame = 0
        self.loading_max = 10
        self.sound_intro = None
        self.sound_ingame = None
        self.sound_click = None
        self.sound_error = SoundLoader.load('sfx/error.ogg')
        self.sound_key_press = None
        self.sound_logging = None
        self._t = Thread(target=self.run_scheduler)
        self.initialize_loader()

    def reset_loader_values(self):
        self.loading_frame = 0

    def initialize_loader(self):
        if not in_game:
            self.current_scene = 'intro_scene'
            self._t.start()
        else:
            self.current_scene = 'game_scene'
            if not self.intro_to_game:
                connect_tread = Thread(target=cc.server_connect)
                connect_tread.start()
            else:
                if self.loader_already_running:
                    self.reset_loader_values()
            _t = Thread(target=self.run_scheduler)
            _t.start()


    def run_scheduler(self):
        try:
            # default timeout 0
            Clock.schedule_once(self.progress_check, 0)
        finally:
            # default timeout 0.08
            Clock.schedule_interval(self.progress_check, 0.08)

    def progress_check(self, dt):
        # placing bigger files like 1.5-2MB at the first 0-2 frames of loading will glitch/freeze full-screen
        # FOR THE MOST PART AVOID PUTTING ANYTHING INSIDE FIRST FRAME !!!
        if self.loading_frame <= self.loading_max:
            if self.loading_frame == 2:
                self.check_fullscreen()

            elif self.loading_frame == 3:
                self.load_interface_textures()

            elif self.loading_frame == 4:
                self.load_game_textures()

            elif self.loading_frame == 5:
                self.load_game_animations()

            elif self.loading_frame == 6:
                self.load_interface_animations()

            elif self.loading_frame == 7:
                self.load_interface_sounds()

            elif self.loading_frame == 9:
                self.load_game_sounds()


            elif self.loading_frame == 10:
                if in_game:
                    # self.manager.add_widget(IngameScreen(name='ingame'))
                    self.manager.get_screen('ingame').load_content()

            self.check_server_context()

            self.update_progressbar()
        else:
            if in_game:
                self.manager.transition = FadeTransition()
                self.sound_ingame.loop = True
                self.sound_ingame.volume = 0.3
                self.sound_ingame.play()
                self.manager.current = 'ingame'
            elif not in_game:
                self.sound_intro.loop = True
                self.sound_intro.volume = 0.3
                self.sound_intro.play()
                if cfg.tutorial == 'empty':
                    self.manager.current = 'main'
                    self.manager.transition = SlideTransition()
                elif cfg.tutorial == 'started':
                    self.manager.get_screen('entering_game').connect_me()
                    self.manager.current = 'entering_game'
                    self.manager.transition = FadeTransition()

            Clock.unschedule(self.progress_check)

    def check_fullscreen(self):
        if not self.loader_already_running:
            self.loader_already_running = True
            if platform == 'android':
                from kvdroid.tools import immersive_mode
                _t = Thread(target=immersive_mode)
                _t.start()

    def update_progressbar(self):
        self.manager.get_screen("loader").ids.progress_bar.source = f'img/loading/{self.loading_frame}.png'
        self.loading_frame += 1

    def check_server_context(self):
        if not self.intro_to_game:
            if not self.clock_stopped:
                if cc.update_available:
                    self.manager.current = 'update'
                    self.clock_stopped = True
                else:
                    if cc.current_status is not None:
                        self._output = cc.current_status
                        self.start_warning_window_for_screen('loader', False)
                        self.clock_stopped = True
            else:
                self.loading_frame = 0

    def load_interface_textures(self):
        if self.current_scene == 'intro_scene':
            self.manager.get_screen("creation").ids.kitty.source = 'img/backup.png'
            self.manager.get_screen("restore").ids.doggy.source = 'img/recover.png'


    def load_game_textures(self):
        if self.current_scene == 'intro_scene':
            from kivy.core.image import Image
            char6 = Image(f'img/char/char6.png')
            self.manager.get_screen('setup').ids.skin.source = char6.filename
        if self.current_scene == 'game_scene':
            pass


    def load_interface_animations(self):
        if self.current_scene == 'intro_scene':
            self.manager.get_screen('main').ids.logo.source = 'img/lol.zip'


    def load_game_animations(self):
        pass


    def load_interface_sounds(self):
        if self.current_scene == 'intro_scene':
            self.sound_key_press = SoundLoader.load('sfx/key_press.ogg')
            self.sound_click = SoundLoader.load('sfx/click.ogg')
            self.sound_intro = SoundLoader.load('sfx/intro.ogg')
        if self.current_scene != 'intro_scene':
            pass  # self.manager.get_screen('loader').sound_intro.unload()


    def load_game_sounds(self):
        if self.current_scene == 'intro_scene':
            self.sound_logging = SoundLoader.load('sfx/logging.ogg')
        if self.current_scene == 'game_scene':
            self.sound_ingame = SoundLoader.load('sfx/ingame.ogg')


    def start_warning_window_for_screen(self, target, fade_out):
        self.target_screen = target
        if self._opacity <= 0:
            if fade_out:
                self.manager.get_screen('loader').sound_error.play()
                self._opacity = 1
                self.velocity = 0
                Clock.schedule_interval(self.fade_out_button, 0.05)
            else:
                self.manager.get_screen('loader').sound_error.play()
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
    xx =screen_x
    yy =screen_y

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def new_player_btn(self):
        _displaySize = Window.system_size
        self.manager.get_screen('loader').sound_click.play()

    def returning_player_btn(self):
        self.manager.get_screen('loader').sound_click.play()


class CreationWindow(Screen):
    xx =screen_x
    yy =screen_y
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
        self.manager.get_screen('loader').sound_key_press.play()

    def checkbox_deny_btn(self, instance, value):
        if not value:
            self.manager.get_screen('creation').ids.deny_id.active = True
        self.manager.get_screen('loader').sound_key_press.play()


    def create_account_btn(self):
        self.manager.get_screen('loader').sound_click.play()
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
        self.manager.get_screen('loader').sound_click.play()


class RestoreWindow(Screen):
    xx =screen_x
    yy =screen_y
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
        self.manager.get_screen('loader').sound_click.play()
        if not self.button_confirmed:
            self.button_confirmed = True
            if not self.worker_running:
                self.worker_running = True
                Clock.schedule_interval(self.check_for_restore_backup_permission, 0.5)
            ask_for_permission()

    def back_btn(self):
        self.manager.get_screen('loader').sound_click.play()


class UpdateScreen(Screen):
    xx =screen_x
    yy =screen_y

    def update_btn(self):
        webbrowser.open('https://asyllion.com')


class EnteringGame(Screen):
    xx =screen_x
    yy =screen_y
    _output = StringProperty()

    def connect_me(self):
        Clock.schedule_interval(self.update_status, 0.08)
        _t = Thread(target=cc.server_connect)
        _t.start()

    def update_status(self, dt):
        global in_game
        if cc.update_available:
            self.manager.current = 'update'
            Clock.unschedule(self.update_status)

        else:
            if cc.user == 'setup' or cc.user == 'creating':
                cfg.config.read('../settings.ini')
                cfg.config.set('Startup', 'Tutorial', 'started')
                cfg.tutorial = 'started'
                with open('../settings.ini', 'w') as current_config:
                    cfg.config.write(current_config)
                self.manager.current = 'setup'
                if cfg.allow_backup:
                    backup_data(cfg.config.get('Startup', 'Secret'))
                Clock.unschedule(self.update_status)

            elif cc.user == 'entering':
                in_game = True
                self.manager.get_screen('loader').intro_to_game = True
                self.manager.current = 'loader'
                self.manager.get_screen('loader').sound_intro.stop()
                self.manager.get_screen('loader').sound_intro.unload()
                self.manager.get_screen('loader').initialize_loader()
                Clock.unschedule(self.update_status)

            elif cc.current_status is not None:
                self._output = cc.current_status
                self.manager.get_screen('loader').start_warning_window_for_screen('entering_game', False)
                Clock.unschedule(self.update_status)


class SetupScreen(Screen):
    xx =screen_x
    yy =screen_y
    _output = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.profession = None
        self.player_skin = 6
        self.awaiting_validation = False


    def get_response(self, dt):
        global in_game
        if self.awaiting_validation:
            response = cc.update_server_message()
            if response is not '':
                Clock.unschedule(self.get_response)
                self.awaiting_validation = False
                if response != 'passed':
                    self._output = response
                    self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                else:
                    cfg.config.read('../settings.ini')
                    cfg.config.set('Startup', 'Tutorial', 'finished')
                    cfg.tutorial = 'finished'
                    with open('../settings.ini', 'w') as current_config:
                        cfg.config.write(current_config)
                    in_game = True
                    self.manager.get_screen('loader').intro_to_game = True
                    self.manager.current = 'loader'
                    self.manager.get_screen('loader').sound_intro.stop()
                    self.manager.get_screen('loader').sound_intro.unload()
                    self.manager.get_screen('loader').initialize_loader()


    def profession_btn(self, _profession):
        self.manager.get_screen('loader').sound_key_press.play()

        self.profession = _profession
        if _profession == 0:
            self.manager.get_screen('setup').ids.selected.pos_hint = {'x': 0}
            self.manager.get_screen('setup').ids.status.text = 'melee combat profession with \n great defence and attack abilities'
        elif _profession == 1:
            self.manager.get_screen('setup').ids.status.text = 'crafting type profession with \n great stamina and range attack abilities'
            self.manager.get_screen('setup').ids.selected.pos_hint = {'center_x': .5}
        elif _profession == 2:
            self.manager.get_screen('setup').ids.status.text = 'magic combat profession with \n great looting abilities and good attack'
            self.manager.get_screen('setup').ids.selected.pos_hint = {'right': 1}

    def skin_btn(self):
        self.manager.get_screen('loader').sound_click.play()

        if self.player_skin < 6:
            self.player_skin += 1
        else:
            self.player_skin = 1
        self.manager.get_screen("setup").ids.skin.source = f'img/char/char{self.player_skin}.png'


    def validate_btn(self, nick):
        self.manager.get_screen('loader').sound_click.play()

        if self.profession is None:
            self._output = 'please choose one of professions'
            self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
            return

        if not self.awaiting_validation:
            if len(nick) >= 4:
                if len(nick) > 16:
                    self._output = 'only 16 characters allowed'
                    self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                    return
                elif not str.isalpha(nick):
                    self._output = 'characters can only be alphabet letters' + '\n' + 'without spaces'
                    self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                    return
                else:
                    cc.sender.send_nickname(self.profession, self.player_skin, nick)
                    Clock.schedule_interval(self.get_response, 0.1)
                    self.awaiting_validation = True
            elif 0 <= len(nick) < 4:
                self._output = 'use minimum 4 characters'
                self.manager.get_screen('loader').start_warning_window_for_screen('setup', True)
                return


class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        self.transition = FadeTransition()

