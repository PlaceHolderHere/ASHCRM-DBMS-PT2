import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import globals
from pages.students_page import StudentDetailWindow
from pages.staff_page import StaffDetailWindow

class ServiceFormPage(tk.Frame):
    def __init__(self, parent, controller):
        self.background_color = globals.BACKGROUND_COLOR
        tk.Frame.__init__(self, parent, bg=self.background_color)
        self.cursor = controller.cursor
        self.controller = controller
        self.keyword = ""
        self._TABLE_NAME = "medical_service_form"
        self._create_widgets()

        # Run a function when a user double clicks on a row
        self.tree.bind("<Double-1>", self.open_details_popup)

    def open_details_popup(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        # Fetch full row data by ID to ensure student_id and staff_id are included
        service_form_id = values[0]
        try:
            query = f"SELECT service_form_id, student_id, staff_id, time_start, time_end, date, purpose FROM {self._TABLE_NAME} WHERE service_form_id = %s"
            self.cursor.execute(query, (service_form_id,))
            row = self.cursor.fetchone()
            if row:
                columns = ["service_form_id", "student_id", "staff_id", "time_start", "time_end", "date", "purpose"]
                values_dict = dict(zip(columns, row))
                ServiceFormDetailWindow(self.controller, self, values_dict)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch details.\n\n{e}")

    def delete_selected(self):
        rows = self.tree.selection()
        if not rows:
            return

        if not messagebox.askokcancel("Delete Records",
                                      "Are you sure you want to delete all of the currently selected service forms?"):
            return

        selected_ids = []
        for row_id in rows:
            row = self.tree.item(row_id, "values")
            selected_ids.append((row[0],))

        query = f"DELETE FROM {self._TABLE_NAME} WHERE service_form_id = %s;"
        try:
            self.cursor.executemany(query, selected_ids)
            self.controller.connection.commit()
            self.search_records()
            self.controller.add_log(f"Deleted the following service form IDs from {self._TABLE_NAME}: {selected_ids}")
            messagebox.showinfo("Deleted Records", "Successfully Deleted all Selected Service Forms")
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror("ERROR! Could not Delete",
                                 f"Error! Failed to delete selected records. \n\nError Message:{e}")

    # DISPLAY RECORDS
    def display_records(self, rows):
        # CLEAR EXISTING ROWS
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert Rows into treeview
        for row_idx, row in enumerate(rows):
            tag = "even" if row_idx % 2 == 0 else "odd"

            self.tree.insert(
                "",
                "end",
                values=row,
                tags=(tag,)
            )

    # SEARCH
    def search_records(self):
        self.keyword = self.search_entry.get().strip()

        if not self.keyword:
            self.load_records()
            return

        try:
            query = f"""
                SELECT
                    service_form_id,
                    time_start,
                    time_end,
                    date,
                    purpose
                FROM {self._TABLE_NAME}
                WHERE service_form_id LIKE %s
                    OR student_id LIKE %s
                    OR staff_id LIKE %s
                    OR date LIKE %s
                    OR purpose LIKE %s
                ORDER BY service_form_id
            """

            search_value = f"%{self.keyword}%"

            self.cursor.execute(
                query,
                (
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value
                )
            )

            rows = self.cursor.fetchall()

            if len(rows) == 0:
                messagebox.showinfo("No Records Found",
                                    f"Could not find any medical service forms matching {self.keyword}")
                return

            self.display_records(rows)

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                f"Search Failed. \n\n {e}"
            )

    # READ/SELECT
    def load_records(self):
        try:
            query = f"""
                SELECT
                    service_form_id,
                    time_start,
                    time_end,
                    date,
                    purpose
                FROM {self._TABLE_NAME}
                ORDER BY service_form_id
            """

            self.cursor.execute(query)

            rows = self.cursor.fetchall()

            self.display_records(rows)

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                f"Could not Load Medical Service Forms. \n\n{e}"
            )

    def open_create_service_form_popup(self):
        create_popup = CreateServiceFormPopUp(self.controller, self)
        self.wait_window(create_popup)

    def _create_widgets(self):
        # SEARCH
        search_frame = tk.Frame(self, bg=self.background_color)
        search_frame.pack(
            fill="x",
            padx=48,
            pady=(24, 16)
        )
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(4, weight=1)

        # Home
        home_button = ttk.Button(
            search_frame,
            text="← Back",
            command=lambda: self.controller.render_page("HOME"),
            style="BTN.TButton",
            cursor="hand2")
        home_button.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 16),
            padx=4
        )

        create_btn = globals.create_styled_button(
            search_frame,
            photo_path="Assets/Icons/Create.png",
            text="Add Service Form",
            command=self.open_create_service_form_popup,
            style="BTN.TButton"
        )
        create_btn.grid(
            row=0,
            column=4,
            sticky="e"
        )

        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=("Helvetica", 14),
            foreground=globals.ACCENT_COLOR,
            background=self.background_color
        )
        search_label.grid(
            row=1,
            column=0,
            sticky="e",
            padx=(0, 4)
        )

        self.search_entry = ttk.Entry(
            search_frame,
            style="ENTRY.TEntry"
        )
        self.search_entry.grid(
            row=1,
            column=1,
            padx=(0, 12),
            sticky="ew"
        )

        search_btn = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_records,
            style="BTN.TButton",
            cursor="hand2"
        )
        search_btn.grid(
            row=1,
            column=2,
            padx=(0, 6)
        )

        # Show All Button
        show_all_btn = ttk.Button(
            search_frame,
            text="Show All",
            command=self.load_records,
            style="BTN.TButton",
            cursor="hand2"
        )
        show_all_btn.grid(
            row=1,
            column=3
        )

        delete_btn = globals.create_styled_button(
            search_frame,
            photo_path="Assets/Icons/Delete.png",
            text="Delete Selected",
            command=self.delete_selected,
            style="BTN_RED.TButton"
        )
        delete_btn.grid(
            row=1,
            column=4,
            sticky="e"
        )

        # Search Results Table
        table_frame = tk.Frame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=48,
            pady=(24, 32)
        )

        columns = (
            "service_form_id",
            "time_start",
            "time_end",
            "date",
            "purpose"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Treeview"
        )
        self.tree.tag_configure("odd", background=globals.PRIMARY_LIGHT)
        self.tree.tag_configure("even", background=globals.BACKGROUND_COLOR)

        # COLUMN HEADINGS
        headings = {
            "service_form_id": "Form ID",
            "time_start": "Start Time",
            "time_end": "End Time",
            "date": "Date",
            "purpose": "Purpose"
        }

        # COLUMN WIDTHS
        widths = {
            "service_form_id": 80,
            "time_start": 100,
            "time_end": 100,
            "date": 120,
            "purpose": 300
        }

        for column in columns:
            self.tree.heading(
                column,
                text=headings[column]
            )
            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        # SCROLLBARS
        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
            style="SCROLL.TScrollbar"
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
            style="SCROLL.TScrollbar"
        )

        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )

        horizontal_scrollbar.pack(
            side="bottom",
            fill="x"
        )

        vertical_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.pack(
            side="top",
            fill="both",
            expand=True
        )


