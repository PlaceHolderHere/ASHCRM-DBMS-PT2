from dotenv import load_dotenv
import os
import mysql.connector
import tkinter as tk
from tkinter import messagebox

def create_database_connection():
    load_dotenv(".env")

    try:
        connection = mysql.connector.connect(
            host=os.getenv('HOST'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            database=os.getenv('DATABASE')
        )
    except Exception as e:
        print(f"Something went wrong: {e}")
    return connection


class App:
    def __init__(self):
        # Database Variables
        self.connection = create_database_connection()
        self.cursor = self.connection.cursor()

        # Gloabl Variables
        self.window_width: int = 1280
        self.window_height: int = 720
        self.viewWidth = self.window_width / 100
        self.viewHeight = self.window_height / 100
        self._resize_timer = None

        # Tkinter Initialization
        self.root = tk.Tk()
        self.root.title("ASHCRM")
        self.center_window()

        # Run a function when the user:
        self.root.protocol("WM_DELETE_WINDOW", self.close_app) # Closes the window
        self.root.bind("<Configure>", self.on_configure) # Resizing the window

    def start_app(self):
        self.root.mainloop()

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


if __name__ == "__main__":
    app = App()
    app.start_app()