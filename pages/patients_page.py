import tkinter as tk

class PatientsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Patients Page", font=("Arial", 18), bg="#ecf0f1").pack(pady=20)

        button1 = tk.Button(self, text="Go to Home Page",
                            command=lambda: controller.render_page("HOME"))
        button1.pack()