import tkinter as tk
from tkinter import ttk
import globals

class ServiceFormPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.cursor = controller.cursor
        self.controller = controller
        self._create_widgets()

    def _create_widgets(self):
        container = tk.Frame(self, bg=globals.BACKGROUND_COLOR)
        container.pack(expand=True, fill="both")

        home_btn = ttk.Button(
            container,
            text="Home",
            command=lambda : self.controller.render_page("HOME"),
            style="BTN.TButton"
        )
        home_btn.pack()