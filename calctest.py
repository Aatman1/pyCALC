from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
import re
import math
import cmath

class AdvancedCalculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Dark background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.result = TextInput(
            multiline=False, readonly=True, halign="right", font_size=32,
            background_color=[0.3, 0.3, 0.3, 1], foreground_color=[1, 1, 1, 1],
            size_hint_y=None, height=60
        )
        self.add_widget(self.result)

        self.tabbed_panel = TabbedPanel(do_default_tab=False)
        
        modes = ['Basic', 'Scientific', 'Graphing']
        for mode in modes:
            tab = TabbedPanelItem(text=mode)
            tab.add_widget(self.create_full_button_layout())
            self.tabbed_panel.add_widget(tab)

        self.add_widget(self.tabbed_panel)

        # Graphing area
        self.graph_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=300)
        self.graph_input = TextInput(multiline=False, size_hint_y=None, height=40)
        self.graph_input.bind(on_text_validate=self.plot_graph)
        self.graph_layout.add_widget(self.graph_input)
        
        self.graph_canvas = BoxLayout()
        with self.graph_canvas.canvas:
            Color(1, 1, 1, 1)
            self.plot_area = Rectangle(pos=self.graph_canvas.pos, size=self.graph_canvas.size)
        self.graph_canvas.bind(size=self._update_plot_area, pos=self._update_plot_area)
        self.graph_layout.add_widget(self.graph_canvas)
        
        self.add_widget(self.graph_layout)

        # History
        self.history_label = Label(text="History", size_hint_y=None, height=30)
        self.add_widget(self.history_label)

        self.history = ScrollView(size_hint_y=None, height=100)
        self.history_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.history.add_widget(self.history_layout)
        self.add_widget(self.history)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_plot_area(self, instance, value):
        self.plot_area.pos = instance.pos
        self.plot_area.size = instance.size

    def create_full_button_layout(self):
        layout = GridLayout(cols=5, spacing=5)
        buttons = [
            'sin', 'cos', 'tan', 'log', 'ln',
            'asin', 'acos', 'atan', '10^x', 'e^x',
            '(', ')', 'π', 'e', '^',
            '7', '8', '9', '÷', 'AC',
            '4', '5', '6', '×', '⌫',
            '1', '2', '3', '-', 'Ans',
            '0', '.', '±', '+', '=',
            'x', 'y', 'z', 'i', 'Plot'
        ]
        for button_text in buttons:
            button = Button(
                text=button_text,
                background_normal='',
                background_color=[0.4, 0.4, 0.4, 1] if button_text.isdigit() or button_text in ['.', '±']
                else [0.3, 0.5, 0.7, 1] if button_text in ['sin', 'cos', 'tan', 'log', 'ln', 'asin', 'acos', 'atan', '10^x', 'e^x']
                else [0.7, 0.3, 0.3, 1] if button_text in ['AC', '⌫']
                else [0.3, 0.7, 0.3, 1] if button_text == '='
                else [0.5, 0.5, 0.5, 1],
                color=[1, 1, 1, 1]
            )
            button.bind(on_press=self.on_button_press)
            layout.add_widget(button)
        return layout

    def on_button_press(self, instance):
        current = self.result.text
        button_text = instance.text

        if button_text == 'AC':
            self.result.text = ''
        elif button_text == '⌫':
            self.result.text = self.result.text[:-1]
        elif button_text == '=':
            try:
                result = str(self.evaluate_expression(current))
                self.result.text = result
                self.add_to_history(f"{current} = {result}")
            except Exception as e:
                self.result.text = f'Error: {str(e)}'
                self.add_to_history(f"{current} = Error: {str(e)}")
        elif button_text == 'Plot':
            self.graph_input.text = current
        elif button_text == '±':
            if current and current[0] == '-':
                self.result.text = current[1:]
            else:
                self.result.text = '-' + current
        elif button_text in ['sin', 'cos', 'tan', 'log', 'ln', 'asin', 'acos', 'atan']:
            self.result.text += f"{button_text}("
        elif button_text == '10^x':
            self.result.text += '10**('
        elif button_text == 'e^x':
            self.result.text += 'e**('
        elif button_text == 'π':
            self.result.text += 'pi'
        elif button_text == 'Ans':
            if self.history_layout.children:
                last_result = self.history_layout.children[0].text.split('=')[-1].strip()
                self.result.text += last_result
        else:
            self.result.text += button_text

    def evaluate_expression(self, expr):
        # Replace '^' with '**' for exponentiation
        expr = expr.replace('^', '**')
        
        # Replace multiplication and division characters
        expr = expr.replace('×', '*')
        expr = expr.replace('÷', '/')
        
        # Replace constants
        expr = expr.replace('π', 'math.pi')
        expr = expr.replace('e', 'math.e')
        
        # Replace trigonometric functions
        for func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']:
            expr = expr.replace(f'{func}(', f'math.{func}(')
        
        # Replace logarithmic functions
        expr = expr.replace('log(', 'math.log10(')
        expr = expr.replace('ln(', 'math.log(')
        
        # Evaluate the expression
        return eval(expr, {"__builtins__": None}, {"math": math, "cmath": cmath})

    def add_to_history(self, entry):
        self.history_layout.add_widget(Label(text=entry, size_hint_y=None, height=30))
        self.history.scroll_to(self.history_layout.children[0])

    def plot_graph(self, instance):
        expression = instance.text
        try:
            x_values = [x * 0.1 for x in range(-50, 51)]
            y_values = [self.evaluate_expression(expression.replace('x', str(x))) for x in x_values]

            # Clear previous plot
            self.graph_canvas.canvas.clear()

            with self.graph_canvas.canvas:
                # Draw axes
                Color(0.7, 0.7, 0.7, 1)  # Light gray
                Line(points=[0, self.graph_canvas.height / 2, self.graph_canvas.width, self.graph_canvas.height / 2])
                Line(points=[self.graph_canvas.width / 2, 0, self.graph_canvas.width / 2, self.graph_canvas.height])

                # Plot the function
                Color(1, 0, 0, 1)  # Red
                points = []
                for x, y in zip(x_values, y_values):
                    px = self.graph_canvas.width / 2 + x * 20  # Scale x
                    py = self.graph_canvas.height / 2 + y * 20  # Scale y
                    points.extend([px, py])
                Line(points=points, width=2)
        except Exception as e:
            print(f"Error plotting graph: {e}")
            with self.graph_canvas.canvas:
                Color(1, 1, 1, 1)
                Rectangle(pos=self.graph_canvas.pos, size=self.graph_canvas.size)
                Color(1, 0, 0, 1)
                Label(text=f"Error: {str(e)}", pos=self.graph_canvas.center)

class AdvancedCalculatorApp(App):
    def build(self):
        return AdvancedCalculator()

if __name__ == '__main__':
    AdvancedCalculatorApp().run()