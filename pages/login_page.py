import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class LogInPage(tk.Frame):
    def __init__(self, parent, controller):
        # TK Init
        tk.Frame.__init__(self, parent)

        # Components
        login_frame = tk.Frame(self, padx=30, pady=30)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_label = tk.Label(login_frame, text="Sign In")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Username
        username_label = tk.Label(login_frame, text="Username")
        username_label.grid(row=1, column=0, sticky="w", pady=(5, 2))

        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 15), ipady=4)

        # Password
        password_label = tk.Label(login_frame, text="Password")
        password_label.grid(row=3, column=0, sticky="w", pady=(5, 2))

        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=4, column=0, sticky="w", columnspan=2, pady=(0, 5), ipady=4)

        # Show Password Checkbox
        self.show_password = tk.BooleanVar()
        show_password_checkbox = tk.Checkbutton(
            login_frame,
            text="Show Password",
            variable=self.show_password,
            command=self.toggle_password_display,
        )
        show_password_checkbox.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Login Button
        login_button = tk.Button(
            login_frame,
            text="Log In",
            command=lambda : self.login_user(controller)
        )
        login_button.grid(row=6, column=0, columnspan=2, sticky="we", ipady=2)

    def toggle_password_display(self):
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def login_user(self, controller):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Temporary Authentication
        if username == "admin" and password == "0000":
            controller.render_page("QR")  # Sends user to home page
            messagebox.showinfo("Login Successful", f"Welcome {username}")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def fetch_authentication_data(self):
        ...

    def verify_password(self, password: str) -> bool:
        ...