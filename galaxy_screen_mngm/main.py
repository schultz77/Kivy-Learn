from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Triangle, Line, Quad
from kivy.core.window import Window
from kivy import platform
import random
from kivy.core.audio import SoundLoader


class MainWindowApp(Screen):
    from transforms import transform, transform_perspective, transform_2d
    from user_actions import on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up, keyboard_closed
    main_window_text = StringProperty()
    # main_button_text = StringProperty()
    score_txt = StringProperty()
    level_txt = StringProperty()

    perspective_point_x = None
    perspective_point_y = None

    current_offset_x = 0
    current_offset_y = 0

    SPEED = 0.4
    SPEED_X = 3
    current_speed_x = 0
    current_offset_x = 0

    V_NB_LINES = 8
    V_LINES_SPACING = .4  # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 14
    H_LINES_SPACING = .1  # percentage in screen heights
    horizontal_lines = []
    current_y_loop = 0

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.009
    ship = None
    ship_coordinate = [(0, 0), (0, 0), (0, 0)]

    NB_TILES = 8
    tiles = []
    tiles_coordinates = []

    state_game_over = False
    state_game_has_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    run_init_flag = False
    clock_variable = None

    def reset_game(self):
        self.vertical_lines = []
        self.horizontal_lines = []
        self.ship = None
        self.ship_coordinate = [(0, 0), (0, 0), (0, 0)]
        self.tiles = []
        self.tiles_coordinates = []

        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0

        self.score_txt = 'SCORE: 0'
        self.level_txt = ''
        self.SPEED = 0.4

        self.perspective_point_x = Window.width / 2
        self.perspective_point_y = Window.height * 0.75

        self.init_audio()

        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()

        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()

    def on_run_button_pressed(self, self_menu_window):
        self_main_window = self_menu_window.manager.get_screen('main_window')

        self_main_window.reset_game()

        if not self_main_window.run_init_flag:

            if self_main_window.is_desktop():
                self_main_window._keyboard = Window.request_keyboard(self_main_window.keyboard_closed, self_main_window)
                self_main_window._keyboard.bind(on_key_down=self_main_window.on_keyboard_down)
                self_main_window._keyboard.bind(on_key_up=self_main_window.on_keyboard_up)

            self_main_window.clock_variable = Clock.schedule_interval(self_main_window.update, 1.0 / 60.0)
            self_main_window.run_init_flag = True

        if self_main_window.state_game_over:
            self_main_window.sound_restart.play()
        else:
            self_main_window.sound_begin.play()

        self_main_window.sound_music1.play()
        self_main_window.sound_music1.loop = True
        self_main_window.state_game_has_started = True

        self_main_window.state_game_over = False

    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED / 100 * self.height
            self.current_offset_y += speed_y * time_factor

            speed_x = self.current_speed_x / 100 * self.width
            self.current_offset_x += speed_x * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1

                if self.current_y_loop >= 50:
                    self.SPEED = 0.6
                    self.score_txt = 'SCORE: ' + str(self.current_y_loop)
                    self.level_txt = 'Level 2'
                else:
                    self.score_txt = 'SCORE: ' + str(self.current_y_loop)
                    self.level_txt = 'Level 1'

                if self.current_y_loop >= 150:
                    self.SPEED = 0.8
                    self.score_txt = 'SCORE: ' + str(self.current_y_loop)
                    self.level_txt = 'Level 3'

                self.generate_tiles_coordinates()

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            # self.clock_variable.cancel()
            self.manager.current = "menu_window"
            self.manager.transition.direction = "right"
            self.manager.get_screen('menu_window').menu_button_title = 'RESTART'
            Clock.schedule_once(self.play_game_over_voice_sound, 3)


    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tiles(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tiles(self, ti_x, ti_y):
        x_min, y_min = self.get_tile_coordinate(ti_x, ti_y)
        x_max, y_max = self.get_tile_coordinate(ti_x + 1, ti_y + 1)

        for i in range(0, len(self.ship_coordinate)):
            px, py = self.ship_coordinate[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True

        return False

    # def on_main_button_pressed(self):
    #     self.manager.current = "menu_window"
    #     self.manager.transition.direction = "right"
    #     self.manager.get_screen('menu_window').menu_button_title = 'RESTART'

    @staticmethod
    def is_desktop():
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = Window.width / 2
        base_y = self.SHIP_BASE_Y * Window.height
        ship_half_width = self.SHIP_WIDTH * Window.width / 2
        ship_height = self.SHIP_HEIGHT * Window.height
        # ....
        #    2
        #  1   3
        # self.transform
        self.ship_coordinate[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinate[1] = (center_x, base_y + ship_height)
        self.ship_coordinate[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinate[0])
        x2, y2 = self.transform(*self.ship_coordinate[1])
        x3, y3 = self.transform(*self.ship_coordinate[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        # -1 0 1 2
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, Window.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * Window.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * Window.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinate(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)

        return x, y

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append((Line()))

    def update_horizontal_lines(self):
        # spacing = self.V_LINES_SPACING * self.width
        # central_line_x = int(self.width / 2)
        # offset = +int(self.V_NB_LINES / 2) - 0.5

        # x_min = central_line_x - offset * spacing
        # x_min = central_line_x - offset * spacing + self.current_offset_x
        # x_max = central_line_x + offset * spacing + self.current_offset_x
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)
        # spacing_y = self.H_LINES_SPACING * self.height
        for i in range(0, self.H_NB_LINES):
            # line_y = i * spacing_y - self.current_offset_y
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]
            # print(x1, y1, x2, y2)

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        # pass
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0

        # clean the coordinates that are out of the screen
        # ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        # print("foo1")

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index - 1:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

        # print("foo2")

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinate(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinate(tile_coordinates[0]+1, tile_coordinates[1]+1)

            # 2  3
            #
            # 1  4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")

        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = 0.25
        self.sound_galaxy.volume = 0.25
        self.sound_gameover_impact.volume = 0.6
        self.sound_gameover_voice.volume = 0.25
        self.sound_restart.volume = 0.25

    def on_leave(self, *args):
        # self.clear_widgets()
        self.canvas.remove(self.ship)
        for i in range(0, len(self.tiles)):
            self.canvas.remove(self.tiles[i])
        for i in range(0, len(self.horizontal_lines)):
            self.canvas.remove(self.horizontal_lines[i])
        for i in range(0, len(self.vertical_lines)):
            self.canvas.remove(self.vertical_lines[i])


class MenuWindowApp(Screen):

    menu_title = StringProperty('G  A  L  A  X  Y')
    menu_title_credits = StringProperty('POWERED BY BONFIM CORP')
    menu_button_title = StringProperty("START")

    main_window = MainWindowApp()

    def __init__(self, **kwargs):
        super(MenuWindowApp, self).__init__(**kwargs)

        # self.main_window.init_main_window()
        self.main_window.init_audio()
        self.main_window.sound_galaxy.play()

    def on_menu_button_pressed(self):

        self.manager.current = "main_window"
        self.manager.transition.direction = "left"

        # self.main_window.clear_widgets()
        # self.main_window.canvas.clear()
        self.main_window.on_run_button_pressed(self)


class WindowManagerApp(ScreenManager):
    pass


kv = Builder.load_file("screen.kv")


class MyMainApp(App):
    def build(self):
        self.title = 'The B-Galaxy App'
        return kv


MyMainApp().run()
