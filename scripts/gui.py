from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy import utils
from kivy.uix.textinput import TextInput
from scripts.content.audio import SoundContainer

sound = SoundContainer()
########################################################

white = '#ffdaeb'
soft_pink = '#ff477c'
pink = '#d3127d'
hard_pink = '#8a0356'
light_purple = '#480045'
dark_purple = '#290020'

########################################################

info_title = '- SCIONS OF ASYLLION -'

info_creation = 'Would you like to backup your profile locally ?' + '\n' + '\n' + 'Local backup is saved in a form of a picture.' + '\n' + 'You can move it later wherever you want' + '\n' + 'for restoring your account in the future.'

info_creation_warning = 'backup already exists in pictures directory' + '\n' + 'try restoring your profile from it '

info_restore = 'If you already have an account and made' + '\n' + 'a backup of your profile in the past,' + '\n' + 'you can restore it here.' + '\n' + '\n' + 'Your backup is saved in Pictures by default.' + '\n' + 'If you moved it somewhere else,' + '\n' + 'please place it back to the Pictures directory.'

info_restore_warning = 'no backup found in Pictures directory' + '\n' + 'its name should be ASYLLION_BACKUP.png'

info_update = 'a new version of the game is available' + '\n' + 'update to continue...'

########################################################

def custom_font_size(screen_x, text_size):
    if text_size == 1:
        text_size = 0.023
    elif text_size == 2:
            text_size = 0.025
    elif text_size == 3:
            text_size = 0.027
    elif text_size == 4:
            text_size = 0.03
    elif text_size == 5:
            text_size = 0.04
    return (screen_x*2) * text_size


class SpecialButton(BoxLayout):

    def __init__(self, _width, _height, label_text, text_size, **kwargs):
        super().__init__(**kwargs)
        self.button = Button(pos_hint={'center_x': 0.5, 'center_y': 0.5}, size_hint = (None, None))
        self.button.bind(on_press=self.callback_press)
        self.button.bind(on_release=self.callback_release)
        self.button.background_color = [0,0,0,0]
        self.text_label = Label(size_hint = (None, None))
        self.text_label.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self.text_label.font_name = 'misc/pixeltype.ttf'
        self.text_label.color = utils.get_color_from_hex(light_purple)

        self.text_label_shadow = Label(size_hint= (None, None))
        self.text_label_shadow.pos_hint = {'center_x': 0.51, 'center_y': 0.47}

        self.text_label_shadow.font_name = 'misc/pixeltype.ttf'
        self.text_label_shadow.color = utils.get_color_from_hex(pink)

        self.button_layout = RelativeLayout()
        self.icon = Image(size_hint = (None, None))
        self.icon.source = 'img/ui/button_normal.png'
        self.icon.color = utils.get_color_from_hex(soft_pink)
        self.icon.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self.button.width = _width * 0.7
        self.button.height = _width * 0.15

        self.text_label.font_size = custom_font_size(_width, text_size)
        self.text_label.text = label_text

        self.text_label_shadow.font_size = self.text_label.font_size
        self.text_label_shadow.text = label_text

        self.icon.width = _width * 0.7
        self.icon.height = _width * 0.15
        self.icon.allow_stretch = True
        self.icon.keep_ratio = True
        self.icon.reload()

        self.add_widget(self.button_layout)
        self.button_layout.add_widget(self.button)
        self.button_layout.add_widget(self.icon)
        self.button_layout.add_widget(self.text_label_shadow)
        self.button_layout.add_widget(self.text_label)


    def callback_press(self, instance):
        sound.sound_click.play()
        self.icon.color = utils.get_color_from_hex(light_purple)
        self.text_label.pos_hint = {'center_y': 0.47}
        self.text_label.color = utils.get_color_from_hex(soft_pink)
        self.icon.pos_hint = {'center_y': 0.47}
        self.text_label_shadow.color = utils.get_color_from_hex(dark_purple)


    def callback_release(self, instance):
        self.icon.color = utils.get_color_from_hex(soft_pink)
        self.text_label.pos_hint = {'center_y': 0.5}
        self.text_label.color = utils.get_color_from_hex(light_purple)
        self.icon.pos_hint = {'center_y': 0.5}
        self.text_label_shadow.color = utils.get_color_from_hex(pink)


