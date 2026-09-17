# Pages Imports
from pages.home_page import HomePage
from pages.login_page import LogInPage
from pages.students_page import StudentsPage
from pages.staff_page import StaffPage
from pages.service_forms_page import ServiceFormPage
from pages.medical_supplies import MedicalSuppliesPage
from pages.medical_equipment_page import MedicalEquipmentPage
from pages.med_certs_page import MedicalCertificatePage
from pages.clinic_visit_page import ClinicVisitPage
from pages.incidents_page import IncidentsPage

# Imports
from tkinter import ttk
from PIL import Image, ImageTk

# List of all global variables and constants that can be accessed by all python files
PRIMARY_COLOR = "#aecfe4"
PRIMARY_LIGHT = "#d0e3ef"
ACCENT_COLOR = "#46748e"
ACCENT_DARK = "#335e76"
BACKGROUND_COLOR = "#ffffff"
HEADER_COLOR = "#627e8f"
window_width: int = 1280
window_height: int = 720
pages = {
    "HOME": HomePage,
    "LOGIN": LogInPage,
    "STUDENTS": StudentsPage,
    "STAFF": StaffPage,
    "SERVICE_FORMS": ServiceFormPage,
    "MED_SUPPLIES": MedicalSuppliesPage,
    "MED_EQUIP": MedicalEquipmentPage,
    "MED_CERTS": MedicalCertificatePage,
    "VISITS": ClinicVisitPage,
    "INCIDENTS" : IncidentsPage
}

def create_styled_button(parent, photo_path, text, command, style, size=(16, 16)):
    try:
        img = Image.open(photo_path)
        resized_icon = img.resize(size, Image.Resampling.LANCZOS)
        icon = ImageTk.PhotoImage(resized_icon)
    except Exception as e:
        print(f"{e}")

    button = ttk.Button(
        parent,
        text=f" {text}",
        image=icon,
        compound="left",
        style=style,
        command=command,
        cursor="hand2"
    )
    button.image = icon
    return button

