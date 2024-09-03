import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sympy as sp
import re
from collections import deque

class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Calculator")
        self.geometry("1000x600")
        
        self.is_dark_mode = False
        self.current_mode = "Basic"
        self.is_history_visible = False
        self.history = deque(maxlen=10)
        self.last_answer = "0"
        
        self.style = ttk.Style(self)
        self.create_themes()
        
        self.create_widgets()
        self.bind("<Configure>", self.on_resize)
        
    def create_themes(self):
        # Light theme
        light_theme = {
            "TButton": {"configure": {"font": ("Arial", 14, "bold"), "anchor": "center", "padding": 5}},
            "Calculator.TButton": {"configure": {"anchor": "center", "padding": 5}},
            "Operation.TButton": {"configure": {"background": "#c97600", "foreground": "white", "anchor": "center", "padding": 5}},
            "Function.TButton": {"configure": {"background": "#2fa9e0", "foreground": "white", "anchor": "center", "padding": 5}},
            "TFrame": {"configure": {"background": "#f0f0f0"}},
            "TEntry": {"configure": {"foreground": "#000000", "background": "#ffffff", "font": ("Arial", 24)}},
            "TNotebook": {"configure": {"background": "#f0f0f0"}},
            "TNotebook.Tab": {"configure": {"background": "#e0e0e0", "foreground": "#000000", "padding": [5, 2]}},
            "History.TFrame": {"configure": {"background": "#ffffff"}},
            "History.TLabel": {"configure": {"background": "#ffffff", "foreground": "#000000", "font": ("Arial", 12)}},
        }
        
        self.style.theme_create("calculator_light_theme", parent="alt", settings=light_theme)
        
        # Dark theme
        dark_theme = {
            "TButton": {"configure": {"background": "#4d4d4d", "foreground": "#ffffff", "font": ("Arial", 14, "bold"), "anchor": "center", "padding": 5}},
            "Calculator.TButton": {"configure": {"background": "#4d4d4d", "foreground": "white" ,"anchor": "center", "padding": 5}},
            "Operation.TButton": {"configure": {"background": "#c97600", "foreground": "white", "anchor": "center", "padding": 5}},
            "Function.TButton": {"configure": {"background": "#2fa9e0", "foreground": "white", "anchor": "center", "padding": 5}},
            "TFrame": {"configure": {"background": "#2c2c2c"}},
            "TEntry": {"configure": {"foreground": "#ffffff", "background": "#2c2c2c", "fieldbackground": "#2c2c2c", "font": ("Arial", 24)}},
            "TNotebook": {"configure": {"background": "#2c2c2c"}},
            "TNotebook.Tab": {"configure": {"background": "#3c3c3c", "foreground": "#ffffff", "padding": [5, 2]}},
            "History.TFrame": {"configure": {"background": "#1c1c1c"}},
            "History.TLabel": {"configure": {"background": "#1c1c1c", "foreground": "#ffffff", "font": ("Arial", 12)}},
        }
        
        self.style.theme_create("calculator_dark_theme", parent="alt", settings=dark_theme)
        
        # Set initial theme
        self.style.theme_use("calculator_light_theme")
    
    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a frame for the top bar
        self.top_bar = ttk.Frame(self.main_frame)
        self.top_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Create the dark mode toggle button
        self.dark_mode_button = ttk.Button(
            self.top_bar, 
            text="☀️",  # Sun emoji for light mode
            command=self.toggle_color_mode,
            width=3
        )
        self.dark_mode_button.pack(side=tk.RIGHT, padx=5)
        
        # Create the history toggle button
        self.history_button = ttk.Button(
            self.top_bar, 
            text="📜",  # Scroll emoji for history
            command=self.toggle_history,
            width=3
        )
        self.history_button.pack(side=tk.RIGHT, padx=5)
        
        # Create a frame for the calculator and history
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the calculator
        self.calculator_frame = ttk.Frame(self.content_frame)
        self.calculator_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.result_var = tk.StringVar()
        self.result_var.set("0")
        
        self.result_display = ttk.Entry(self.calculator_frame, textvariable=self.result_var, justify="right", font=("Arial", 24))
        self.result_display.pack(fill=tk.X, padx=5, pady=5)
        self.result_display.bind("<Return>", self.solve_problem)
        
        self.notebook = ttk.Notebook(self.calculator_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.basic_frame = ttk.Frame(self.notebook)
        self.scientific_frame = ttk.Frame(self.notebook)
        self.graphing_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.basic_frame, text="Basic")
        self.notebook.add(self.scientific_frame, text="Scientific")
        self.notebook.add(self.graphing_frame, text="Graphing")
        
        self.create_basic_buttons(self.basic_frame)
        self.create_scientific_buttons(self.scientific_frame)
        self.create_graphing_buttons(self.graphing_frame)
        
        self.graph_frame = ttk.Frame(self.graphing_frame)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create history display
        self.history_frame = ttk.Frame(self.content_frame, style="History.TFrame")
        self.history_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), pady=5)
        
        self.history_title = ttk.Label(self.history_frame, text="History", style="History.TLabel")
        self.history_title.pack(pady=(0, 5))
        
        self.history_listbox = tk.Listbox(self.history_frame, font=("Arial", 12), height=20, width=30)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

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
            ('C', 0, 0), ('(', 0, 1), (')', 0, 2), ('÷', 0, 3), ('sin', 0, 4), ('cos', 0, 5), ('tan', 0, 6),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3), ('asin', 1, 4), ('acos', 1, 5), ('atan', 1, 6),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3), ('log', 2, 4), ('ln', 2, 5), ('e^x', 2, 6),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3), ('x^y', 3, 4), ('√', 3, 5), ('∛', 3, 6),
            ('ANS', 4, 0), ('0', 4, 1), ('.', 4, 2), ('x', 4, 3), ('π', 4, 4), ('e', 4, 5), ('|x|', 4, 6),
            ('Plot', 5, 0, 2), ('Clear', 5, 2, 2), ('Zoom In', 5, 4), ('Zoom Out', 5, 5), ('Reset', 5, 6),
        ]
        
        self.create_button_grid(parent, buttons)

    def create_button_grid(self, parent, buttons):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        for button in buttons:
            text = button[0]
            row = button[1]
            col = button[2]
            colspan = button[3] if len(button) > 3 else 1
            
            style = "Calculator.TButton"
            if text in ['÷', '×', '-', '+', '=']:
                style = "Operation.TButton"
            elif text not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'C', '(', ')']:
                style = "Function.TButton"
            
            btn = ttk.Button(buttons_frame, text=text, style=style, command=lambda x=text: self.button_click(x))
            btn.grid(row=row, column=col, columnspan=colspan, padx=2, pady=2, sticky="nsew")
        
        for i in range(6):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(7):
            buttons_frame.grid_columnconfigure(i, weight=1)

    def button_click(self, key):
        current = self.result_var.get()
        if key == '=':
            self.solve_problem()
        elif key == 'C':
            self.result_var.set("0")
        elif key == 'ANS':
            if current == "0":
                self.result_var.set(self.last_answer)
            else:
                self.result_var.set(current + self.last_answer)
        elif key == 'Plot':
            self.update_graph()
        elif key == 'Clear':
            self.result_var.set("0")
            if self.current_mode == "Graphing":
                self.update_graph()
        elif key in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'log', 'ln', '√', '∛']:
            if current == "0":
                self.result_var.set(key + '(')
            else:
                self.result_var.set(current + key + '(')
        elif key in ['π', 'e', '(', ')']:
            if current == "0":
                self.result_var.set(key)
            else:
                self.result_var.set(current + key)
        elif key == 'x^y':
            self.result_var.set(current + '^')
        elif key == 'e^x':
            if current == "0":
                self.result_var.set('exp(')
            else:
                self.result_var.set(current + 'exp(')
        elif key == '|x|':
            if current == "0":
                self.result_var.set('abs(')
            else:
                self.result_var.set(current + 'abs(')
        elif key == '!':
            if current == "0":
                self.result_var.set('fact(')
            else:
                self.result_var.set(current + 'fact(')
        elif key == 'mod':
            self.result_var.set(current + '%')
        elif key in ['Zoom In', 'Zoom Out', 'Reset']:
            self.handle_zoom(key)
        elif key == '±':
            if current.startswith('-'):
                self.result_var.set(current[1:])
            else:
                self.result_var.set('-' + current)
        else:
            if current == "0":
                self.result_var.set(key)
            else:
                self.result_var.set(current + key)

    def solve_problem(self, event=None):
        try:
            expression = self.result_var.get()
            result = self.evaluate_expression(expression)
            self.result_var.set(result)
            self.last_answer = str(result)
            self.history.appendleft(f"{expression} = {result}")
            self.update_history_display()
            if self.current_mode == "Graphing":
                self.update_graph()
        except Exception as e:
            self.result_var.set("Error")
            self.history.appendleft(f"{expression} = Error")
            self.update_history_display()

    def evaluate_expression(self, expression):
        x = sp.Symbol('x')
        # Insert * for implicit multiplication
        expression = re.sub(r'(\d+)([x])', r'\1*\2', expression)
        expression = re.sub(r'(\d+)(pi|e)', r'\1*\2', expression)
        expression = expression.replace('÷', '/')
        expression = expression.replace('×', '*')
        expression = expression.replace('^', '**')
        expression = expression.replace('√', 'sqrt')
        expression = expression.replace('∛', 'cbrt')
        expression = expression.replace('ln', 'log')
        expression = expression.replace('π', 'pi')
        expression = expression.replace('deg', 'degrees')
        expression = expression.replace('rad', 'radians')
        expression = expression.replace('fact(', 'factorial(')
        try:
            expr = sp.sympify(expression, locals={'x': x})
            if self.current_mode == "Graphing":
                return sp.lambdify(x, expr, modules=['numpy', 'sympy'])
            else:
                return float(expr.evalf())
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")

    def update_graph(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        try:
            x = np.linspace(-10, 10, 1000)
            func = self.evaluate_expression(self.result_var.get())
            y = func(x)
            self.ax.plot(x, y)
            self.ax.axhline(y=0, color='k', linewidth=0.5)
            self.ax.axvline(x=0, color='k', linewidth=0.5)
            self.ax.set_title(f"y = {self.result_var.get()}")
            self.ax.set_xlim(-10, 10)
            y_min, y_max = np.min(y[np.isfinite(y)]), np.max(y[np.isfinite(y)])
            y_range = y_max - y_min
            self.ax.set_ylim(y_min - 0.1*y_range, y_max + 0.1*y_range)
            if self.is_dark_mode:
                self.fig.patch.set_facecolor('#2c2c2c')
                self.ax.set_facecolor('#2c2c2c')
                self.ax.xaxis.label.set_color('#ffffff')
                self.ax.yaxis.label.set_color('#ffffff')
                self.ax.title.set_color('#ffffff')
                self.ax.tick_params(axis='x', colors='#ffffff')
                self.ax.tick_params(axis='y', colors='#ffffff')
                self.ax.spines['bottom'].set_color('#ffffff')
                self.ax.spines['top'].set_color('#ffffff')
                self.ax.spines['left'].set_color('#ffffff')
                self.ax.spines['right'].set_color('#ffffff')
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center', wrap=True)

        self.canvas.draw()

    def handle_zoom(self, action):
        if action == 'Zoom In':
            self.ax.set_xlim(self.ax.get_xlim()[0] / 2, self.ax.get_xlim()[1] / 2)
            self.ax.set_ylim(self.ax.get_ylim()[0] / 2, self.ax.get_ylim()[1] / 2)
        elif action == 'Zoom Out':
            self.ax.set_xlim(self.ax.get_xlim()[0] * 2, self.ax.get_xlim()[1] * 2)
            self.ax.set_ylim(self.ax.get_ylim()[0] * 2, self.ax.get_ylim()[1] * 2)
        elif action == 'Reset':
            self.ax.set_xlim(-10, 10)
            self.ax.set_ylim(-10, 10)
        
        self.canvas.draw()

    def toggle_color_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.style.theme_use("calculator_dark_theme")
            self.dark_mode_button.config(text="🌙")  # Moon emoji for dark mode
            self.history_listbox.config(bg="#1c1c1c", fg="#ffffff")
        else:
            self.style.theme_use("calculator_light_theme")
            self.dark_mode_button.config(text="☀️")  # Sun emoji for light mode
            self.history_listbox.config(bg="#ffffff", fg="#000000")
        
        if self.current_mode == "Graphing":
            self.update_graph()

    def toggle_history(self):
        self.is_history_visible = not self.is_history_visible
        if self.is_history_visible:
            self.history_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), pady=5)
            self.history_button.config(text="🗒️")  # Note emoji for visible history
        else:
            self.history_frame.pack_forget()
            self.history_button.config(text="📜")  # Scroll emoji for hidden history

    def update_history_display(self):
        self.history_listbox.delete(0, tk.END)
        for item in self.history:
            self.history_listbox.insert(tk.END, item)

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        self.current_mode = selected_tab
        if self.current_mode == "Graphing":
            self.update_graph()

    def on_resize(self, event):
        # Adjust font size based on window size
        window_width = self.winfo_width()
        button_font_size = max(10, min(20, int(window_width / 50)))  # Adjust these values as needed
        self.style.configure("TButton", font=("Arial", button_font_size, "bold"))
        self.style.configure("Calculator.TButton", font=("Arial", button_font_size, "bold"))
        self.style.configure("Operation.TButton", font=("Arial", button_font_size, "bold"))
        self.style.configure("Function.TButton", font=("Arial", button_font_size, "bold"))

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()