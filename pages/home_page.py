import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Home Page", font=("Arial", 18), bg="#ecf0f1").pack(pady=20)

        patients_button = tk.Button(self, text="Go to Patients Page",
                            command=lambda: controller.render_page("PATIENTS"))
        patients_button.pack()

        students_button = tk.Button(self, text="Go to Students Page",
                            command=lambda: controller.render_page("STUDENTS"))
        students_button.pack()

        scanner_button = tk.Button(self, text="Open QR Code Scanner",
                                    command=lambda: controller.render_page("QR"))
        scanner_button.pack()