class ServiceFormDetailWindow(tk.Toplevel):
    month_map = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }
    month_map_rev = {v: k for k, v in month_map.items()}

    def __init__(self, controller, parent, service_form_data):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent
        self.service_form_data = service_form_data

        # Window Configuration
        self.title("Medical Service Form Details")
        self.geometry(f"{globals.window_width // 2}x{int(globals.window_height * 0.7)}")
        self.resizable(False, False)

        x, y = controller.get_screen_center(globals.window_width // 2, int(globals.window_height * 0.7))
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._create_widgets()

    def view_student_details(self):
        student_id = self.service_form_data.get("student_id")
        if not student_id:
            messagebox.showinfo("No Student ID", "No Student ID attached to this form.")
            return

        try:
            StudentDetailWindow(self.controller, self, student_id, False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch student details.\n\n{e}")

    def view_staff_details(self):
        staff_id = self.service_form_data.get("staff_id")
        if not staff_id:
            messagebox.showinfo("No Staff ID", "No Staff ID attached to this form.")
            return

        try:
            StaffDetailWindow(self.controller, self, staff_id, False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch staff details.\n\n{e}")

    def _create_widgets(self):
        canvas = tk.Canvas(
            self,
            bg=globals.BACKGROUND_COLOR,
            highlightthickness=0,
            bd=0
        )
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=canvas.yview,
            style="SCROLL.TScrollbar"
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        container = tk.Frame(canvas, bg=globals.BACKGROUND_COLOR)
        canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")

        container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width)
        )

        # TITLE
        tk.Label(
            container,
            text="SERVICE FORM DETAILS",
            font=("Arial", 20, "bold"),
            foreground=globals.ACCENT_COLOR,
            background=globals.BACKGROUND_COLOR
        ).pack(pady=(15, 5))

        info_frame = tk.Frame(container, padx=20, pady=10, bg=globals.BACKGROUND_COLOR)
        info_frame.pack(fill="both", expand=True)

        self.entry_widgets = {}

        # Parse date if available (YYYY-MM-DD)
        raw_date = str(self.service_form_data.get("date", ""))
        date_parts = raw_date.split("-") if "-" in raw_date else ["2026", "01", "01"]
        init_year = date_parts[0] if len(date_parts) > 0 else "2026"
        init_month_num = date_parts[1] if len(date_parts) > 1 else "01"
        init_day = date_parts[2] if len(date_parts) > 2 else "01"
        init_month_name = self.month_map_rev.get(init_month_num, "January")

        # Parse time_start & time_end (HH:MM:SS)
        raw_start = str(self.service_form_data.get("time_start", ""))
        start_parts = raw_start.split(":") if ":" in raw_start else ["08", "00"]

        raw_end = str(self.service_form_data.get("time_end", ""))
        end_parts = raw_end.split(":") if ":" in raw_end else ["09", "00"]

        fields = [
            ("service_form_id", "Service Form ID"),
            ("student_id", "Student ID"),
            ("staff_id", "Staff ID"),
            ("date", "Date"),
            ("time_start", "Time Start"),
            ("time_end", "Time End"),
            ("purpose", "Purpose")
        ]

        month_names = list(self.month_map.keys())
        days = [f"{i:02d}" for i in range(1, 32)]
        years = [str(i) for i in range(2026, 2031)]
        hours = [f"{i:02d}" for i in range(0, 24)]
        minutes = [f"{i:02d}" for i in range(0, 60, 5)]

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

            if field_key == "service_form_id":
                tk.Label(
                    info_frame,
                    text=self.service_form_data.get("service_form_id"),
                    font=("Helvetica", 11, "bold"),
                    background=globals.BACKGROUND_COLOR
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif field_key == "student_id":
                student_id = self.service_form_data.get("student_id", "N/A")
                ttk.Button(
                    info_frame,
                    text=f"View Student ({student_id})",
                    style="BTN.TButton",
                    command=self.view_student_details,
                    cursor="hand2"
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif field_key == "staff_id":
                staff_id = self.service_form_data.get("staff_id", "N/A")
                ttk.Button(
                    info_frame,
                    text=f"View Staff ({staff_id})",
                    style="BTN.TButton",
                    command=self.view_staff_details,
                    cursor="hand2"
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif field_key == "date":
                date_frame = tk.Frame(info_frame, bg=globals.BACKGROUND_COLOR)
                date_frame.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

                self.apt_month = tk.StringVar(value=init_month_name)
                self.apt_day = tk.StringVar(value=init_day)
                self.apt_year = tk.StringVar(value=init_year)

                ttk.Combobox(date_frame, textvariable=self.apt_month, values=month_names, state="readonly", width=10,
                             style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                ttk.Combobox(date_frame, textvariable=self.apt_day, values=days, state="readonly", width=3,
                             style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                ttk.Combobox(date_frame, textvariable=self.apt_year, values=years, state="readonly", width=6,
                             style="dropdown.TCombobox").pack(side="left")

            elif field_key in ["time_start", "time_end"]:
                time_frame = tk.Frame(info_frame, bg=globals.BACKGROUND_COLOR)
                time_frame.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

                if field_key == "time_start":
                    self.start_hour = tk.StringVar(value=start_parts[0])
                    self.start_min = tk.StringVar(value=start_parts[1])
                    h_var, m_var = self.start_hour, self.start_min
                else:
                    self.end_hour = tk.StringVar(value=end_parts[0])
                    self.end_min = tk.StringVar(value=end_parts[1])
                    h_var, m_var = self.end_hour, self.end_min

                ttk.Combobox(time_frame, textvariable=h_var, values=hours, state="readonly", width=4,
                             style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                tk.Label(time_frame, text=":", bg=globals.BACKGROUND_COLOR, font=("Helvetica", 11, "bold")).pack(
                    side="left")
                ttk.Combobox(time_frame, textvariable=m_var, values=minutes, state="readonly", width=4,
                             style="dropdown.TCombobox").pack(side="left")

            else:
                entry = ttk.Entry(info_frame, style="ENTRY.TEntry")
                entry.insert(0, str(self.service_form_data.get(field_key, "")))
                entry.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))
                self.entry_widgets[field_key] = entry

        # BUTTONS
        ttk.Button(container, text="Save", style="BTN_SOLID.TButton", command=self.save_update).pack(pady=16,
                                                                                                     side="right",
                                                                                                     padx=(8, 32))
        ttk.Button(container, text="Cancel", style="BTN.TButton", command=self.on_close).pack(pady=16, side="right",
                                                                                              padx=8)

    def on_close(self):
        if not self.is_data_changed():
            self.destroy()
            return

        if messagebox.askokcancel("Unsaved Changes",
                                  "You have unsaved changes, are you sure you want to close this window?"):
            self.destroy()

    def is_data_changed(self) -> bool:
        entry_data = self.get_entry_data()
        for key in ["purpose", "date", "time_start", "time_end"]:
            if str(self.service_form_data.get(key, "")) != str(entry_data.get(key, "")):
                return True
        return False

    def get_entry_data(self) -> dict:
        output = {key: widget.get() for key, widget in self.entry_widgets.items()}
        output["service_form_id"] = self.service_form_data.get("service_form_id")
        output["student_id"] = self.service_form_data.get("student_id")
        output["staff_id"] = self.service_form_data.get("staff_id")

        month_num = self.month_map.get(self.apt_month.get(), "01")
        output["date"] = f"{self.apt_year.get()}-{month_num}-{self.apt_day.get()}"
        output["time_start"] = f"{self.start_hour.get()}:{self.start_min.get()}:00"
        output["time_end"] = f"{self.end_hour.get()}:{self.end_min.get()}:00"
        return output

    def save_update(self):
        if not self.is_data_changed():
            self.destroy()
            return

        form_data = self.get_entry_data()
        if form_data.get("service_form_id") is None:
            messagebox.showerror("ERROR! Invalid Form ID", "Error! Invalid Service Form ID.")
            return

        query = """
            UPDATE medical_service_form
            SET
                student_id = %(student_id)s,
                staff_id = %(staff_id)s,
                time_start = %(time_start)s,
                time_end = %(time_end)s,
                date = %(date)s,
                purpose = %(purpose)s
            WHERE 
                service_form_id = %(service_form_id)s
        """
        try:
            self.controller.cursor.execute(query, form_data)
            self.controller.connection.commit()

            log_msg = f"Updated Medical Service Form (ID: {form_data.get('service_form_id')})."
            self.controller.add_log(log_msg)

            messagebox.showinfo("Updated Successfully!", "Updated medical service form record successfully!")
            self.parent.search_records()
            self.destroy()
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror("ERROR! Could not Update Record",
                                 f"An error occurred while trying to update service form ID {form_data.get('service_form_id')}\n\nError Message: {e}")

class CreateServiceFormPopUp(tk.Toplevel):
    month_map = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12",
    }

    def __init__(self, controller, parent):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent

        # Window Configuration
        self.title("Add Medical Service Form")
        self.geometry(
            f"{int(globals.window_width // 1.5)}x{int(globals.window_height // 1.5)}"
        )
        self.resizable(False, False)

        x, y = controller.get_screen_center(
            int(globals.window_width // 1.5), int(globals.window_height // 1.5)
        )
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close_attempt)
        self._create_widgets()

    def _create_widgets(self):
        canvas = tk.Canvas(
            self,
            bg=globals.BACKGROUND_COLOR,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=canvas.yview,
            style="SCROLL.TScrollbar",
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        container = tk.Frame(canvas, bg=globals.BACKGROUND_COLOR)
        canvas_window = canvas.create_window(
            (0, 0), window=container, anchor="nw"
        )

        container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width),
        )

        # TITLE
        title = tk.Label(
            container,
            text="ADD MEDICAL SERVICE FORM",
            font=("Arial", 20, "bold"),
            background=globals.BACKGROUND_COLOR,
            foreground=globals.ACCENT_COLOR,
        )
        title.pack(pady=(15, 5))

        # FORM
        form_frame = tk.LabelFrame(
            container,
            text="Service Form Details",
            padx=16,
            pady=16,
            background=globals.BACKGROUND_COLOR,
        )
        form_frame.pack(fill="x", padx=20, pady=4)

        month_names = list(self.month_map.keys())
        days = [f"{i:02d}" for i in range(1, 32)]
        years = [str(i) for i in range(2026, 2031)]
        hours = [f"{i:02d}" for i in range(0, 24)]
        minutes = [f"{i:02d}" for i in range(0, 60, 5)]

        form_entries = [
            "STUDENT ID",
            "APPROVING STAFF ID",
            "INVOLVED STAFF IDS",
            "MEDICAL EQUIPMENT IDS",
            "MEDICAL SUPPLIES IDS",
            "DATE",
            "TIME START",
            "TIME END",
            "PURPOSE",
        ]

        self.entry_widgets = {}
        num_of_cols = 2

        for index, label in enumerate(form_entries):
            column = index % num_of_cols
            row = index // num_of_cols

            tk.Label(
                form_frame,
                text=label.title(),
                font=("Helvetica", 11, "bold"),
                foreground=globals.ACCENT_COLOR,
                background=globals.BACKGROUND_COLOR,
            ).grid(
                row=row,
                column=column * num_of_cols,
                sticky="w",
                pady=8,
            )

            if label == "DATE":
                date_frame = tk.Frame(form_frame, bg=globals.BACKGROUND_COLOR)
                date_frame.grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16),
                )

                self.apt_month = tk.StringVar(value="January")
                self.apt_day = tk.StringVar(value="01")
                self.apt_year = tk.StringVar(value="2026")

                ttk.Combobox(
                    date_frame,
                    textvariable=self.apt_month,
                    values=month_names,
                    state="readonly",
                    width=10,
                    style="dropdown.TCombobox",
                ).pack(side="left", padx=(0, 2))
                ttk.Combobox(
                    date_frame,
                    textvariable=self.apt_day,
                    values=days,
                    state="readonly",
                    width=3,
                    style="dropdown.TCombobox",
                ).pack(side="left", padx=(0, 2))
                ttk.Combobox(
                    date_frame,
                    textvariable=self.apt_year,
                    values=years,
                    state="readonly",
                    width=6,
                    style="dropdown.TCombobox",
                ).pack(side="left")

            elif label in ["TIME START", "TIME END"]:
                time_frame = tk.Frame(form_frame, bg=globals.BACKGROUND_COLOR)
                time_frame.grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16),
                )

                if label == "TIME START":
                    self.start_hour = tk.StringVar(value="08")
                    self.start_min = tk.StringVar(value="00")
                    h_var, m_var = self.start_hour, self.start_min
                else:
                    self.end_hour = tk.StringVar(value="09")
                    self.end_min = tk.StringVar(value="00")
                    h_var, m_var = self.end_hour, self.end_min

                ttk.Combobox(
                    time_frame,
                    textvariable=h_var,
                    values=hours,
                    state="readonly",
                    width=4,
                    style="dropdown.TCombobox",
                ).pack(side="left", padx=(0, 2))
                tk.Label(
                    time_frame,
                    text=":",
                    bg=globals.BACKGROUND_COLOR,
                    font=("Helvetica", 11, "bold"),
                ).pack(side="left")
                ttk.Combobox(
                    time_frame,
                    textvariable=m_var,
                    values=minutes,
                    state="readonly",
                    width=4,
                    style="dropdown.TCombobox",
                ).pack(side="left")

            else:
                self.entry_widgets[label] = ttk.Entry(
                    form_frame, style="ENTRY.TEntry"
                )
                self.entry_widgets[label].grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16),
                )

        # BUTTONS
        button_frame = tk.Frame(container, bg=globals.BACKGROUND_COLOR)
        button_frame.pack(pady=10)

        # CANCEL
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_close_attempt,
            style="BTN.TButton",
            cursor="hand2",
        ).grid(row=0, column=0, padx=5)

        # SUBMIT
        ttk.Button(
            button_frame,
            text="Submit",
            command=self.add_service_form_record,
            style="BTN.TButton",
            cursor="hand2",
        ).grid(row=0, column=1, padx=5)

        # CLEAR FIELDS
        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_fields,
            style="BTN_RED.TButton",
            cursor="hand2",
        ).grid(row=0, column=3, padx=5)

    def add_service_form_record(self):
        if self.is_form_empty():
            messagebox.showerror(
                "Form is Empty!",
                "Error! Form is empty, please fill in the form.",
            )
            return

        data = self.get_form_data()

        query_params = {
            "STUDENT ID": data["STUDENT ID"],
            "APPROVING STAFF ID": data["APPROVING STAFF ID"],
            "TIME START": data["TIME START"],
            "TIME END": data["TIME END"],
            "DATE": data["DATE"],
            "PURPOSE": data["PURPOSE"],
        }

        query = """
                INSERT INTO medical_service_form (
                    student_id,
                    staff_id,
                    time_start,
                    time_end,
                    date,
                    purpose
                )
                VALUES (
                    %(STUDENT ID)s,
                    %(APPROVING STAFF ID)s,
                    %(TIME START)s,
                    %(TIME END)s,
                    %(DATE)s,
                    %(PURPOSE)s
                );
                """

        med_supplies_query = """
            INSERT INTO medical_supplies_used_service_form (
                    medical_item_id,
                    service_form_id,
                    quantity
                )
                VALUES (
                    %s, %s, %s
                );
        """

        involved_staff_query = """
             INSERT INTO involved_staff_medical_service_form (
                    service_form_id,
                    staff_id
                )
                VALUES (
                    %s, %s
                );
        """

        medical_equipment_query = """
            INSERT INTO borrowed_items (
                    borrow_log_id,
                    equipment_id
                )
                VALUES (
                    %s, %s
                );
        """

        try:
            self.controller.cursor.execute(query, query_params)
            form_id = self.controller.cursor.lastrowid

            # Associative Tables
            for staff_id in data['INVOLVED STAFF IDS']:
                self.controller.cursor.execute(involved_staff_query, (form_id, staff_id))

            for equipment_id in data['MEDICAL EQUIPMENT IDS']:
                self.controller.cursor.execute(medical_equipment_query, (form_id, equipment_id))

            for supply_id, quantity in data['MEDICAL SUPPLIES IDS'].items():
                self.controller.cursor.execute(med_supplies_query, (supply_id, form_id, quantity))

            self.controller.connection.commit()
            self.controller.add_log(
                f"Added new medical service form for Student ID: {data['STUDENT ID']}."
            )
            messagebox.showinfo(
                "Success",
                "Medical service form record has been added successfully.",
            )
            self.parent.search_records()
            self.close_window()

        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror(
                "Database Error", f"Could not add record.\n\n{e}"
            )

    def clear_fields(self):
        for entry in self.entry_widgets.values():
            entry.delete(0, tk.END)
        self.apt_month.set("January")
        self.apt_day.set("01")
        self.apt_year.set("2026")
        self.start_hour.set("08")
        self.start_min.set("00")
        self.end_hour.set("09")
        self.end_min.set("00")

    def is_form_empty(self) -> bool:
        for entry in self.entry_widgets.values():
            if entry.get().strip():
                return False
        return True

    def get_form_data(self) -> dict:
        data = {}
        tuple_fields = {
            "INVOLVED STAFF IDS",
            "MEDICAL EQUIPMENT IDS",
        }

        for label, entry in self.entry_widgets.items():
            raw_text = entry.get().strip()

            if label == "MEDICAL SUPPLIES IDS":
                supplies_dict = {}
                if raw_text:
                    for item in raw_text.split(","):
                        if ":" in item:
                            k, v = item.split(":", 1)
                            supplies_dict[k.strip()] = v.strip()
                data[label] = supplies_dict

            elif label in tuple_fields:
                data[label] = tuple(
                    item.strip() for item in raw_text.split(",") if item.strip()
                )
            else:
                data[label] = raw_text

        month_num = self.month_map.get(self.apt_month.get(), "01")
        data["DATE"] = f"{self.apt_year.get()}-{month_num}-{self.apt_day.get()}"
        data["TIME START"] = f"{self.start_hour.get()}:{self.start_min.get()}:00"
        data["TIME END"] = f"{self.end_hour.get()}:{self.end_min.get()}:00"
        return data

    def on_close_attempt(self):
        if self.is_form_empty() or messagebox.askokcancel(
            "Do you wish to close this window?",
            "Are you sure you want to close this window? Any data you have inputted will not be saved",
        ):
            self.close_window()

    def close_window(self):
        self.grab_release()
        self.destroy()