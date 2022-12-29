from intro import *
from kivy import utils
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget



purple_light = '#0c061c'
red_light = '#c7185e'
red_middle = '#990842'


class GameDisplay(Image):

    def __init__(self, **kwargs):
        super(GameDisplay, self).__init__(**kwargs)
        self.source = 'img/ui_design.png'
        self.allow_stretch = True
        self.keep_radio = True
        self.size = (screen_x, screen_y)
        self.size_hint = (None, None)
        # HERE IS VERY GOOD START DOWN THERE :D
        self.pos = (0, 0)

class Menu(Image):

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.source = 'img/menu_mask.png'
        self.allow_stretch = True
        self.keep_radio = True
        # self.pos = (0, )

class Items(Image):

    def __init__(self, **kwargs):
        super(Items, self).__init__(**kwargs)
        self.source = 'img/items_mask.png'
        self.allow_stretch = True
        self.keep_radio = True


class MyButton(ButtonBehavior, Image):

    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.source = 'img/button_normal.png'
        self.width = screen_x*0.7
        self.height = screen_x*0.15
        self.allow_stretch = True
        self.keep_radio = True
        self.size_hint = (None, None)


    def on_press(self):
        self.source = 'img/button_normal.png'


    def on_release(self):
        self.source = 'img/button_normal.png'


class IngameScreen(Screen):
    xx = screen_x
    yy = screen_y


    def __init__(self, **kw):
        super().__init__(**kw)
        self.for_fun_label = Label(text='WELCOME  IN  DA  GAME  :D')
        self.for_fun_label.color = utils.get_color_from_hex(purple_light)
        self.for_fun_label.font_size = screen_x / 16
        self.for_fun_label.width = screen_x
        self.for_fun_label.height = screen_y / 12
        self.for_fun_label.pos = (0, screen_y / 12)


    def load_content(self):
        game_display = GameDisplay()
        menu = Menu()
        items = Items()
        modify_btn = MyButton()

        c = utils.get_color_from_hex(red_light)
        #with self.for_fun_label.canvas.before:
        #    Color(c[0], c[1], c[2], c[3])
        #    Rectangle(pos=(0, screen_y / 2),
        #              size=(screen_x, screen_y / 12))
        self.ids.float_layout.add_widget(game_display)
        #self.ids.float_layout.add_widget(menu)
        #self.ids.float_layout.add_widget(items)
        # self.ids.box_layout.add_widget(self.for_fun_label)
        # self.ids.box_layout.add_widget(modify_btn)

    def animate_title(self):
        anim = Animation(x=0, y=screen_y / 2, duration=1.0)
        anim.start(self.for_fun_label)


class MainApp(App):

    def build(self):
        return Builder.load_file('kv/loading_section.kv')



MainApp().run()
