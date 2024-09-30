import sys
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QTabWidget, QFrame, QVBoxLayout, QHBoxLayout, QScrollArea, QListWidget, QListWidgetItem, QAbstractItemView, QMainWindow
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import sympy as sp
import re
from collections import deque

class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Calculator")
        self.setGeometry(100, 100, 1000, 600)

        self.is_dark_mode = False
        self.current_mode = "Basic"
        self.is_history_visible = False
        self.history = deque(maxlen=10)
        self.last_answer = "0"

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_frame.setLayout(self.main_layout)
        self.setCentralWidget(self.main_frame)

        # Create a frame for the top bar
        self.top_bar = QFrame()
        self.top_bar_layout = QHBoxLayout()
        self.top_bar.setLayout(self.top_bar_layout)
        self.main_layout.addWidget(self.top_bar)

        # Create the dark mode toggle button
        self.dark_mode_button = QPushButton("☀️")
        self.dark_mode_button.clicked.connect(self.toggle_color_mode)
        self.top_bar_layout.addWidget(self.dark_mode_button)

        # Create the history toggle button
        self.history_button = QPushButton("📜")
        self.history_button.clicked.connect(self.toggle_history)
        self.top_bar_layout.addWidget(self.history_button)

        # Create a frame for the calculator and history
        self.content_frame = QFrame()
        self.content_layout = QHBoxLayout()
        self.content_frame.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_frame)

        # Create a frame for the calculator
        self.calculator_frame = QFrame()
        self.calculator_layout = QVBoxLayout()
        self.calculator_frame.setLayout(self.calculator_layout)
        self.content_layout.addWidget(self.calculator_frame)

        self.result_var = ""
        self.result_display = QListWidget()
        self.result_display.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.calculator_layout.addWidget(self.result_display)

        self.notebook = QTabWidget()
        self.calculator_layout.addWidget(self.notebook)

        self.basic_frame = QFrame()
        self.scientific_frame = QFrame()
        self.graphing_frame = QFrame()

        self.notebook.addTab(self.basic_frame, "Basic")
        self.notebook.addTab(self.scientific_frame, "Scientific")
        self.notebook.addTab(self.graphing_frame, "Graphing")

        self.create_basic_buttons(self.basic_frame)
        self.create_scientific_buttons(self.scientific_frame)
        self.create_graphing_buttons(self.graphing_frame)

        self.graph_frame = QFrame()
        self.graph_frame_layout = QVBoxLayout()
        self.graph_frame.setLayout(self.graph_frame_layout)
        self.graphing_frame.setLayout(self.graph_frame_layout)

        # Create history display
        self.history_frame = QFrame()
        self.history_frame_layout = QVBoxLayout()
        self.history_frame.setLayout(self.history_frame_layout)
        self.content_layout.addWidget(self.history_frame)

        self.history_title = QListWidget()
        self.history_title.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_title.addItem("History")
        self.history_frame_layout.addWidget(self.history_title)

        self.history_listbox = QListWidget()
        self.history_listbox.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_frame_layout.addWidget(self.history_listbox)

        self.notebook.currentChanged.connect(self.on_tab_change)

    def create_basic_buttons(self, parent):
        buttons = [
            ('C', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 2), ('.', 4, 2), ('=', 4, 3),
        ]

        self.create_button_grid(parent, buttons)

    def create_scientific_buttons(self, parent):
        buttons = [
            ('C', 0, 0), ('(', 0, 1), (')', 0, 2), ('÷', 0, 3), ('sin', 0, 4), ('cos', 0, 5), ('tan', 0, 6),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3), ('asin', 1, 4), ('acos', 1, 5), ('atan', 1, 6),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3), ('log', 2, 4), ('ln', 2, 5), ('e^x', 2, 6),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3), ('x^y', 3, 4), ('√', 3, 5), ('∛', 3, 6),
            ('ANS', 4, 0), ('0', 4, 1), ('.', 4, 2), ('=', 4, 3), ('π', 4, 4), ('e', 4, 5), ('|x|', 4, 6),
            ('sinh', 5, 0), ('cosh', 5, 1), ('tanh', 5, 2), ('deg', 5, 3), ('rad', 5, 4), ('!', 5, 5), ('%', 5, 6),
        ]

        self.create_button_grid(parent, buttons)

    def create_graphing_buttons(self, parent):
        buttons = [
            ('C', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 2), ('.', 4, 2), ('=', 4, 3),
            ('x', 5, 0), ('y', 5, 1), ('z', 5, 2), ('graph', 5, 3),
        ]

        self.create_button_grid(parent, buttons)

    def create_button_grid(self, parent, buttons):
        grid = QGridLayout()
        parent.setLayout(grid)

        for button in buttons:
            if len(button) == 4:
                btn = QPushButton(button[0])
                btn.clicked.connect(self.on_button_click)
                grid.addWidget(btn, button[1], button[2], 1, button[3])
            else:
                btn = QPushButton(button[0])
                btn.clicked.connect(self.on_button_click)
                grid.addWidget(btn, button[1], button[2])

    def on_button_click(self):
        button = self.sender()
        text = button.text()

        if text == '=':
            self.calculate_result()
        elif text == 'C':
            self.clear_result()
        elif text == '±':
            self.change_sign()
        elif text == '%':
            self.calculate_percentage()
        elif text == 'graph':
            self.graph_function()
        elif text == 'sin':
            self.append_to_result('math.sin(')
        elif text == 'cos':
            self.append_to_result('math.cos(')
        elif text == 'tan':
            self.append_to_result('math.tan(')
        elif text == 'asin':
            self.append_to_result('math.asin(')
        elif text == 'acos':
            self.append_to_result('math.acos(')
        elif text == 'atan':
            self.append_to_result('math.atan(')
        elif text == 'log':
            self.append_to_result('math.log(')
        elif text == 'ln':
            self.append_to_result('math.log(')
        elif text == 'e^x':
            self.append_to_result('math.exp(')
        elif text == 'x^y':
            self.append_to_result('**')
        elif text == '√':
            self.append_to_result('math.sqrt(')
        elif text == '∛':
            self.append_to_result('round(' + self.result_var + '**(1./3))')
        elif text == 'π':
            self.append_to_result('math.pi')
        elif text == 'e':
            self.append_to_result('math.e')
        elif text == '|x|':
            self.append_to_result('abs(')
        elif text == 'sinh':
            self.append_to_result('math.sinh(')
        elif text == 'cosh':
            self.append_to_result('math.cosh(')
        elif text == 'tanh':
            self.append_to_result('math.tanh(')
        elif text == '!':
            self.append_to_result('math.factorial(')
        elif text == '%':
            self.append_to_result('/100')
        else:
            self.append_to_result(text)

    def on_tab_change(self):
        self.current_mode = self.notebook.tabText(self.notebook.currentIndex())

    def toggle_color_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.setStyleSheet("background-color: #2b2b2b; color: #ffffff")
            self.dark_mode_button.setText("🌙")
        else:
            self.setStyleSheet("")
            self.dark_mode_button.setText("☀️")

    def toggle_history(self):
        self.is_history_visible = not self.is_history_visible
        if self.is_history_visible:
            self.history_frame.show()
        else:
            self.history_frame.hide()

    def append_to_result(self, text):
        self.result_var += text
        self.result_display.clear()
        self.result_display.addItem(self.result_var)

    def clear_result(self):
        self.result_var = ""
        self.result_display.clear()

    def change_sign(self):
        if self.result_var:
            if self.result_var[0] == '-':
                self.result_var = self.result_var[1:]
            else:
                self.result_var = '-' + self.result_var
            self.result_display.clear()
            self.result_display.addItem(self.result_var)

    def calculate_percentage(self):
        if self.result_var:
            self.result_var = str(float(self.result_var) / 100)
            self.result_display.clear()
            self.result_display.addItem(self.result_var)

    def calculate_result(self):
        try:
            # Replace ^ with **, × with *, and ÷ with / before evaluating the expression
            expression = self.result_var.replace('^', '**').replace('×', '*').replace('÷', '/')
            # Replace cos, sin, and tan with their corresponding Python functions
            expression = expression.replace('cos(', 'math.cos(math.radians(').replace('sin(', 'math.sin(math.radians(').replace('tan(', 'math.tan(math.radians(')
            result = eval(expression)
            full_calculation = self.result_var + ' = ' + str(result)
            self.history.append(full_calculation)
            self.history_listbox.clear()
            for item in self.history:
                self.history_listbox.addItem(item)
            self.last_answer = str(result)
            self.result_var = str(result)
            self.result_display.clear()
            self.result_display.addItem(self.result_var)
        except Exception as e:
            self.result_var = "Error"
            self.result_display.clear()
            self.result_display.addItem(self.result_var)

    def graph_function(self):
        try:
            x = sp.symbols('x')
            func = sp.sympify(self.result_var)
            x_vals = np.linspace(-10, 10, 400)
            y_vals = sp.lambdify(x, func, 'numpy')(x_vals)

            fig = Figure()
            ax = fig.add_subplot(111)
            ax.plot(x_vals, y_vals)
            ax.set_title('Graph of ' + self.result_var)
            ax.set_xlabel('x')
            ax.set_ylabel('y')

            canvas = FigureCanvas(fig)
            self.graph_frame_layout.addWidget(canvas)
        except Exception as e:
            self.result_var = "Error"
            self.result_display.clear()
            self.result_display.addItem(self.result_var)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculatorApp()
    window.show()
    sys.exit(app.exec())