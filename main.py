from kivy.app import App
from kivy._event import partial
import threading
import webbrowser
from platform import platform
from threading import Thread
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from scripts.client import ClientConnection
from scripts.startup import ConfigManager
from scripts.android_permissions import *
from scripts.backup import *
from display import *
from game import *

cfg = ConfigManager()
if cfg.active():
    in_game = True
else:
    in_game = False

cc = ClientConnection()


class LoaderScreen(Screen):
    box_layout = DefaultBoxLayout(screen_x, screen_y)
    warn = WarningLabel(screen_x, screen_y)
    progress_bar = DefaultImage( screen_x, screen_y, source = 'img/loading/0.png')
    intro_mask = VinaigretteMask(screen_x, screen_y, 0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.box_layout.add_widget(self.warn)
        self.box_layout.add_widget(self.progress_bar)
        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)

        self.current_screen = ''
        self.next_screen = ''
        self.current_scene = ''
        self.clock_stopped = False
        self.intro_to_game = False
        self.loader_already_running = False
        self.char_list = []
        self.loading_frame = 0
        self.loading_max = 10
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
                self.load_screens()

            elif self.loading_frame == 4:
                self.load_interface_textures()
                self.load_game_textures()

            elif self.loading_frame == 5:
                self.load_game_animations()

            elif self.loading_frame == 6:
                self.load_interface_animations()

            elif self.loading_frame == 7:
                sound.load_interface_sounds(self.current_scene)
                #self.load_interface_sounds()

            elif self.loading_frame == 9:
                sound.load_game_sounds(self.current_scene)

            elif self.loading_frame == 10:
                pass


            self.check_server_context()

            self.update_progressbar()
        else:
            if in_game:
                sound.sound_ingame.loop = True
                sound.sound_ingame.volume = 0.3
                sound.sound_ingame.play()
                self.transition_move('loader', 'ingame')
            elif not in_game:
                sound.sound_intro.loop = True
                sound.sound_intro.volume = 0.3
                sound.sound_intro.play()
                if cfg.tutorial == 'empty':
                    self.transition_move('loader', 'main')
                elif cfg.tutorial == 'started':
                    self.manager.get_screen('entering_screen').connect_me()
                    self.transition_move('loader', 'entering_screen')

            Clock.unschedule(self.progress_check)


    def check_fullscreen(self):
        if not self.loader_already_running:
            self.loader_already_running = True
            if platform == 'android':
                from kvdroid.tools import immersive_mode
                _t = Thread(target=immersive_mode)
                _t.start()

    def update_progressbar(self):
        self.manager.get_screen("loader").progress_bar.source = f'img/loading/{self.loading_frame}.png'
        self.loading_frame += 1

    def check_server_context(self):
        if not self.intro_to_game:
            if not self.clock_stopped:
                if cc.update_available:
                    self.transition_move('loader', 'update')
                    self.clock_stopped = True
                else:
                    if cc.current_status is not None:
                        self.warn.popup(cc.current_status, False)
                        self.clock_stopped = True
            else:
                self.loading_frame = 0

    def load_screens(self):
        if self.current_scene == 'intro_scene':
            self.manager.add_widget(MainScreen(name='main'))
            self.manager.add_widget(CreationScreen(name='creation'))
            self.manager.add_widget(RestoreScreen(name='restore'))
            self.manager.add_widget(UpdateScreen(name='update'))
            self.manager.add_widget(EnteringScreen(name='entering_screen'))
            self.manager.add_widget(SetupScreen(name='setup'))
        elif self.current_scene == 'game_scene':
            update_res_ingame(screen_x, screen_y)
            self.manager.add_widget(IngameScreen(name='ingame'))

    def load_interface_textures(self):
        if self.current_scene == 'intro_scene':
            self.manager.get_screen("creation").backup_image.source = 'img/ui/backup.png'
            self.manager.get_screen("restore").restore_image.source = 'img/ui/recover.png'

    def load_game_textures(self):
        if self.current_scene == 'intro_scene':
            from kivy.core.image import Image
            char6 = Image(f'img/char/char6.png')
            self.manager.get_screen('setup').skin.source = char6.filename
        if self.current_scene == 'game_scene':
            pass

    def load_interface_animations(self):
        if self.current_scene == 'intro_scene':
            self.manager.get_screen('main').logo.source = 'img/animation.zip'

    def load_game_animations(self):
        pass

    def transition_move(self, current_target, next_target):
        self.current_screen = current_target
        self.next_screen = next_target
        self.manager.get_screen(self.current_screen).intro_mask.start_screen_fading()
        Clock.schedule_interval(self.transition_fade, 0.05)

    def transition_fade(self, dt):
        if self.manager.get_screen(self.current_screen).intro_mask.opacity == 1:
            self.manager.current = self.next_screen
            self.manager.get_screen(self.next_screen).intro_mask.start_screen_fading()
            Clock.unschedule(self.transition_fade)


