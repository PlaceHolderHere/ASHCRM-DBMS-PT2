import tkinter as tk
from database_connection import create_database_connection, get_env_variables
from tkinter import messagebox
from pages.home_page import HomePage
from pages.patients_page import PatientsPage
from pages.login_page import LogInPage
from qr_scanner import QrScanner

class App:
    def __init__(self):
        # Database Variables
        env_variables = get_env_variables(".env")
        self.connection = create_database_connection(env_variables)
        self.cursor = self.connection.cursor()

        # Gloabl Variables
        self.window_width: int = 1280
        self.window_height: int = 720
        self.viewWidth = self.window_width / 100
        self.viewHeight = self.window_height / 100
        self._resize_timer = None
        self.pages = {
            "HOME": HomePage,
            "PATIENTS": PatientsPage,
            "LOGIN": LogInPage,
            "QR": QrScanner
        }
        self.loaded_pages = {}

        # Tkinter Initialization
        self.root = tk.Tk()
        self.root.title("ASHCRM")
        self.center_window()

        # Full Window Container for all content
        self.content_container = tk.Frame(self.root)
        self.content_container.pack(side="top", fill="both", expand=True)

        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Run a function when the user:
        self.root.protocol("WM_DELETE_WINDOW", self.close_app) # Closes the window
        self.root.bind("<Configure>", self.on_configure) # Resizing the window

    def start_app(self):
        self.load_pages()
        self.render_page("LOGIN")
        self.root.mainloop()

    def load_pages(self):
        for key, page in self.pages.items():
            loaded_page = page(self.content_container, self)
            self.loaded_pages[key] = loaded_page
            loaded_page.grid(row=0, column=0, sticky="nsew")

    def render_page(self, page) -> bool:
        fetched_page = self.loaded_pages.get(page)
        if fetched_page is None:
            print(f"Error, {page} page not found")
            return False

        fetched_page.tkraise()
        return True

    def close_app(self):
        if messagebox.askokcancel("Quit", "Do you want to save your progress and exit?"):
            self.cursor.close()
            self.connection.close()
            self.root.destroy()  # close the window

    def on_configure(self, event: tk.Event) -> None:
        if event.widget != self.root:
            return

        # Checking if the window has been resized
        new_window_width: int = event.width
        new_window_height: int = event.height
        if new_window_width == self.window_width and self.window_height == new_window_height:
            return

        # Runs on_resize() if the window hasnt been resized after 250ms
        if self._resize_timer is not None:
            self.root.after_cancel(self._resize_timer)

        self._resize_timer = self.root.after(250, lambda : self.on_resize(new_window_width, new_window_height))

    def on_resize(self, window_width: int, window_height: int) -> None:
        self.window_width = window_width
        self.window_height = window_height
        self.viewWidth = self.window_width / 100
        self.viewHeight = self.window_height / 100

    def center_window(self):
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculating the center of the screen relative to the window size
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)

        # Set the dimensions and position
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")