class RadioButtonWide(BoxLayout):

    def __init__(self, _width, _height, label_text, text_size, status, **kwargs):
        super().__init__(**kwargs)
        self.active = status
        self.button = Button(pos_hint={'center_x': 0.5, 'center_y': 0.5}, size_hint=(None, None))
        self.button.bind(on_press=self.on_pressed_checkbox)
        self.button.background_color = [0, 0, 0, 0]
        self.text_label = Label(size_hint=(None, None))
        self.text_label.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.text_label.font_name = 'misc/pixeltype.ttf'
        self.button_layout = RelativeLayout()
        self.icon = Image(size_hint=(None, None))
        if self.active:
            self.icon.source = 'img/ui/radio_btn_selected.png'
            self.text_label.color = utils.get_color_from_hex(soft_pink)
        else:
            self.icon.source = 'img/ui/radio_btn.png'
            self.text_label.color = utils.get_color_from_hex(hard_pink)
        self.icon.color = utils.get_color_from_hex(soft_pink)
        self.icon.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.button.width = _width * 0.7
        self.button.height = _width * 0.15
        self.text_label.font_size = custom_font_size(_width, text_size)
        self.text_label.text = label_text
        self.icon.width = (_width * 0.7)*1.2
        self.icon.height = (_width * 0.15)*1.2
        self.icon.allow_stretch = True
        self.icon.keep_ratio = True
        self.icon.reload()
        self.add_widget(self.button_layout)
        self.button_layout.add_widget(self.button)
        self.button_layout.add_widget(self.icon)
        self.button_layout.add_widget(self.text_label)

    def toggle_check_box(self):
        if self.active:
            self.icon.source = 'img/ui/radio_btn_selected.png'
            self.text_label.color = utils.get_color_from_hex(soft_pink)
        else:
            self.icon.source = 'img/ui/radio_btn.png'
            self.text_label.color = utils.get_color_from_hex(hard_pink)

    def on_pressed_checkbox(self, instance):
        sound.sound_key_press.play()



class DefaultImage(Image):

    def __init__(self, screen_x, screen_y, **kwargs):
        super().__init__(**kwargs)
        self.source = ''
        self.size_hint = None, None
        self.allow_stretch = True
        self.keep_radio = True
        self.width = screen_x
        self.height = screen_y
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}


