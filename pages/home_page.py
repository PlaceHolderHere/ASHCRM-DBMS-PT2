import tkinter as tk
from tkinter import ttk
import globals
from PIL import Image, ImageTk


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self._create_widgets()

    def _create_widgets(self):
        self.container = tk.Frame(self, bg=globals.BACKGROUND_COLOR)
        self.container.pack(expand=True, fill="both")

        # 1. Configure rows and columns directly on self.container
        self.container.rowconfigure(0, weight=1)

        # Adjust weight ratios as needed (e.g., side_bar fixed/smaller weight, content_area larger weight)
        self.container.columnconfigure(0, weight=0)
        self.container.columnconfigure(1, weight=1)

        # SIDE BAR FRAME
        self.side_bar = tk.Frame(self.container, bg=globals.PRIMARY_LIGHT)
        self.side_bar.grid(row=0, column=0, sticky="nsew", ipadx=32, ipady=16)
        self.side_bar.grid_columnconfigure(0, weight=1)

        header = tk.Label(
            self.side_bar,
            bg=globals.PRIMARY_LIGHT,
            text="ASHCRM",
            fg=globals.ACCENT_COLOR,
            font=("Helvetica", 14, "bold"),
            compound="left",
        )
        header.grid(row=0, column=0, padx=32, pady=(16, 0))

        subtitle = tk.Label(
            self.side_bar,
            bg=globals.PRIMARY_LIGHT,
            text="SHS Clinic",
            fg=globals.ACCENT_COLOR,
            font=("Helvetica", 11),
            compound="left",
        )
        subtitle.grid(row=1, column=0, padx=32, pady=(2, 16))

        # Buttons and Icons
        self.icon_students = self._load_icon("assets/icons/students.png")
        self.icon_staff = self._load_icon("assets/icons/Staff.png")
        self.icon_service = self._load_icon("assets/icons/Service_Form.png")
        self.icon_med_supplies = self._load_icon("assets/icons/Med_Supplies.png")
        self.icon_med_equip = self._load_icon("Assets/icons/Logo.png")

        buttons_config = [
            ("Students", "STUDENTS", self.icon_students),
            ("Staff", "STAFF", self.icon_staff),
            ("Medical Service Forms", "SERVICE_FORMS", self.icon_service),
            ("Medical Supplies", "MED_SUPPLIES", self.icon_med_supplies),
            ("Medical Equipment", "MED_EQUIP", self.icon_med_equip)
        ]

        self.sidebar_buttons = {}
        for row_idx, (text, page_key, icon) in enumerate(buttons_config):
            btn = ttk.Button(
                self.side_bar,
                text=f"  {text}",
                image=icon,
                compound="left",
                style="SIDEBAR_BTN.TButton",
                cursor="hand2",
                command=lambda p=page_key: self.controller.render_page(p),
            )
            btn.grid(row=row_idx + 2, column=0, sticky="nsew")
            self.sidebar_buttons[page_key] = btn

        # CONTENT AREA FRAME
        self.content_area = tk.Frame(self.container, bg=globals.BACKGROUND_COLOR)
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Vertical centering using empty weight cushion rows
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=0)
        self.content_area.grid_rowconfigure(2, weight=1)

        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(1, weight=0)

        # 1. Create Treeview Widget with single column
        columns = ("log_content",)
        self.tree = ttk.Treeview(
            self.content_area,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=20
        )

        # 2. Configure Single Column Header & Alignment
        self.tree.heading("log_content", text="Log Entry", anchor="w")
        self.tree.column("log_content", minwidth=200, stretch=True, anchor="w")

        # 3. Attach Vertical Scrollbar
        scrollbar = ttk.Scrollbar(
            self.content_area,
            orient="vertical",
            command=self.tree.yview,
            style="SCROLL.TScrollbar"
        )
        self.tree.configure(yscroll=scrollbar.set)

        # 4. Layout
        self.tree.grid(row=1, column=0, sticky="ew")
        scrollbar.grid(row=1, column=1, sticky="ns")

    def load_logs_to_treeview(self):
        log_lines = []
        try:
            with open("log.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
                log_lines = lines[-25:]
        except Exception as e:
            log_lines = [f"Error reading log file: {e}"]

        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert only log_content string
        for line in reversed(log_lines):
            clean_line = line.strip()
            self.tree.insert("", "end", values=(clean_line,))
    @staticmethod
    def _load_icon(filepath, size=(20, 20)):
        img = Image.open(filepath)
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)