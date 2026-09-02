import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class StudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Students Page", font=("Arial", 18), bg="#ecf0f1").pack(pady=20)

        home_button = tk.Button(self, text="Go to Home Page",
                            command=lambda: controller.render_page("HOME"))
        home_button.pack()
        upload_button = ttk.Button(self, text="Upload a CSV", command=self.get_csv_upload)
        upload_button.pack()

    @staticmethod
    def get_csv_upload() -> str:
        return filedialog.askopenfilename(
            title="Select a Photo to Edit",
            filetypes=[("Photos", "*.csv")],
        )
