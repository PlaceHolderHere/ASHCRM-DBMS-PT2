import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import globals
from pages.students_page import StudentDetailWindow
from pages.staff_page import StaffDetailWindow


class ClinicVisitPage(tk.Frame):
    def __init__(self, parent, controller):
        self.background_color = globals.BACKGROUND_COLOR
        tk.Frame.__init__(self, parent, bg=self.background_color)
        self.cursor = controller.cursor
        self.controller = controller
        self.keyword = ""
        self._TABLE_NAME = "clinic_visit"
        self._create_widgets()

        self.tree.bind("<Double-1>", self.open_details_popup)

    def open_details_popup(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        visit_id = values[0]
        try:
            query = f"""
                SELECT visit_id, student_id, date, time_in, time_out, chief_complaints, treatment 
                FROM {self._TABLE_NAME} 
                WHERE visit_id = %s
            """
            self.cursor.execute(query, (visit_id,))
            row = self.cursor.fetchone()
            if row:
                columns = ["visit_id", "student_id", "date", "time_in", "time_out", "chief_complaints", "treatment"]
                values_dict = dict(zip(columns, row))
                ClinicVisitDetailWindow(self.controller, self, values_dict)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch clinic visit details.\n\n{e}")

    def delete_selected(self):
        rows = self.tree.selection()
        if not rows:
            return

        if not messagebox.askokcancel("Delete Records", "Are you sure you want to delete all selected clinic visits?"):
            return

        selected_ids = [(self.tree.item(row_id, "values")[0],) for row_id in rows]
        delete_visit_query = f"DELETE FROM {self._TABLE_NAME} WHERE visit_id = %s;"
        delete_staff_query = "DELETE FROM involved_staff_clinic_visit WHERE visit_id = %s;"

        try:
            for visit_id_tuple in selected_ids:
                self.cursor.execute(delete_staff_query, visit_id_tuple)
                self.cursor.execute(delete_visit_query, visit_id_tuple)

            self.controller.connection.commit()
            self.search_records()
            self.controller.add_log(f"Deleted clinic visit IDs from {self._TABLE_NAME}: {selected_ids}")
            messagebox.showinfo("Deleted Records", "Successfully deleted selected clinic visits.")
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror("ERROR! Could not Delete", f"Failed to delete selected records.\n\nError Message: {e}")

    def display_records(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

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
                SELECT visit_id, student_id, date, time_in, time_out, chief_complaints, treatment
                FROM {self._TABLE_NAME}
                WHERE visit_id LIKE %s
                    OR student_id LIKE %s
                    OR date LIKE %s
                    OR chief_complaints LIKE %s
                    OR treatment LIKE %s
                ORDER BY visit_id
            """
            search_value = f"%{self.keyword}%"
            self.cursor.execute(query, (search_value,) * 5)
            rows = self.cursor.fetchall()

            if not rows:
                messagebox.showinfo("No Records Found", f"No clinic visits found matching '{self.keyword}'")
                return

            self.display_records(rows)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Search Failed.\n\n{e}")

    def load_records(self):
        try:
            query = f"""
                SELECT visit_id, student_id, date, time_in, time_out, chief_complaints, treatment
                FROM {self._TABLE_NAME}
                ORDER BY visit_id
            """
            self.cursor.execute(query)
            self.display_records(self.cursor.fetchall())
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not load clinic visits.\n\n{e}")

    def open_create_clinic_visit_popup(self):
        CreateClinicVisitPopUp(self.controller, self)

    def _create_widgets(self):
        search_frame = tk.Frame(self, bg=self.background_color)
        search_frame.pack(fill="x", padx=48, pady=(24, 16))
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(4, weight=1)

        ttk.Button(
            search_frame, text="← Back",
            command=lambda: self.controller.render_page("HOME"),
            style="BTN.TButton", cursor="hand2"
        ).grid(row=0, column=0, sticky="w", pady=(0, 16), padx=4)

        create_btn = globals.create_styled_button(
            search_frame, photo_path="Assets/Icons/Create.png",
            text="Add Clinic Visit", command=self.open_create_clinic_visit_popup, style="BTN.TButton"
        )
        create_btn.grid(row=0, column=4, sticky="e")

        tk.Label(
            search_frame, text="Search:", font=("Helvetica", 14),
            foreground=globals.ACCENT_COLOR, background=self.background_color
        ).grid(row=1, column=0, sticky="e", padx=(0, 4))

        self.search_entry = ttk.Entry(search_frame, style="ENTRY.TEntry")
        self.search_entry.grid(row=1, column=1, padx=(0, 12), sticky="ew")

        ttk.Button(
            search_frame, text="Search", command=self.search_records, style="BTN.TButton", cursor="hand2"
        ).grid(row=1, column=2, padx=(0, 6))

        ttk.Button(
            search_frame, text="Show All", command=self.load_records, style="BTN.TButton", cursor="hand2"
        ).grid(row=1, column=3)

        delete_btn = globals.create_styled_button(
            search_frame, photo_path="Assets/Icons/Delete.png",
            text="Delete Selected", command=self.delete_selected, style="BTN_RED.TButton"
        )
        delete_btn.grid(row=1, column=4, sticky="e")

        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=48, pady=(24, 32))

        columns = ("visit_id", "student_id", "date", "time_in", "time_out", "chief_complaints", "treatment")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        self.tree.tag_configure("odd", background=globals.PRIMARY_LIGHT)
        self.tree.tag_configure("even", background=globals.BACKGROUND_COLOR)

        headings = {
            "visit_id": "Visit ID", "student_id": "Student ID", "date": "Date",
            "time_in": "Time In", "time_out": "Time Out",
            "chief_complaints": "Chief Complaints", "treatment": "Treatment"
        }
        widths = {
            "visit_id": 80, "student_id": 90, "date": 100,
            "time_in": 90, "time_out": 90,
            "chief_complaints": 250, "treatment": 250
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="SCROLL.TScrollbar")
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview, style="SCROLL.TScrollbar")
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")
        self.tree.pack(side="top", fill="both", expand=True)


class CreateClinicVisitPopUp(tk.Toplevel):
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

        self.title("Add Clinic Visit")
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

        title = tk.Label(
            container,
            text="ADD CLINIC VISIT",
            font=("Arial", 20, "bold"),
            background=globals.BACKGROUND_COLOR,
            foreground=globals.ACCENT_COLOR,
        )
        title.pack(pady=(15, 5))

        form_frame = tk.LabelFrame(
            container,
            text="Clinic Visit Details",
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
            "INVOLVED STAFF IDS",
            "DATE",
            "TIME IN",
            "TIME OUT",
            "CHIEF COMPLAINTS",
            "TREATMENT",
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
                sticky="nw" if label in ["CHIEF COMPLAINTS", "TREATMENT"] else "w",
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

            elif label in ["TIME IN", "TIME OUT"]:
                time_frame = tk.Frame(form_frame, bg=globals.BACKGROUND_COLOR)
                time_frame.grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16),
                )

                if label == "TIME IN":
                    self.in_hour = tk.StringVar(value="08")
                    self.in_min = tk.StringVar(value="00")
                    h_var, m_var = self.in_hour, self.in_min
                else:
                    self.out_hour = tk.StringVar(value="09")
                    self.out_min = tk.StringVar(value="00")
                    h_var, m_var = self.out_hour, self.out_min

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

            elif label in ["CHIEF COMPLAINTS", "TREATMENT"]:
                text_widget = tk.Text(
                    form_frame,
                    height=4,
                    width=25,
                    font=("Helvetica", 10),
                    wrap="word",
                    bd=0,
                    highlightthickness=1,
                    highlightbackground=globals.ACCENT_COLOR,
                    highlightcolor=globals.ACCENT_DARK
                )
                text_widget.grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16),
                )
                self.entry_widgets[label] = text_widget

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

        button_frame = tk.Frame(container, bg=globals.BACKGROUND_COLOR)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_close_attempt,
            style="BTN.TButton",
            cursor="hand2",
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Submit",
            command=self.add_clinic_visit_record,
            style="BTN.TButton",
            cursor="hand2",
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_fields,
            style="BTN_RED.TButton",
            cursor="hand2",
        ).grid(row=0, column=3, padx=5)

    def add_clinic_visit_record(self):
        if self.is_form_empty():
            messagebox.showerror(
                "Form is Empty!",
                "Error! Form is empty, please fill in the form.",
            )
            return

        data = self.get_form_data()

        query_params = {
            "STUDENT ID": data["STUDENT ID"],
            "DATE": data["DATE"],
            "TIME IN": data["TIME IN"],
            "TIME OUT": data["TIME OUT"],
            "CHIEF COMPLAINTS": data["CHIEF COMPLAINTS"],
            "TREATMENT": data["TREATMENT"],
        }

        query = """
                INSERT INTO clinic_visit (
                    student_id,
                    date,
                    time_in,
                    time_out,
                    chief_complaints,
                    treatment
                )
                VALUES (
                    %(STUDENT ID)s,
                    %(DATE)s,
                    %(TIME IN)s,
                    %(TIME OUT)s,
                    %(CHIEF COMPLAINTS)s,
                    %(TREATMENT)s
                );
                """

        involved_staff_query = """
             INSERT INTO involved_staff_clinic_visit (
                    visit_id,
                    staff_id
                )
                VALUES (
                    %s, %s
                );
        """

        try:
            self.controller.cursor.execute(query, query_params)
            visit_id = self.controller.cursor.lastrowid

            for staff_id in data["INVOLVED STAFF IDS"]:
                self.controller.cursor.execute(involved_staff_query, (visit_id, staff_id))

            self.controller.connection.commit()
            self.controller.add_log(
                f"Added new clinic visit record (ID: {visit_id}) for Student ID: {data['STUDENT ID']}."
            )
            messagebox.showinfo(
                "Success",
                "Clinic visit record has been added successfully.",
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
            if isinstance(entry, tk.Text):
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
        self.apt_month.set("January")
        self.apt_day.set("01")
        self.apt_year.set("2026")
        self.in_hour.set("08")
        self.in_min.set("00")
        self.out_hour.set("09")
        self.out_min.set("00")

    def is_form_empty(self) -> bool:
        for entry in self.entry_widgets.values():
            if isinstance(entry, tk.Text):
                if entry.get("1.0", tk.END).strip():
                    return False
            else:
                if entry.get().strip():
                    return False
        return True

    def get_form_data(self) -> dict:
        data = {}

        for label, entry in self.entry_widgets.items():
            if isinstance(entry, tk.Text):
                raw_text = entry.get("1.0", tk.END).strip()
            else:
                raw_text = entry.get().strip()

            if label == "INVOLVED STAFF IDS":
                data[label] = tuple(
                    item.strip() for item in raw_text.split(",") if item.strip()
                )
            else:
                data[label] = raw_text

        month_num = self.month_map.get(self.apt_month.get(), "01")
        data["DATE"] = f"{self.apt_year.get()}-{month_num}-{self.apt_day.get()}"
        data["TIME IN"] = f"{self.in_hour.get()}:{self.in_min.get()}:00"
        data["TIME OUT"] = f"{self.out_hour.get()}:{self.out_min.get()}:00"
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


class ClinicVisitDetailWindow(tk.Toplevel):
    month_map = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }
    month_map_rev = {v: k for k, v in month_map.items()}

    def __init__(self, controller, parent, visit_id_or_data):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent

        if isinstance(visit_id_or_data, dict):
            self.visit_data = visit_id_or_data
            self.visit_id = visit_id_or_data.get("visit_id")
        else:
            self.visit_id = visit_id_or_data
            self.visit_data = {}

        self.fetch_data()

        self.title("Clinic Visit Details")
        self.geometry(f"{globals.window_width // 2}x{int(globals.window_height * 0.7)}")
        self.resizable(False, False)

        x, y = controller.get_screen_center(globals.window_width // 2, int(globals.window_height * 0.7))
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._create_widgets()

    def fetch_data(self):
        if not self.visit_id:
            return

        query = """
            SELECT 
                visit_id,
                student_id,
                date,
                time_in,
                time_out,
                chief_complaints,
                treatment
            FROM clinic_visit
            WHERE visit_id = %s
        """
        try:
            self.controller.cursor.execute(query, (self.visit_id,))
            result = self.controller.cursor.fetchone()

            if result:
                if isinstance(result, dict):
                    self.visit_data.update(result)
                else:
                    self.visit_data.update({
                        "visit_id": result[0],
                        "student_id": result[1],
                        "date": result[2],
                        "time_in": result[3],
                        "time_out": result[4],
                        "chief_complaints": result[5],
                        "treatment": result[6]
                    })

            self.controller.cursor.execute(
                "SELECT staff_id FROM involved_staff_clinic_visit WHERE visit_id = %s",
                (self.visit_id,)
            )
            self.staff_ids = self.controller.cursor.fetchall()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch clinic visit details.\n\n{e}")

    def view_student_details(self):
        student_id = self.visit_data.get("student_id")
        if not student_id:
            messagebox.showinfo("No Student ID", "No Student ID attached to this visit.")
            return

        try:
            StudentDetailWindow(self.controller, self, student_id, False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch student details.\n\n{e}")

    def view_staff_details(self, staff_id):
        if not staff_id:
            messagebox.showinfo("No Staff ID", "No Staff ID specified.")
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

        tk.Label(
            container,
            text="CLINIC VISIT DETAILS",
            font=("Arial", 20, "bold"),
            foreground=globals.ACCENT_COLOR,
            background=globals.BACKGROUND_COLOR
        ).pack(pady=(15, 5))

        info_frame = tk.Frame(container, padx=20, pady=10, bg=globals.BACKGROUND_COLOR)
        info_frame.pack(fill="both", expand=True)

        self.entry_widgets = {}

        raw_date = str(self.visit_data.get("date", ""))
        date_parts = raw_date.split("-") if "-" in raw_date else ["2026", "01", "01"]
        init_year = date_parts[0] if len(date_parts) > 0 else "2026"
        init_month_num = date_parts[1] if len(date_parts) > 1 else "01"
        init_day = date_parts[2] if len(date_parts) > 2 else "01"
        init_month_name = self.month_map_rev.get(init_month_num, "January")

        raw_in = str(self.visit_data.get("time_in", ""))
        in_parts = raw_in.split(":") if ":" in raw_in else ["08", "00"]

        raw_out = str(self.visit_data.get("time_out", ""))
        out_parts = raw_out.split(":") if ":" in raw_out else ["09", "00"]

        fields = [
            ("visit_id", "Visit ID"),
            ("student_id", "Student ID"),
            ("date", "Date"),
            ("time_in", "Time In"),
            ("time_out", "Time Out"),
            ("chief_complaints", "Chief Complaints"),
            ("treatment", "Treatment")
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
            ).grid(
                row=row,
                column=column * num_of_cols,
                sticky="nw" if field_key in ["chief_complaints", "treatment"] else "w",
                pady=8
            )

            if field_key == "visit_id":
                tk.Label(
                    info_frame,
                    text=self.visit_data.get("visit_id"),
                    font=("Helvetica", 11, "bold"),
                    background=globals.BACKGROUND_COLOR
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif field_key == "student_id":
                student_id = self.visit_data.get("student_id", "N/A")
                ttk.Button(
                    info_frame,
                    text=f"View Student ({student_id})",
                    style="BTN.TButton",
                    command=self.view_student_details,
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

            elif field_key in ["time_in", "time_out"]:
                time_frame = tk.Frame(info_frame, bg=globals.BACKGROUND_COLOR)
                time_frame.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

                if field_key == "time_in":
                    self.in_hour = tk.StringVar(value=in_parts[0])
                    self.in_min = tk.StringVar(value=in_parts[1])
                    h_var, m_var = self.in_hour, self.in_min
                else:
                    self.out_hour = tk.StringVar(value=out_parts[0])
                    self.out_min = tk.StringVar(value=out_parts[1])
                    h_var, m_var = self.out_hour, self.out_min

                ttk.Combobox(time_frame, textvariable=h_var, values=hours, state="readonly", width=4,
                             style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                tk.Label(time_frame, text=":", bg=globals.BACKGROUND_COLOR, font=("Helvetica", 11, "bold")).pack(
                    side="left")
                ttk.Combobox(time_frame, textvariable=m_var, values=minutes, state="readonly", width=4,
                             style="dropdown.TCombobox").pack(side="left")

            elif field_key in ["chief_complaints", "treatment"]:
                text_widget = tk.Text(
                    info_frame,
                    height=4,
                    width=25,
                    font=("Helvetica", 10),
                    wrap="word",
                    bd=0,
                    highlightthickness=1,
                    highlightbackground=globals.ACCENT_COLOR,
                    highlightcolor=globals.ACCENT_DARK
                )
                text_widget.insert("1.0", str(self.visit_data.get(field_key, "")))
                text_widget.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))
                self.entry_widgets[field_key] = text_widget

            else:
                entry = ttk.Entry(info_frame, style="ENTRY.TEntry")
                entry.insert(0, str(self.visit_data.get(field_key, "")))
                entry.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))
                self.entry_widgets[field_key] = entry

        if getattr(self, "staff_ids", None):
            tk.Label(
                container,
                text="INVOLVED STAFF",
                font=("Helvetica", 12, "bold"),
                foreground=globals.ACCENT_COLOR,
                background=globals.BACKGROUND_COLOR
            ).pack(anchor="w", padx=20, pady=(15, 5))

            staff_btn_frame = tk.Frame(container, bg=globals.BACKGROUND_COLOR, padx=20)
            staff_btn_frame.pack(fill="x")

            for item in self.staff_ids:
                s_id = item[0] if isinstance(item, (tuple, list)) else item.get("staff_id")
                ttk.Button(
                    staff_btn_frame,
                    text=f"View Staff ({s_id})",
                    style="BTN.TButton",
                    command=lambda sid=s_id: self.view_staff_details(sid),
                    cursor="hand2"
                ).pack(side="left", padx=(0, 8), pady=4)

        ttk.Button(container, text="Save", style="BTN_SOLID.TButton", command=self.save_update).pack(
            pady=16, side="right", padx=(8, 32)
        )
        ttk.Button(container, text="Cancel", style="BTN.TButton", command=self.on_close).pack(
            pady=16, side="right", padx=8
        )

    def on_close(self):
        if not self.is_data_changed():
            self.destroy()
            return

        if messagebox.askokcancel("Unsaved Changes",
                                  "You have unsaved changes, are you sure you want to close this window?"):
            self.destroy()

    def is_data_changed(self) -> bool:
        entry_data = self.get_entry_data()
        for key in ["chief_complaints", "treatment", "date", "time_in", "time_out"]:
            if str(self.visit_data.get(key, "")) != str(entry_data.get(key, "")):
                return True
        return False

    def get_entry_data(self) -> dict:
        output = {}
        for key, widget in self.entry_widgets.items():
            if isinstance(widget, tk.Text):
                output[key] = widget.get("1.0", tk.END).strip()
            else:
                output[key] = widget.get().strip()

        output["visit_id"] = self.visit_data.get("visit_id")
        output["student_id"] = self.visit_data.get("student_id")

        month_num = self.month_map.get(self.apt_month.get(), "01")
        output["date"] = f"{self.apt_year.get()}-{month_num}-{self.apt_day.get()}"
        output["time_in"] = f"{self.in_hour.get()}:{self.in_min.get()}:00"
        output["time_out"] = f"{self.out_hour.get()}:{self.out_min.get()}:00"
        return output

    def save_update(self):
        if not self.is_data_changed():
            self.destroy()
            return

        visit_data = self.get_entry_data()
        if visit_data.get("visit_id") is None:
            messagebox.showerror("ERROR! Invalid Visit ID", "Error! Invalid Visit ID.")
            return

        query = """
            UPDATE clinic_visit
            SET
                student_id = %(student_id)s,
                time_in = %(time_in)s,
                time_out = %(time_out)s,
                date = %(date)s,
                chief_complaints = %(chief_complaints)s,
                treatment = %(treatment)s
            WHERE 
                visit_id = %(visit_id)s
        """
        try:
            self.controller.cursor.execute(query, visit_data)
            self.controller.connection.commit()

            log_msg = f"Updated Clinic Visit (ID: {visit_data.get('visit_id')})."
            self.controller.add_log(log_msg)

            messagebox.showinfo("Updated Successfully!", "Updated clinic visit record successfully!")
            self.parent.search_records()
            self.destroy()
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror("ERROR! Could not Update Record",
                                 f"An error occurred while trying to update clinic visit ID {visit_data.get('visit_id')}\n\nError Message: {e}")