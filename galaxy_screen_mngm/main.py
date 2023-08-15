from kivy.app import App
from kivy.graphics import Line, Color, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget

# import torch


class WidgetExample(GridLayout):
    my_text = StringProperty("0")
    counter = 0
    count_enabled = BooleanProperty(False)

    # slider_value_txt = StringProperty("50")

    my_input_str = StringProperty("foo")

    def on_button_click(self):
        print('Button Clicked')
        if self.count_enabled:
            self.counter += 1
            self.my_text = "{}".format(self.counter)

    def on_toggle_button_state(self, widget):
        print("Button state " + widget.state)
        if widget.state == 'normal':
            # off
            widget.text = "OFF"
            self.count_enabled = False
            # x = torch.rand(5, 3)
            # print(x)

        else:
            # on
            widget.text = "ON"
            self.count_enabled = True

    @staticmethod
    def on_switch_active(widget):
        print('Switch: ' + str(widget.active))

    # def on_slider_value(self, widget):
        # print("Slider: " + str(int(widget.value)))
        # self.slider_value_txt = str(int(widget.value))

    def on_text_validate(self, widget):
        self.my_input_str = widget.text


class StackLayoutExample(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "lr-tb"
        for i in range(0, 100):
            # size = dp(100) + i*10
            size = dp(100)
            b = Button(text=str(i+1), size_hint=(None, None), size=(size, size))
            self.add_widget(b)


class AnchorLayoutExample(AnchorLayout):
    pass


class BoxLayoutExample(BoxLayout):
    pass
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        b1 = Button(text='A')
        b2 = Button(text='B')
        b3 = Button(text='C')
        self.add_widget(b1)
        self.add_widget(b2)
        self.add_widget(b3)

    """


class MainWidget(Widget):
    pass


class TheLabApp(App):
    pass


class CanvasExample1(Widget):
    pass


class CanvasExample2(Widget):
    pass


class CanvasExample3(Widget):
    pass


class CanvasExample4(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Line(points=(100, 100, 400, 500), width=2)
            Color(0, 1, 0)
            Line(circle=(200, 200, 100), width=2)
            Line(rectangle=(600, 200, 20, 50), width=4)
            Line(ellipse=(500, 300, 100, 50), width=2)
            self.rect = Rectangle(pos=(300, 100), size=(150, 100))
            self.move_forward = True

    def on_button_a_click(self):
        x, y = self.rect.pos
        rect_width, rect_height = self.rect.size

        if x + rect_width < self.width and self.move_forward:
            x += dp(10)
        elif x > 0:
            x -= dp(10)
            self.move_forward = False
        else:
            self.move_forward = True

        self.rect.pos = (x, y)


class CanvasExample5(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball_size = dp(50)
        self.vx = dp(3)
        self.vy = dp(4)
        with self.canvas:
            self.ball = Ellipse(pos=(100, 100), size=(self.ball_size, self.ball_size))
        Clock.schedule_interval(self.update, 1/60)

    def on_size(self, *args):
        # print('on size:')
        self.ball.pos = (self.center_x - self.ball_size/2, self.center_y - self.ball_size/2)

    def update(self, dt):
        # print("update")
        x, y = self.ball.pos

        if x + self.ball_size > self.width:
            x = self.width - self.ball_size
            self.vx = - self.vx
        elif x < 0:
            x = 0
            self.vx = - self.vx
        if y + self.ball_size > self.height:
            y = self.height - self.ball_size
            self.vy = - self.vy
        elif y < 0:
            y = 0
            self.vy = - self.vy
        x += self.vx
        y += self.vy
        self.ball.pos = (x, y)


class CanvasExample6(Widget):
    pass


class CanvasExample7(BoxLayout):
    pass


TheLabApp().run()
