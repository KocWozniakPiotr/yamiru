from kivy.uix.screenmanager import Screen
from scripts.gui import *

res_x = 0
res_y = 0

def update_res_ingame(x, y):
    global res_x, res_y
    res_x = x
    res_y = y

class IngameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box_layout = DefaultBoxLayout(res_x, res_y)
        self.welcome_text = DescriptionLabel(res_x, res_y, 'Welcome ', 2)
        self.intro_mask = VinaigretteMask(res_x, res_y, 1)
        self.box_layout.add_widget(self.welcome_text)
        self.box_layout.add_widget(self.intro_mask)
        self.add_widget(self.box_layout)
