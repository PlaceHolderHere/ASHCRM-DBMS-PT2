import tkinter as tk
from database_connection import create_database_connection, get_env_variables
import globals
from datetime import datetime
from qr_scanner import QRScanner

class App:
    def __init__(self):
        # Database Variables
        env_variables = get_env_variables(".env")
        self.connection = create_database_connection(env_variables)
        self.cursor = self.connection.cursor()
        self.log_file_path = "log.txt"
        self.current_user = None

        # Variables
        self._resize_timer = None
        self.loaded_pages = {}

        # Tkinter Initialization
        self.root = tk.Tk()
        self.root.title("ASHCRM")
        self.root.resizable(False, False)
        self.center_window()
        globals.init_ttk_styles()
        self.qr_scanner = QRScanner(self.root)

        # Full Window Container for all content
        self.content_container = tk.Frame(self.root)
        self.content_container.pack(side="top", fill="both", expand=True)

        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Run a function when the user:
        self.root.protocol("WM_DELETE_WINDOW", self.close_app) # Closes the window

    def add_log(self, message: str) -> None:
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file_path, "a") as file:
            file.write(f"{timestamp} {message}; USER = {self.current_user}\n")

    def start_app(self):
        self.load_pages()
        self.render_page("LOGIN")
        self.root.mainloop()

    def load_pages(self):
        for key, page in globals.pages.items():
            loaded_page = page(self.content_container, self)
            self.loaded_pages[key] = loaded_page
            loaded_page.grid(row=0, column=0, sticky="nsew")

    def render_page(self, page) -> bool:
        fetched_page = self.loaded_pages.get(page)
        if fetched_page is None:
            print(f"Error, {page} page not found")
            return False

        elif page == "HOME":
            fetched_page.load_logs_to_treeview()

        # Start Webcam for QR Scanner
        elif page == "QR":
            fetched_page.update_webcam()
        fetched_page.tkraise()
        return True

    def close_app(self):
        # Close Database Connection
        self.cursor.close()
        self.connection.close()
        self.qr_scanner.stop_camera()
        self.root.destroy()  # close the window

    def center_window(self):
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculating the center of the screen relative to the window size
        x = (screen_width // 2) - (globals.window_width // 2)
        y = (screen_height // 2) - (globals.window_height // 2)

        # Set the dimensions and position
        self.root.geometry(f"{globals.window_width}x{globals.window_height}+{x}+{y}")

    def get_screen_center(self, win_width: int, win_height: int) -> tuple:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculating the center of the screen relative to the window size
        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)

        return x, y