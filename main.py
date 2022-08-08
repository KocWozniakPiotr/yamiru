import kivy
from plyer import notification
from random import random as r
from kivy.utils import platform
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from scripts import client

kivy.require("2.1.0")

if platform == 'android':
    pass
else:
    Window.fullscreen = 0
    Window.size = 360, 640

displaySize = Window.system_size
displayW = displaySize[0]
displayH = displaySize[1]
temp_status = ""
chat_len = 0


class UILayout(Widget):
    xx = displayW
    yy = displayH
    saved_attrs = []

    def click_msg(self):
        pass
        notification.notify(title="Frajer News", message="not today xD", app_name="Yamiru")

    def click_task(self):
        pass

    def click_item(self):
        pass

    def click_option(self):
        pass


class Cell(Widget):
    pass


class Bunny(Widget):
    pass


class Sleeper(Widget):
    pass


class MainGame(Widget):

    def __init__(self):
        super().__init__()
        self.tile_obj = []
        self.scaling = displayW / 12
        self.center_display_y = displayH - (displayW / 2) - (
                displayH - displayW - (displayW / 8) - (displayW / 1.53)) / 4
        self.app = App.get_running_app()

    def start(self):
        # self.gen_ground(8, 8)
        Clock.schedule_interval(self.update, 0.01)

    def update(self, _):
        global temp_status, chat_len
        if temp_status != client.login_status:
            temp_status = client.login_status
            self.app.root.ids.content.text += '\n' + '        ' + temp_status
        if chat_len < len(client.chat_list):
            chat_len = len(client.chat_list)
            self.app.root.ids.content.text += '\n' + '        ' + client.chat_list[0]
        # self.update_ground(8, 8, displayW / 2, self.center_display_y, self.scaling)

    def gen_ground(self, _width, _height, *largs):
        self.canvas.clear()
        _rand = _width * _height
        bunny = (round(r() * _rand))
        with self.canvas:
            for y in range(_height):
                for x in range(_width):
                    if len(self.tile_obj) == bunny:
                        b = Bunny()
                        b.size = (self.scaling, self.scaling * 1.5)
                        self.tile_obj.append(b)
                    else:
                        c = Cell()
                        c.size = (self.scaling, self.scaling)
                        self.tile_obj.append(c)

    def update_ground(self, _width, _height, pos_x, pos_y, scaling, *largs):
        pos_x -= scaling / 2
        cur_y = pos_y
        offset_x = 0
        linear_counter = 0
        with self.canvas:
            for y in range(_height):
                cur_x = pos_x - offset_x
                iso_view_x = 0
                iso_view_y = 0
                for x in range(_width):
                    self.tile_obj[linear_counter].pos = (cur_x + iso_view_x, cur_y + iso_view_y)
                    cur_x += scaling
                    iso_view_x += -(scaling / 2)
                    iso_view_y += -(scaling / 4)
                    linear_counter += 1
                offset_x += scaling / 2
                cur_y -= scaling / 4


class GridApp(App):

    def build(self):
        self.mg = MainGame()
        self.ui = UILayout()
        self.ui.add_widget(self.mg)
        self.mg.start()
        client.t_server_connect.start()
        return self.ui


GridApp().run()
try:
    client.usr.close()
except:
    pass
