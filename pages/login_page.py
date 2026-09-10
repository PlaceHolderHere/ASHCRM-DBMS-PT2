import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import globals

class LogInPage(tk.Frame):
    def __init__(self, parent, controller):
        # TK Init
        tk.Frame.__init__(self, parent)

        # Causes the grid in self to fill up the entire window evenly
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1, uniform="group1")
        self.columnconfigure(1, weight=1, uniform="group1")

        # Left Frame
        left_frame = tk.Frame(self, bg=globals.ACCENT_COLOR)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Left Frame
        left_frame = tk.Frame(self, bg=globals.ACCENT_COLOR)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for left_frame so content centers vertically and horizontally
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        # Inner container frame to hold the elements together
        center_container = tk.Frame(left_frame, bg=globals.ACCENT_COLOR)
        center_container.grid(row=0, column=0)

        # Title
        title_label = tk.Label(
            center_container,
            text="ASHCRM",
            font=("Helvetica", 36, "bold"),
            fg=globals.BACKGROUND_COLOR,
            bg=globals.ACCENT_COLOR
        )
        title_label.pack()

        # Subtitle
        subtitle_label = tk.Label(
            center_container,
            text="Ateneo Senior Highschool Clinic Record Manager",
            font=("Helvetica", 16),
            fg="#E0E0E0",
            bg=globals.ACCENT_COLOR,
        )
        subtitle_label.pack(pady=(0, 16))

        try:
            self.logo_img = tk.PhotoImage(file="Assets/Logo.png")
            self.logo_img = self.logo_img.subsample(7)
            logo_label = tk.Label(
                center_container, image=self.logo_img, bg=globals.ACCENT_COLOR
            )
            logo_label.pack(pady=(0, 15))
        except:
            pass

        # Right Frame
        right_frame = tk.Frame(self, bg=globals.BACKGROUND_COLOR)
        right_frame.grid(row=0, column=1, sticky="nsew")

        login_bg = globals.BACKGROUND_COLOR
        login_frame = tk.Frame(right_frame, padx=40, pady=64, bg=login_bg)
        login_frame.pack(fill="both", padx=64, pady=96, expand=True, anchor="center")

        # Login Widgets
        header = tk.Label(
            login_frame,
            text="Welcome!",
            font=("Helvetica", 18, "bold"),
            bg=login_bg,
            fg=globals.HEADER_COLOR
        )
        header.pack()

        # Subtitle
        subtitle_label = tk.Label(
            login_frame,
            text="Sign in to Continue",
            font=("Helvetica", 9),
            bg=login_bg,
            fg=globals.ACCENT_COLOR
        )
        subtitle_label.pack()

        # Username
        user_label = tk.Label(
            login_frame,
            text="Username",
            font=("Helvetica", 10, "bold"),
            bg=login_bg,
            fg=globals.ACCENT_COLOR,
            anchor="w"
        )
        user_label.pack(fill="x", pady=(12, 0))

        self.username_entry = ttk.Entry(
            login_frame,
            style="ENTRY.TEntry"
        )
        self.username_entry.pack(fill="x", ipady=4)

        # Password
        pass_label = tk.Label(
            login_frame,
            text="Password",
            font=("Helvetica", 10, "bold"),
            bg=login_bg,
            fg=globals.ACCENT_COLOR,
            anchor="w",
        )
        pass_label.pack(fill="x", pady=(12, 0))

        self.password_entry = ttk.Entry(
            login_frame,
            style="ENTRY.TEntry",
            show="•"
        )
        self.password_entry.pack(fill="x", ipady=4)

        # Toggle Password
        checkbox_style = ttk.Style()
        checkbox_style.configure(
            "Custom.TCheckbutton",
            font=("Helvetica", 11),
            background=login_bg,
            foreground=globals.ACCENT_COLOR
        )

        checkbox_style.map(
            "Custom.TCheckbutton",
            background=[("active", login_bg)],
            foreground=[("active", globals.ACCENT_COLOR)]
        )

        self.show_password = tk.BooleanVar()
        show_password_checkbox = ttk.Checkbutton(
            login_frame,
            text="Show Password",
            variable=self.show_password,
            command=self.toggle_password_display,
            style="Custom.TCheckbutton"
        )
        show_password_checkbox.pack(fill="x", pady=(8, 0))

        # Login Button
        login_btn = tk.Button(
            login_frame,
            text="Sign In",
            font=("Helvetica", 11, "bold"),
            bd=0,
            cursor="hand2",
            command=lambda: self.login_user(controller),
            fg = globals.BACKGROUND_COLOR,
            bg = globals.ACCENT_COLOR,
            highlightthickness=2,
            activebackground=globals.ACCENT_DARK,
            activeforeground=globals.BACKGROUND_COLOR
        )
        login_btn.pack(fill="x", ipady=8, pady=(32, 0))

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
            controller.render_page("HOME")  # Sends user to home page
            messagebox.showinfo("Login Successful", f"Welcome {username}")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def fetch_authentication_data(self):
        ...

    def verify_password(self, password: str) -> bool:
        ...