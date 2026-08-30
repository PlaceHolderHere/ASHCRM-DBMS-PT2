import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Home Page", font=("Arial", 18), bg="#ecf0f1").pack(pady=20)

        button1 = tk.Button(self, text="Go to Patient's Page",
                            command=lambda: controller.render_page("PATIENTS"))
        button1.pack()