def init_ttk_styles():
    styles = ttk.Style()
    styles.theme_use("clam")  # For custom border and background doverrides

    # CHECK BOXES
    styles.configure(
        "checkbox.TCheckbutton",
        background=BACKGROUND_COLOR,
        foreground=ACCENT_COLOR,
        font=("Helvetica", 10),
        indicatorbackground=BACKGROUND_COLOR,
        indicatorforeground=ACCENT_DARK,
        focusthickness=0
    )

    styles.map(
        "checkbox.TCheckbutton",
        background=[("active", BACKGROUND_COLOR)],
        foreground=[("active", ACCENT_DARK)],
        indicatorbackground=[("selected", ACCENT_DARK), ("active", BACKGROUND_COLOR)]
    )

    styles.configure(
        "dropdown.TCombobox",
        fieldbackground=BACKGROUND_COLOR,
        background=ACCENT_DARK,
        foreground=ACCENT_COLOR,
        arrowcolor=BACKGROUND_COLOR,
        bordercolor=ACCENT_COLOR,
        lightcolor=BACKGROUND_COLOR,
        darkcolor=BACKGROUND_COLOR,
        padding=4
    )

    styles.map(
        "dropdown.TCombobox",
        fieldbackground=[("readonly", BACKGROUND_COLOR), ("focus", BACKGROUND_COLOR)],
        foreground=[("readonly", ACCENT_COLOR)],
        selectbackground=[("readonly", ACCENT_DARK)],
        selectforeground=[("readonly", "#FFFFFF")]
    )

    # SCROLL BARS
    styles.configure(
        "SCROLL.TScrollbar",
        troughcolor=PRIMARY_COLOR,
        background=BACKGROUND_COLOR,
        bordercolor=PRIMARY_COLOR,
        arrowcolor=BACKGROUND_COLOR,
        relief="flat",
        borderwidth=0,
        arrowsize=12,
        gripcount=0,
        darkcolor=BACKGROUND_COLOR,
        lightcolor=BACKGROUND_COLOR
    )

    styles.layout(
        "SCROLL.TScrollbar",
        [
            (
                "Scrollbar.trough",
                {
                    "sticky": "ns",
                    "children": [
                        ("Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                    ],
                },
            )
        ],
    )

    styles.map(
        "SCROLL.TScrollbar",
        background=[("active", ACCENT_DARK), ("pressed", PRIMARY_COLOR)],
    )

    # TABLES
    styles.configure(
        "Treeview",
        background=BACKGROUND_COLOR,
        foreground=ACCENT_COLOR,
        borderwidth=2,
        bordercolor=ACCENT_COLOR,
        rowheight=30,
        font=("Helvetica", 11)
    )
    styles.configure(
        "Treeview.Heading",
        background=ACCENT_COLOR,
        foreground=BACKGROUND_COLOR,
        borderwidth=2,
        bordercolor=ACCENT_COLOR,
        rowheight=30,
        font=("Helvetica", 11)
    )
    styles.map(
        "Treeview.Heading",
        background=[
            ("hover", ACCENT_DARK),
            ("active", ACCENT_DARK)
        ]
    )

    # ENTRIES
    styles.configure(
        "ENTRY.TEntry",
        font=("Helvetica", 11),
        bordercolor=PRIMARY_COLOR,
        relief="solid",
        padding=4,
    )

    styles.map(
        "ENTRY.TEntry",
        bordercolor=[
            ("focus", ACCENT_COLOR)
        ]
    )

    # DEFAULT BUTTON
    styles.configure(
        "BTN.TButton",
        foreground=ACCENT_COLOR,
        background=BACKGROUND_COLOR,
        focusthickness=2,
        font=("Helvetica", 11, "bold"),
        padding=(8, 4),
        bordercolor=ACCENT_COLOR,  # Primary border color
        lightcolor=ACCENT_COLOR,  # Prevents 3D top/left highlights
        darkcolor=ACCENT_COLOR,  # Prevents 3D bottom/right shadows
        borderwidth=2,  # Border thickness
        relief="solid",
    )
    styles.map(
        "BTN.TButton",
        background=[
            ("active", ACCENT_DARK),  # Color when clicked
            ("hover", ACCENT_DARK)  # Color on mouse hover
        ],
        foreground=[
            ("active", BACKGROUND_COLOR),  # Color when clicked
            ("hover", BACKGROUND_COLOR)  # Color on mouse hover
        ],
    )

    styles.configure(
        "BTN_RED.TButton",
        foreground="#dc2626",
        background=BACKGROUND_COLOR,
        focusthickness=2,
        font=("Helvetica", 11, "bold"),
        padding=(8, 4),
        bordercolor="#dc2626",  # Primary border color
        lightcolor="#dc2626",  # Prevents 3D top/left highlights
        darkcolor="#dc2626",  # Prevents 3D bottom/right shadows
        borderwidth=2,  # Border thickness
        relief="solid",
    )
    styles.map(
        "BTN_RED.TButton",
        background=[
            ("active", "#dc2626"),
            ("hover", "#dc2626")
        ],
        bordercolor=[
            ("active", "#dc2626"),
            ("hover", "#dc2626")
        ],
        foreground=[
            ("active", BACKGROUND_COLOR),  # Color when clicked
            ("hover", BACKGROUND_COLOR)  # Color on mouse hover
        ],
    )

    # SOLID BUTTON
    styles = ttk.Style()
    styles.configure(
        "BTN_SOLID.TButton",
        foreground=BACKGROUND_COLOR,
        background=ACCENT_COLOR,
        focusthickness=2,
        font=("Helvetica", 11, "bold"),
        padding=(8, 4),
        borderwidth=1,
        relief="flat",
    )
    styles.map(
        "BTN_SOLID.TButton",
        background=[
            ("active", ACCENT_DARK),  # Color when clicked
            ("hover", ACCENT_DARK)  # Color on mouse hover
        ]
    )

    # SIDEBAR BUTTONS
    styles.configure(
        "SIDEBAR_BTN.TButton",
        font=("Helvetica", 15, "bold"),
        foreground=ACCENT_DARK,
        background=PRIMARY_LIGHT,
        anchor="w",
        padding=(15, 10),
        relief="flat"
    )
    styles.map(
        "SIDEBAR_BTN.TButton",
        background=[
            ("active", PRIMARY_COLOR),  # Color when clicked
            ("hover", PRIMARY_COLOR)  # Color on mouse hover
        ]
    )