class MainScreen(Screen):
    box_layout = DefaultBoxLayout(screen_x, screen_y)
    empty_label_top = Label(size_hint=(None, None), width=screen_x, height=screen_y / 6)
    title_label = DefaultLabel(info_title, screen_x, screen_y, 4)
    logo = DefaultImage(screen_x, screen_x/2.5, anim_loop = 0, keep_data = True, anim_delay = 0.05)
    new_player = SpecialButton(screen_x, screen_y, 'new player', 4)
    returning_player = SpecialButton(screen_x, screen_y, 'returning player', 4)
    intro_mask = VinaigretteMask(screen_x, screen_y, 1)

    def __init__(self, **kw):
        super().__init__(**kw)

        self.box_layout.add_widget(self.empty_label_top)
        self.box_layout.add_widget(self.title_label)
        self.box_layout.add_widget(Label())

        self.box_layout.add_widget(self.logo)
        self.box_layout.add_widget(Label(size_hint=(None, None), width=screen_x, height=screen_y / 5))
        self.new_player.button.bind(on_release=self.new_player_btn)
        self.box_layout.add_widget(self.new_player)

        self.returning_player.button.bind(on_release=self.returning_player_btn)
        self.box_layout.add_widget(self.returning_player)


        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)

    def new_player_btn(self, instance):
        self.manager.get_screen('loader').transition_move('main', 'creation')

    def returning_player_btn(self, instance):
        self.manager.get_screen('loader').transition_move('main', 'restore')


class CreationScreen(Screen):
    box_layout = DefaultBoxLayout(screen_x, screen_y)
    warn = WarningLabel(screen_x, screen_y)
    backup_image = DefaultImage(screen_x, screen_x/2.5)
    creation_description = DescriptionLabel(screen_x, screen_y, info_creation, 1)
    allow_id = RadioButtonWide(screen_x, screen_y, 'yes, backup it up right now', 2, True)
    deny_id = RadioButtonWide(screen_x, screen_y, 'please let me decide later...', 2, False)
    create_account = SpecialButton(screen_x, screen_y, 'create an account', 4)
    back = SpecialButton(screen_x, screen_y, 'back', 4)
    intro_mask = VinaigretteMask(screen_x, screen_y, 1)


    def __init__(self, **kw):
        super().__init__(**kw)
        self.box_layout.add_widget(self.warn)
        self.box_layout.add_widget(self.backup_image)
        self.box_layout.add_widget(self.creation_description)
        self.box_layout.add_widget(self.allow_id)
        self.allow_id.button.bind(on_press=self.checkbox_allow_btn)
        self.box_layout.add_widget(self.deny_id)
        self.deny_id.button.bind(on_press=self.checkbox_deny_btn)
        self.create_account.button.bind(on_release=self.create_account_btn)
        self.box_layout.add_widget(self.create_account)
        self.back.button.bind(on_release=self.back_btn)
        self.box_layout.add_widget(self.back)
        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)

        self.button_confirmed = False
        self.worker_running = False

    def update_permission_status(self, dt):
        if check_permissions():
            s = search_backups()
            if s == 'exist':
                self.warn.popup(info_creation_warning, False)
                self.button_confirmed = False
            elif s == 'empty':
                cfg.allow_backup = True
                self.manager.get_screen('loader').transition_move('creation', 'entering_screen')
                self.manager.get_screen('entering_screen').connect_me()
            Clock.unschedule(self.update_permission_status)
            self.worker_running = False

    def checkbox_allow_btn(self, instance):
        self.allow_id.active = True
        self.deny_id.active = False
        self.allow_id.toggle_check_box()
        self.deny_id.toggle_check_box()

    def checkbox_deny_btn(self, instance):
        self.deny_id.active = True
        self.allow_id.active = False
        self.allow_id.toggle_check_box()
        self.deny_id.toggle_check_box()

    def create_account_btn(self, instance):
        if self.allow_id.active:
            if not self.button_confirmed:
                self.button_confirmed = True
                if not self.worker_running:
                    self.worker_running = True
                    Clock.schedule_interval(self.update_permission_status, 0.5)
                ask_for_permission()
        else:
            cfg.allow_backup = False
            self.manager.get_screen('loader').transition_move('creation', 'entering_screen')
            self.manager.get_screen('entering_screen').connect_me()

    def back_btn(self, instance):
        self.manager.get_screen('loader').transition_move('creation', 'main')


