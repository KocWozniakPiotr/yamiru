from kivy.core.audio import SoundLoader


class SoundContainer:

    def __init__(self):
        ####################################### INTERFACE SOUNDS
        self.sound_intro = None
        self.sound_click = None
        self.sound_error = None
        self.sound_key_press = None
        self.sound_logging = None
        ####################################### INGAME SOUNDS
        self.sound_ingame = None


    def load_interface_sounds(self, current_scene):
        if current_scene == 'intro_scene':
            self.sound_error = SoundLoader.load('sfx/error.ogg')
            self.sound_key_press = SoundLoader.load('sfx/key_press.ogg')
            self.sound_click = SoundLoader.load('sfx/click.ogg')
            self.sound_intro = SoundLoader.load('sfx/intro.ogg')
        if current_scene != 'intro_scene':
            pass  # self.manager.get_screen('loader').sound_intro.unload()

    def load_game_sounds(self, current_scene):
        if current_scene == 'intro_scene':
            self.sound_logging = SoundLoader.load('sfx/logging.ogg')
        if current_scene == 'game_scene':
            self.sound_ingame = SoundLoader.load('sfx/ingame.ogg')

    def unload_interface_sounds(self):
        pass

    def unload_game_sounds(self):
        pass

    def mute_music(self):
        pass

    def mute_sounds(self):
        pass
