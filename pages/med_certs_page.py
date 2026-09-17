import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import globals
from pages.students_page import StudentDetailWindow
from pages.staff_page import StaffDetailWindow

class MedicalCertificatePage(tk.Frame):
    def __init__(self, parent, controller):
        self.background_color = globals.BACKGROUND_COLOR
        tk.Frame.__init__(self, parent, bg=self.background_color)
        self.cursor = controller.cursor
        self.controller = controller
        self.keyword = ""
        self._TABLE_NAME = "medical_certificates"
        self._create_widgets()

        # Run a function when a user double clicks on a row
        self.tree.bind("<Double-1>", self.open_details_popup)

    def open_details_popup(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        certificate_id = values[0]
        try:
            query = f"SELECT certificate_id, student_id, staff_id, date_approved, event_name FROM {self._TABLE_NAME} WHERE certificate_id = %s"
            self.cursor.execute(query, (certificate_id,))
            row = self.cursor.fetchone()
            if row:
                columns = ["certificate_id", "student_id", "staff_id", "date_approved", "event_name"]
                values_dict = dict(zip(columns, row))
                MedicalCertificateDetailWindow(self.controller, self, values_dict)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch details.\n\n{e}")

    def delete_selected(self):
        rows = self.tree.selection()
        if not rows:
            return

        if not messagebox.askokcancel("Delete Records",
                                      "Are you sure you want to delete all currently selected medical certificates?"):
            return

        selected_ids = [(self.tree.item(r, "values")[0],) for r in rows]
        query = f"DELETE FROM {self._TABLE_NAME} WHERE certificate_id = %s;"

        try:
            self.cursor.executemany(query, selected_ids)
            self.controller.connection.commit()
            self.search_records()
            self.controller.add_log(f"Deleted the following certificate IDs from {self._TABLE_NAME}: {selected_ids}")
            messagebox.showinfo("Deleted Records", "Successfully deleted all selected medical certificates.")
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror("ERROR! Could not Delete",
                                 f"Error! Failed to delete selected records.\n\nError Message: {e}")

    def display_records(self, rows):
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert rows into treeview
        for row_idx, row in enumerate(rows):
            tag = "even" if row_idx % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def search_records(self):
        self.keyword = self.search_entry.get().strip()

        if not self.keyword:
            self.load_records()
            return

        try:
            query = f"""
                SELECT certificate_id, student_id, staff_id, date_approved, event_name
                FROM {self._TABLE_NAME}
                WHERE certificate_id LIKE %s
                   OR student_id LIKE %s
                   OR staff_id LIKE %s
                   OR date_approved LIKE %s
                   OR event_name LIKE %s
                ORDER BY certificate_id
            """

            search_value = f"%{self.keyword}%"
            self.cursor.execute(query, (search_value,) * 5)
            rows = self.cursor.fetchall()

            if len(rows) == 0:
                messagebox.showinfo("No Records Found",
                                    f"Could not find any medical certificates matching {self.keyword}")
                return

            self.display_records(rows)

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Search Failed.\n\n{e}")

    def load_records(self):
        try:
            query = f"""
                SELECT certificate_id, student_id, staff_id, date_approved, event_name
                FROM {self._TABLE_NAME}
                ORDER BY certificate_id
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.display_records(rows)

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not load medical certificates.\n\n{e}")

    def open_create_popup(self):
        CreateMedicalCertificateWindow(self.controller, self)

    def _create_widgets(self):
        # SEARCH FRAME
        search_frame = tk.Frame(self, bg=self.background_color)
        search_frame.pack(fill="x", padx=48, pady=(24, 16))
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(4, weight=1)

        # Home / Back
        home_button = ttk.Button(
            search_frame,
            text="← Back",
            command=lambda: self.controller.render_page("HOME"),
            style="BTN.TButton",
            cursor="hand2"
        )
        home_button.grid(row=0, column=0, sticky="w", pady=(0, 16), padx=4)

        create_btn = globals.create_styled_button(
            search_frame,
            photo_path="Assets/Icons/Create.png",
            text="Add Certificate",
            command=self.open_create_popup,
            style="BTN.TButton"
        )
        create_btn.grid(row=0, column=4, sticky="e")

        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=("Helvetica", 14),
            foreground=globals.ACCENT_COLOR,
            background=self.background_color
        )
        search_label.grid(row=1, column=0, sticky="e", padx=(0, 4))

        self.search_entry = ttk.Entry(search_frame, style="ENTRY.TEntry")
        self.search_entry.grid(row=1, column=1, padx=(0, 12), sticky="ew")

        search_btn = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_records,
            style="BTN.TButton",
            cursor="hand2"
        )
        search_btn.grid(row=1, column=2, padx=(0, 6))

        show_all_btn = ttk.Button(
            search_frame,
            text="Show All",
            command=self.load_records,
            style="BTN.TButton",
            cursor="hand2"
        )
        show_all_btn.grid(row=1, column=3)

        delete_btn = globals.create_styled_button(
            search_frame,
            photo_path="Assets/Icons/Delete.png",
            text="Delete Selected",
            command=self.delete_selected,
            style="BTN_RED.TButton"
        )
        delete_btn.grid(row=1, column=4, sticky="e")

        # Table Frame
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=48, pady=(24, 32))

        columns = ("certificate_id", "student_id", "staff_id", "date_approved", "event_name")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        self.tree.tag_configure("odd", background=globals.PRIMARY_LIGHT)
        self.tree.tag_configure("even", background=globals.BACKGROUND_COLOR)

        headings = {
            "certificate_id": "Cert ID",
            "student_id": "Student ID",
            "staff_id": "Staff ID",
            "date_approved": "Date Approved",
            "event_name": "Event Name"
        }

        widths = {
            "certificate_id": 80,
            "student_id": 100,
            "staff_id": 100,
            "date_approved": 120,
            "event_name": 300
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="SCROLL.TScrollbar")
        horizontal_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview, style="SCROLL.TScrollbar")

        self.tree.configure(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

        horizontal_scrollbar.pack(side="bottom", fill="x")
        vertical_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="top", fill="both", expand=True)


class MedicalCertificateDetailWindow(tk.Toplevel):
    month_map = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }
    month_map_rev = {v: k for k, v in month_map.items()}

    def __init__(self, controller, parent, certificate_id_or_data):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent

        if isinstance(certificate_id_or_data, dict):
            self.cert_data = certificate_id_or_data
            self.certificate_id = certificate_id_or_data.get("certificate_id")
        else:
            self.certificate_id = certificate_id_or_data
            self.cert_data = {}

        self.fetch_data()

        self.title("Medical Certificate Details")
        self.geometry(f"{globals.window_width // 2}x{int(globals.window_height * 0.55)}")
        self.resizable(False, False)

        x, y = controller.get_screen_center(globals.window_width // 2, int(globals.window_height * 0.55))
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._create_widgets()

    def fetch_data(self):
        if not self.certificate_id:
            return

        query = """
            SELECT certificate_id, student_id, staff_id, date_approved, event_name
            FROM medical_certificates
            WHERE certificate_id = %s
        """
        try:
            self.controller.cursor.execute(query, (self.certificate_id,))
            result = self.controller.cursor.fetchone()

            if result:
                if isinstance(result, dict):
                    self.cert_data.update(result)
                else:
                    self.cert_data.update({
                        "certificate_id": result[0],
                        "student_id": result[1],
                        "staff_id": result[2],
                        "date_approved": result[3],
                        "event_name": result[4]
                    })
            else:
                messagebox.showerror("Error", f"Certificate ID {self.certificate_id} not found.")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch certificate details.\n\n{e}")

    def view_student_details(self):
        student_id = self.cert_data.get("student_id")
        if not student_id:
            messagebox.showinfo("No Student ID", "No Student ID attached to this certificate.")
            return

        try:
            StudentDetailWindow(self.controller, self, student_id, False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch student details.\n\n{e}")

    def view_staff_details(self):
        staff_id = self.cert_data.get("staff_id")
        if not staff_id:
            messagebox.showinfo("No Staff ID", "No Staff ID attached to this certificate.")
            return

        try:
            StaffDetailWindow(self.controller, self, staff_id, False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch staff details.\n\n{e}")

    def on_close(self):
        self.destroy()

    def _create_widgets(self):
        canvas = tk.Canvas(self, bg=globals.BACKGROUND_COLOR, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview, style="SCROLL.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        container = tk.Frame(canvas, bg=globals.BACKGROUND_COLOR)
        canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")

        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        def _on_mousewheel(event):
            try:
                # Linux (Button-4 / Button-5)
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
                # Windows & macOS (MouseWheel)
                elif event.delta:
                    direction = -1 if event.delta > 0 else 1
                    canvas.yview_scroll(direction, "units")
            except tk.TclError:
                # Prevents crashes if canvas is destroyed while scrolling
                pass

        def _unbind_mousewheel(event=None):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        def _bind_mousewheel(event=None):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        # Bind mouse wheel only when hovering over the window, and cleanup on exit/destroy
        self.bind("<Enter>", _bind_mousewheel)
        self.bind("<Leave>", _unbind_mousewheel)
        self.bind("<Destroy>", _unbind_mousewheel)

        tk.Label(
            container,
            text="MEDICAL CERTIFICATE DETAILS",
            font=("Arial", 20, "bold"),
            foreground=globals.ACCENT_COLOR,
            background=globals.BACKGROUND_COLOR
        ).pack(pady=(15, 5))

        info_frame = tk.Frame(container, padx=20, pady=10, bg=globals.BACKGROUND_COLOR)
        info_frame.pack(fill="both", expand=True)

        self.entry_widgets = {}

        raw_date = str(self.cert_data.get("date_approved", ""))
        date_parts = raw_date.split("-") if "-" in raw_date else ["2026", "01", "01"]
        init_year = date_parts[0] if len(date_parts) > 0 else "2026"
        init_month_num = date_parts[1] if len(date_parts) > 1 else "01"
        init_day = date_parts[2] if len(date_parts) > 2 else "01"
        init_month_name = self.month_map_rev.get(init_month_num, "January")

        fields = [
            ("certificate_id", "Certificate ID"),
            ("student_id", "Student ID"),
            ("staff_id", "Staff ID"),
            ("date_approved", "Date Approved"),
            ("event_name", "Event Name")
        ]

        month_names = list(self.month_map.keys())
        days = [f"{i:02d}" for i in range(1, 32)]
        years = [str(i) for i in range(2026, 2031)]

        num_of_cols = 2
        for index, (field_key, label_text) in enumerate(fields):
            column = index % num_of_cols
            row = index // num_of_cols

            tk.Label(
                info_frame,
                text=label_text,
                font=("Helvetica", 11, "bold"),
                foreground=globals.ACCENT_COLOR,
                background=globals.BACKGROUND_COLOR
            ).grid(row=row, column=column * num_of_cols, sticky="w", pady=8)

            if field_key == "certificate_id":
                tk.Label(
                    info_frame,
                    text=self.cert_data.get("certificate_id"),
                    font=("Helvetica", 11, "bold"),
                    background=globals.BACKGROUND_COLOR
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif field_key == "student_id":
                student_id = self.cert_data.get("student_id", "N/A")
                ttk.Button(
                    info_frame,
                    text=f"View Student ({student_id})",
                    style="BTN.TButton",
                    command=self.view_student_details,
                    cursor="hand2"
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif field_key == "staff_id":
                staff_id = self.cert_data.get("staff_id", "N/A")
                ttk.Button(
                    info_frame,
                    text=f"View Staff ({staff_id})",
                    style="BTN.TButton",
                    command=self.view_staff_details,
                    cursor="hand2"
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif field_key == "date_approved":
                date_frame = tk.Frame(info_frame, bg=globals.BACKGROUND_COLOR)
                date_frame.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

                self.apt_month = tk.StringVar(value=init_month_name)
                self.apt_day = tk.StringVar(value=init_day)
                self.apt_year = tk.StringVar(value=init_year)

                ttk.Combobox(date_frame, textvariable=self.apt_month, values=month_names, state="readonly", width=10, style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                ttk.Combobox(date_frame, textvariable=self.apt_day, values=days, state="readonly", width=3, style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                ttk.Combobox(date_frame, textvariable=self.apt_year, values=years, state="readonly", width=6, style="dropdown.TCombobox").pack(side="left")

            else:
                entry = ttk.Entry(info_frame, style="ENTRY.TEntry")
                entry.insert(0, str(self.cert_data.get(field_key, "")))
                entry.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))
                self.entry_widgets[field_key] = entry

class CreateMedicalCertificateWindow(tk.Toplevel):
    month_map = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }

    def __init__(self, controller, parent):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent

        self.title("Create Medical Certificate")
        self.geometry(f"{globals.window_width // 2}x{int(globals.window_height * 0.55)}")
        self.resizable(False, False)

        x, y = controller.get_screen_center(globals.window_width // 2, int(globals.window_height * 0.55))
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)
        self.grab_set()

        self._create_widgets()

    def save_record(self):
        student_id = self.student_id_entry.get().strip()
        staff_id = self.staff_id_entry.get().strip()
        event_name = self.event_name_entry.get().strip()

        month_num = self.month_map.get(self.apt_month.get(), "01")
        day_num = self.apt_day.get()
        year_num = self.apt_year.get()
        date_approved = f"{year_num}-{month_num}-{day_num}"

        if not student_id or not staff_id or not event_name:
            messagebox.showerror("Validation Error", "Please fill out all required fields.")
            return

        query = """
            INSERT INTO medical_certificates (student_id, staff_id, date_approved, event_name)
            VALUES (%s, %s, %s, %s)
        """

        try:
            self.controller.cursor.execute(query, (student_id, staff_id, date_approved, event_name))
            self.controller.connection.commit()
            self.controller.add_log(
                f"Created medical certificate for Student ID: {student_id} by Staff ID: {staff_id}")
            messagebox.showinfo("Success", "Medical certificate successfully created!")

            # Refresh treeview in parent page and close modal
            self.parent.load_records()
            self.destroy()
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror("Database Error", f"Failed to save medical certificate.\n\n{e}")

    def _create_widgets(self):
        container = tk.Frame(self, bg=globals.BACKGROUND_COLOR, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="CREATE MEDICAL CERTIFICATE",
            font=("Arial", 18, "bold"),
            foreground=globals.ACCENT_COLOR,
            background=globals.BACKGROUND_COLOR
        ).pack(pady=(0, 20))

        form_frame = tk.Frame(container, bg=globals.BACKGROUND_COLOR)
        form_frame.pack(fill="both", expand=True)

        # Student ID
        tk.Label(
            form_frame, text="Student ID:", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=0, column=0, sticky="w", pady=10)

        self.student_id_entry = ttk.Entry(form_frame, style="ENTRY.TEntry")
        self.student_id_entry.grid(row=0, column=1, sticky="ew", pady=10, padx=(10, 0))

        # Staff ID
        tk.Label(
            form_frame, text="Staff ID:", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=1, column=0, sticky="w", pady=10)

        self.staff_id_entry = ttk.Entry(form_frame, style="ENTRY.TEntry")
        self.staff_id_entry.grid(row=1, column=1, sticky="ew", pady=10, padx=(10, 0))

        # Date Approved
        tk.Label(
            form_frame, text="Date Approved:", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=2, column=0, sticky="w", pady=10)

        date_frame = tk.Frame(form_frame, bg=globals.BACKGROUND_COLOR)
        date_frame.grid(row=2, column=1, sticky="w", pady=10, padx=(10, 0))

        month_names = list(self.month_map.keys())
        days = [f"{i:02d}" for i in range(1, 32)]
        years = [str(i) for i in range(2026, 2031)]

        self.apt_month = tk.StringVar(value="January")
        self.apt_day = tk.StringVar(value="01")
        self.apt_year = tk.StringVar(value="2026")

        ttk.Combobox(date_frame, textvariable=self.apt_month, values=month_names, state="readonly", width=10,
                     style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
        ttk.Combobox(date_frame, textvariable=self.apt_day, values=days, state="readonly", width=3,
                     style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
        ttk.Combobox(date_frame, textvariable=self.apt_year, values=years, state="readonly", width=6,
                     style="dropdown.TCombobox").pack(side="left")

        # Event Name
        tk.Label(
            form_frame, text="Event Name:", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=3, column=0, sticky="w", pady=10)

        self.event_name_entry = ttk.Entry(form_frame, style="ENTRY.TEntry")
        self.event_name_entry.grid(row=3, column=1, sticky="ew", pady=10, padx=(10, 0))

        form_frame.columnconfigure(1, weight=1)

        # Action Buttons
        btn_frame = tk.Frame(container, bg=globals.BACKGROUND_COLOR)
        btn_frame.pack(fill="x", pady=(20, 0))

        save_btn = ttk.Button(
            btn_frame,
            text="Save Record",
            command=self.save_record,
            style="BTN.TButton",
            cursor="hand2"
        )
        save_btn.pack(side="right", padx=(6, 0))

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            style="BTN_RED.TButton",
            cursor="hand2"
        )
        cancel_btn.pack(side="right")