class RestoreScreen(Screen):
    box_layout = DefaultBoxLayout(screen_x, screen_y)
    warn = WarningLabel(screen_x, screen_y)
    empty_label_top = Label(size_hint=(None, None), width=screen_x, height=screen_y / 12)
    restore_image = DefaultImage(screen_x, screen_x/2.5)
    text_description = DescriptionLabel(screen_x, screen_y, info_restore, 1)
    restore = SpecialButton(screen_x, screen_y, 'restore profile', 4)
    back = SpecialButton(screen_x, screen_y, 'back', 4)
    empty_label_bottom = Label()
    intro_mask = VinaigretteMask(screen_x, screen_y, 1)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.box_layout.add_widget(self.warn)
        self.box_layout.add_widget(self.empty_label_top)
        self.box_layout.add_widget(self.restore_image)
        self.box_layout.add_widget(self.text_description)
        self.box_layout.add_widget(self.empty_label_bottom)
        self.restore.button.bind(on_release=self.restore_btn)
        self.box_layout.add_widget(self.restore)

        self.back.button.bind(on_release=self.back_btn)
        self.box_layout.add_widget(self.back)

        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)

        self.button_confirmed = False
        self.worker_running = False

    def check_for_restore_backup_permission(self, dt):
        if check_permissions():
            result = restore_from_backup()
            if result == 'failed':
                self.warn.popup(info_restore_warning, False)
                self.button_confirmed = False
            else:
                cfg.config.read('../settings.ini')
                cfg.config.set('Startup', 'Secret', restore_from_backup())
                with open('../settings.ini', 'w') as current_config:
                    cfg.config.write(current_config)
                cfg.allow_backup = False
                self.manager.get_screen('loader').transition_move('restore', 'entering_screen')
                self.manager.get_screen('entering_screen').connect_me()
            Clock.unschedule(self.check_for_restore_backup_permission)
            self.worker_running = False

    def restore_btn(self, instance):
        self.manager.get_screen('loader').sound_click.play()
        if not self.button_confirmed:
            self.button_confirmed = True
            if not self.worker_running:
                self.worker_running = True
                Clock.schedule_interval(self.check_for_restore_backup_permission, 0.5)
            ask_for_permission()

    def back_btn(self, instance):
        self.manager.get_screen('loader').transition_move('restore', 'main')


class UpdateScreen(Screen):
    box_layout = DefaultBoxLayout(screen_x, screen_y)
    update_description = DescriptionLabel(screen_x, screen_y, info_update, 1)
    update = SpecialButton(screen_x, screen_y, 'update', 1)
    intro_mask = VinaigretteMask(screen_x, screen_y, 1)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.box_layout.add_widget(Label())
        self.box_layout.add_widget(self.update_description)
        self.box_layout.add_widget(Label())
        self.box_layout.add_widget(Label())
        self.box_layout.add_widget(Label())
        self.update.button.bind(on_release=self.update_btn)
        self.box_layout.add_widget(self.update)
        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)

    def update_btn(self, instance):
        webbrowser.open('https://asyllion.com')


class EnteringScreen(Screen):
    box_layout = DefaultBoxLayout(screen_x, screen_y)
    warn = WarningLabel(screen_x, screen_y)
    intro_mask = VinaigretteMask(screen_x, screen_y, 1)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.box_layout.add_widget(self.warn)
        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)


    def connect_me(self):
        Clock.schedule_interval(self.update_status, 0.08)
        _t = Thread(target=cc.server_connect)
        _t.start()


    def update_status(self, dt):
        global in_game

        if self.intro_mask.transition_finished:

            if cc.update_available:
                self.manager.get_screen('loader').transition_move('entering_screen', 'update')
                Clock.unschedule(self.update_status)

            else:
                if cc.user == 'setup' or cc.user == 'creating':
                    cfg.config.read('../settings.ini')
                    cfg.config.set('Startup', 'Tutorial', 'started')
                    cfg.tutorial = 'started'
                    with open('../settings.ini', 'w') as current_config:
                        cfg.config.write(current_config)
                    self.manager.get_screen('loader').transition_move('entering_screen', 'setup')
                    if cfg.allow_backup:
                        backup_data(cfg.config.get('Startup', 'Secret'))
                    Clock.unschedule(self.update_status)

                elif cc.user == 'entering':
                    in_game = True
                    self.manager.get_screen('loader').intro_to_game = True
                    self.manager.get_screen('loader').transition_move('entering_screen', 'loader')
                    self.manager.get_screen('loader').sound_intro.stop()
                    self.manager.get_screen('loader').sound_intro.unload()
                    self.manager.get_screen('loader').initialize_loader()
                    Clock.unschedule(self.update_status)

                elif cc.current_status is not None:
                    self.warn.popup(cc.current_status, False)
                    Clock.unschedule(self.update_status)