class DefaultLabel(Label):

    def __init__(self, label_text, screen_x, screen_y, text_size, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = None, None
        self.font_name = 'misc/pixeltype.ttf'
        self.text = label_text
        self.width = screen_x * 0.9
        self.height = screen_y / 12
        self.color = utils.get_color_from_hex(soft_pink)
        self.font_size = custom_font_size(screen_x, text_size)
        self.pos_hint = {'center_x': 0.5}



class DefaultBoxLayout(BoxLayout):

    def __init__(self, screen_x, screen_y, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = None, None
        self.size = screen_x, screen_y
        self.orientation = 'vertical'
        Window.clearcolor = utils.get_color_from_hex(dark_purple)


class WarningLabel(Label):

    def __init__(self, screen_x, screen_y, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'misc/pixeltype.ttf'
        self.opacity = 0
        self.velocity = 0
        self._opacity = 0
        self.halign = "center"
        self.text = ''
        self.font_size = custom_font_size(screen_x, 2)
        self.color = light_purple
        self.width = screen_x
        self.height = screen_y / 12
        self.size_hint = (None, None)
        self.pos = (0, screen_y - (screen_y/12))
        self.size = (screen_x, screen_y / 12)
        c = utils.get_color_from_hex(soft_pink)
        with self.canvas.before:
            Color(c[0], c[1], c[2], c[3])
            Rectangle(pos = self.pos, size= self.size)


    def popup(self, info, fade_out):
        self.text = info
        if self._opacity <= 0:
            sound.sound_error.play()
            if fade_out:
                self._opacity = 1
                self.velocity = 0
                Clock.schedule_interval(self.fade_out_button, 0.05)
            else:
                self._opacity = 1
                self.opacity = self._opacity

    def fade_out_button(self, dt):
        self.opacity = self._opacity
        if self._opacity > 0.0:
            self._opacity -= 0.001 * self.velocity
            if self.velocity < 600:
                self.velocity += 1
            return self._opacity
        else:
            Clock.unschedule(self.fade_out_button)


class DescriptionLabel(Label):

    def __init__(self, screen_x, screen_y, description, text_size , **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'misc/pixeltype.ttf'
        self.text = description
        self.size_hint = (None, None)
        self.pos_hint = {'center_x': 0.5}
        self.width = screen_x * 0.9
        self.height = screen_y / 3.5
        self.font_size = custom_font_size(screen_x, text_size)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0}
        self.halign = 'center'
        self.valign = 'middle'
        self.color = soft_pink


class VinaigretteMask(FloatLayout):

    def __init__(self, screen_x, screen_y, _opacity, **kwargs):
        super().__init__(**kwargs)
        self.mask = Image()
        self.velocity = 0
        self._opacity = _opacity
        self.opacity = _opacity
        self.speed = 0.09
        self.transition_finished = False
        self.mask.source = 'img/ui/vinaigrette.png'
        self.mask.size_hint = None, None
        self.mask.allow_stretch = True
        self.mask.keep_ratio = False
        self.mask.width = screen_x
        self.mask.height = screen_y
        self.mask.pos_hint = {'x': 0, 'y': 0}
        self.add_widget(self.mask)


    def start_screen_fading(self):
        if self.opacity >= 1:
            self._opacity = 1
            self.velocity = 0
            Clock.schedule_interval(self.fadeout_screen, 0.05)
        elif self.opacity == 0:
            self._opacity = 0
            self.velocity = 0
            Clock.schedule_interval(self.fade_in_screen, 0.05)


    def fadeout_screen(self, dt):
        self.opacity = self._opacity
        if self._opacity >= 0:
            self._opacity -= self.speed * self.velocity
            if self.velocity < 600:
                self.velocity += 1
            return self._opacity
        else:
            self.opacity = 0
            self.transition_finished = True
            Clock.unschedule(self.fadeout_screen)

    def fade_in_screen(self, dt):
        self.opacity = self._opacity
        if self._opacity < 1.0:
            self._opacity += self.speed * self.velocity
            if self.velocity < 600:
                self.velocity += 1
            return self._opacity
        else:
            self.opacity = 1
            self.transition_finished = True
            Clock.unschedule(self.fade_in_screen)


class DefaultTextInput(TextInput):

    def __init__(self, screen_x, screen_y, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = screen_x*0.66
        self.height = screen_y/24
        self.pos_hint = {'center_x': 0.5}
        self.disabled = False
        self.font_size = (0.47 * self.height)
        self.font_name = 'misc/pixeltype.ttf'
        self.multiline = False
        self.halign = "center"
        self.valign = "middle"
        self.padding = [0, 15 * (screen_x * 0.001), 0, 0]
        self.cursor_width = "2sp"
        self.hint_text = '' if self.focus else 'enter nickname'
        self.hint_text_color = soft_pink if self.focus else hard_pink
        self.background_normal = dark_purple
        self.background_active = dark_purple
        self.background_color = dark_purple if self.focus else dark_purple
        a = utils.get_color_from_hex(soft_pink)
        b = utils.get_color_from_hex(hard_pink)
        text_field_width = 500 * (screen_x * 0.001)
        text_field_height = 95 * (screen_x * 0.001)
        with self.canvas.before:
            Color(a[0], a[1], a[2], a[3])
            Rectangle(source = 'img/ui/textfield.png', size = (text_field_width, text_field_height), pos = ((screen_x/2) - (text_field_width/2), (screen_y/1.835)))



class ProfessionChangeGrid(GridLayout):

    def __init__(self, screen_x, screen_y, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.size_hint = None, None
        self.size = screen_x, screen_y/24
        self.buster_button = SpecialButton(screen_x*0.5, screen_y*0.5, 'Buster', 5)
        self.maestro_button = SpecialButton(screen_x*0.5, screen_y*0.5, 'Buster', 5)
        self.collector_button = SpecialButton(screen_x*0.5, screen_y*0.5, 'Buster', 5)

        self.add_widget(self.buster_button)
        self.add_widget(self.maestro_button)
        self.add_widget(self.collector_button)





