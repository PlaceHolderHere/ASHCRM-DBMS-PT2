from dotenv import load_dotenv
import os
import mysql.connector
import tkinter as tk


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
        # Gloabl Variables
        self.window_width: int = 1280
        self.window_height: int = 720
        self.viewWidth = self.window_width / 100
        self.viewHeight = self.window_height / 100

        # Tkinter Initialization
        self.root = tk.Tk()
        self.root.title("ASHCRM")
        self.center_window()

    def start_app(self):
        self.root.mainloop()

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
    # Testing Database Connection
    database_connection = create_database_connection()
    cursor = database_connection.cursor()
    cursor.close()
    database_connection.close()

    # App
    app = App()
    app.start_app()