class SetupScreen(Screen):
    box_layout = DefaultBoxLayout(screen_x, screen_y)
    warn = WarningLabel(screen_x, screen_y)
    skin = DefaultImage(screen_x, screen_y/3)
    input_nick = DefaultTextInput(screen_x, screen_y)
    change_skin = SpecialButton(screen_x*0.66, screen_y/24, 'change skin', 5)
    status = DescriptionLabel(screen_x, screen_y, 'choose your profession', 1)
    professions = ProfessionChangeGrid(screen_x, screen_y)
    confirm = SpecialButton(screen_x, screen_y, 'confirm', 1)
    intro_mask = VinaigretteMask(screen_x, screen_y, 1)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box_layout.add_widget(self.warn)
        self.box_layout.add_widget(self.skin)
        self.box_layout.add_widget(self.input_nick)
        self.box_layout.add_widget(Label(size_hint=(0.1,0.1)))
        self.change_skin.button.bind(on_press = self.skin_btn)
        self.box_layout.add_widget(self.change_skin)
        self.box_layout.add_widget(self.status)
        self.professions.buster_button.button.bind(on_press=partial(self.profession_btn, 0))
        self.professions.maestro_button.button.bind(on_press=partial(self.profession_btn, 1))
        self.professions.collector_button.button.bind(on_press=partial(self.profession_btn, 2))
        self.box_layout.add_widget(self.professions)
        self.confirm.button.bind(on_press=self.validate_btn)
        self.box_layout.add_widget(Label(size_hint=(0.4, 0.4)))
        self.box_layout.add_widget(self.confirm)
        self.box_layout.add_widget(Label(size_hint=(1,1)))
        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)

        self.profession = None
        self.player_skin = 6
        self.awaiting_validation = False


    def get_response(self, dt):
        global in_game
        if self.awaiting_validation:
            response = cc.update_server_message()
            if response != '':
                Clock.unschedule(self.get_response)
                self.awaiting_validation = False
                if response != 'passed':
                    self.warn.popup(response, True)
                else:
                    cfg.config.read('../settings.ini')
                    cfg.config.set('Startup', 'Tutorial', 'finished')
                    cfg.tutorial = 'finished'
                    with open('../settings.ini', 'w') as current_config:
                        cfg.config.write(current_config)
                    in_game = True
                    self.manager.get_screen('loader').intro_to_game = True
                    self.manager.get_screen('loader').transition_move('setup', 'loader')
                    sound.sound_intro.stop()
                    sound.sound_intro.unload()
                    self.manager.get_screen('loader').initialize_loader()


    def profession_btn(self, _profession, instance):
        self.profession = _profession
        if _profession == 0:
            self.status.text = 'melee combat profession with \n great defence and attack abilities'
            #self.manager.get_screen('setup').selected.pos_hint = {'x': 0}
        elif _profession == 1:
            self.status.text = 'crafting type profession with \n great stamina and range attack abilities'
            #self.selected.pos_hint = {'center_x': .5}
        elif _profession == 2:
            self.status.text = 'magic combat profession with \n great looting abilities and good attack'
            #self.manager.get_screen('setup').selected.pos_hint = {'right': 1}

    def skin_btn(self, instance):
        if self.player_skin < 6:
            self.player_skin += 1
        else:
            self.player_skin = 1
        self.manager.get_screen("setup").skin.source = f'img/char/char{self.player_skin}.png'


    def validate_btn(self, instance):
        nick = self.input_nick.text

        if self.profession is None:
            self.warn.popup('please choose one of professions', True)
            return

        if not self.awaiting_validation:
            if len(nick) >= 4:
                if len(nick) > 16:
                    self.warn.popup('only 16 characters allowed', True)
                    return
                elif not str.isalpha(nick):
                    self.warn.popup('characters can only be alphabet letters' + '\n' + 'without spaces', True)
                    return
                else:
                    cc.sender.send_nickname(self.profession, self.player_skin, nick)
                    Clock.schedule_interval(self.get_response, 0.1)
                    self.awaiting_validation = True
            elif 0 <= len(nick) < 4:
                self.warn.popup('use minimum 4 characters', True)
                return


class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        self.transition = NoTransition()


class MainApp(App):
    def build(self):
        wm = WindowManager()
        wm.add_widget(LoaderScreen(name = 'loader'))
        return wm


MainApp().run()
