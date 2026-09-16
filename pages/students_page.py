import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import csv
import json
import mysql.connector
import globals

class StudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        self.background_color = globals.BACKGROUND_COLOR
        tk.Frame.__init__(self, parent, bg=self.background_color)
        self.cursor = controller.cursor
        self.controller = controller
        self.keyword = ""
        self._TABLE_NAME = "student"
        self._create_widgets()

    def open_create_student_popup(self):
        create_student_popup = CreateStudentProfilePopUp(self.controller, self)
        self.wait_window(create_student_popup)

    def delete_selected(self):
        rows = self.tree.selection()
        if not rows:
            return

        if not messagebox.askokcancel("Delete Records",
                                      "Are you sure you want to delete all of the currently selected records?"):
            return

        selected_ids = []
        for row_id in rows:
            row = self.tree.item(row_id, "values")
            selected_ids.append((row[0],))

        query = f"DELETE FROM {self._TABLE_NAME} WHERE student_id = %s;"
        try:
            self.cursor.executemany(query, selected_ids)
            self.controller.connection.commit()
            self.search_records()
            self.controller.add_log(f"Deleted the following ids from {self._TABLE_NAME} table: {selected_ids}")
            messagebox.showinfo("Deleted Records", "Successfully Deleted all Selected Records")
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
            if row_idx % 2 == 0:
                tag="even"
            else:
                tag="odd"

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
                    student_id,
                    name,
                    section,
                    date_of_birth,
                    emergency_contact_number
                FROM {self._TABLE_NAME}
                WHERE student_id LIKE %s
                    OR name LIKE %s
                    OR section LIKE %s
                    OR date_of_birth LIKE %s
                    OR emergency_contact_number LIKE %s
                ORDER BY student_id
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

            # Checking if any Staff Members matching keyword were found
            if len(rows) == 0:
                messagebox.showinfo("No Students Found",
                                f"Could not find any students who's attributes containing {self.keyword}")
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
            query = query = f"""
                SELECT
                    student_id,
                    name,
                    section,
                    date_of_birth,
                    emergency_contact_number
                FROM {self._TABLE_NAME}
                ORDER BY student_id
            """

            self.cursor.execute(query)

            rows = self.cursor.fetchall()

            self.display_records(rows)

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                f"Could not Load Staff Records. \n\n{e}"
            )

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

        upload_csv_btn = ttk.Button(
            search_frame,
            text="Upload CSV",
            command=self.upload_csv,
            style="BTN.TButton",
            cursor="hand2"
        )
        upload_csv_btn.grid(
            row=0,
            column=4,
            sticky="e"
        )

        create_btn = globals.create_styled_button(
            search_frame,
            photo_path="Assets/Icons/Create.png",
            text="Create Profile",
            style="BTN.TButton",
            command=self.open_create_student_popup
        )
        create_btn.grid(
            row=0,
            column=5,
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
            padx = (0, 12),
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
            column=5,
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
            "student_id",
            "name",
            "section",
            "date_of_birth",
            "emergency_contact_number"
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
            "student_id": "Student ID",
            "name": "Name",
            "section": "Section",
            "date_of_birth": "Date of Birth",
            "emergency_contact_number": "Emergency Contact Number"
        }

        # COLUMN WIDTHS
        widths = {
            "student_id": 100,
            "name": 180,
            "section": 120,
            "date_of_birth": 120,
            "emergency_contact_number": 120
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

    def upload_csv(self):
        # Get csv file path
        rows = []
        csv_file_path = filedialog.askopenfilename(
            title="Select a Photo to Edit",
            filetypes=[("Photos", "*.csv")],
        )

        if not csv_file_path:
            return

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(row)

        self.insert_csv_to_database(rows)

    def insert_csv_to_database(self, data) -> bool:
        cleaned_data = []

        for row_index, row in enumerate(data):
            family_history = self.validate_json_string(row.get("family_history"))
            medical_history = self.validate_json_string(row.get("medical_history"))
            immunizations = self.validate_json_string(row.get("immunizations"))
            psychosocial_history = self.validate_json_string(row.get("psychosocial_history"))
            sexual_history = self.validate_json_string(row.get("sexual_history"))

            if any(x is None for x in (family_history, medical_history, immunizations,
                                       psychosocial_history, sexual_history)):
                messagebox.showerror("ERROR! Failed to Upload CSV", f"ERROR! Invalid JSON inputted")
                return False

            cleaned_data.append({
                "name": row.get("name"),
                "section": row.get("section"),
                "address": row.get("address"),
                "date_of_birth": row.get("date_of_birth"),
                "religion": row.get("religion"),
                "nationality": row.get("nationality"),
                "emergency_contact_number": row.get("emergency_contact_number"),
                "family_history": family_history,
                "medical_history": medical_history,
                "immunizations": immunizations,
                "psychosocial_history": psychosocial_history,
                "sexual_history": sexual_history
            })

        query = """
            INSERT INTO student (name, section, address, date_of_birth, religion, nationality,
                emergency_contact_number, family_history, medical_history, immunizations, psychosocial_history,
                sexual_history)
            VALUES (%(name)s, %(section)s, %(address)s, %(date_of_birth)s, %(religion)s, %(nationality)s,
                %(emergency_contact_number)s, %(family_history)s, %(medical_history)s, %(immunizations)s,
                %(psychosocial_history)s, %(sexual_history)s)
        """

        try:
            self.controller.cursor.executemany(query, cleaned_data)
            self.controller.connection.commit()
            self.search_records()
            messagebox.showinfo("Upload Successful!", "Successfully Uploaded Student Profiles into Database")
            return True

        except mysql.connector.Error as e:
            messagebox.showerror("ERROR! Failed to Upload CSV", f"Error Message: {e}")
            self.controller.connection.rollback()
            return False

    def validate_json_string(self, json_string: str) -> str | None:
        if json_string is None:
            return None

        try:
            output = json.dumps(json.loads(json_string))
        except:
            return None

        return output


class CreateStudentProfilePopUp(tk.Toplevel):
    def __init__(self, controller, parent):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent

        # Window Configuration
        self.title("Create a Student Profile")
        self.geometry(f"{int(globals.window_width // 1.5)}x{int(globals.window_height // 1.5)}")
        self.resizable(False, False)

        # Center relative to parent
        x, y = controller.get_screen_center(globals.window_width // 2, globals.window_height // 2)
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

        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        self.bind("<Enter>", _bind_mousewheel)

        title = tk.Label(
            container,
            text="STUDENTS",
            font=("Arial", 22, "bold"),
            background=globals.BACKGROUND_COLOR,
            foreground=globals.ACCENT_COLOR
        )
        title.pack(pady=(15, 5))

        # --- COMBINED FORM CONTAINER ---
        form_frame = tk.LabelFrame(
            container,
            text="Student Information & Medical History",
            padx=16,
            pady=16,
            background=globals.BACKGROUND_COLOR,
            foreground=globals.ACCENT_COLOR
        )
        form_frame.pack(fill="x", padx=20, pady=4)

        # 1. Standard Text Entries
        form_entries = {
            "name": "Name",
            "section": "Section",
            "address": "Address",
            "religion": "Religion",
            "nationality": "Nationality",
            "emergency_contact_number": "Emergency Contact Number"
        }

        self.entry_widgets = {}

        entry_keys = list(form_entries.keys())
        entry_keys.insert(3, "date_of_birth")

        num_of_cols = 2
        last_row = 0

        # Month mapping dict for UI display -> MySQL conversion
        self.month_map = {
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
            "December": "12"
        }

        for index, key in enumerate(entry_keys):
            column = index % num_of_cols
            row = index // num_of_cols
            last_row = row

            if key == "date_of_birth":
                tk.Label(
                    form_frame,
                    text="Date of Birth",
                    font=("Helvetica", 11, "bold"),
                    foreground=globals.ACCENT_COLOR,
                    background=globals.BACKGROUND_COLOR
                ).grid(row=row, column=column * num_of_cols, sticky="w", pady=8)

                # Date Picker Frame (Month Dropdown / Day / Year)
                dob_frame = tk.Frame(form_frame, bg=globals.BACKGROUND_COLOR)
                dob_frame.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

                month_names = list(self.month_map.keys())
                days = [f"{i:02d}" for i in range(1, 32)]
                years = [str(i) for i in range(2026, 1940, -1)]

                self.dob_month = tk.StringVar(value="January")
                self.dob_day = tk.StringVar(value="01")
                self.dob_year = tk.StringVar(value="2005")

                ttk.Combobox(dob_frame, textvariable=self.dob_month, values=month_names, state="readonly", width=10,
                             style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                ttk.Combobox(dob_frame, textvariable=self.dob_day, values=days, state="readonly", width=3,
                             style="dropdown.TCombobox").pack(side="left", padx=(0, 2))
                ttk.Combobox(dob_frame, textvariable=self.dob_year, values=years, state="readonly", width=6,
                             style="dropdown.TCombobox").pack(side="left")

            else:
                label = form_entries[key]
                tk.Label(
                    form_frame,
                    text=label,
                    font=("Helvetica", 11, "bold"),
                    foreground=globals.ACCENT_COLOR,
                    background=globals.BACKGROUND_COLOR
                ).grid(row=row, column=column * num_of_cols, sticky="w", pady=8)

                self.entry_widgets[key] = ttk.Entry(
                    form_frame,
                    style="ENTRY.TEntry"
                )
                self.entry_widgets[key].grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16)
                )

        # Separator Line between basic info and medical history
        sep_row = last_row + 1
        ttk.Separator(form_frame, orient="horizontal").grid(
            row=sep_row, column=0, columnspan=4, sticky="ew", pady=15
        )

        # 2. Family History
        fam_row = sep_row + 1
        tk.Label(
            form_frame, text="Family History", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=fam_row, column=0, sticky="w", pady=4)

        fam_box = tk.Frame(form_frame, bg=globals.BACKGROUND_COLOR)
        fam_box.grid(row=fam_row, column=1, sticky="w", pady=4)

        self.fam_hypertension = tk.BooleanVar(value=False)
        self.fam_diabetes = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            fam_box, text="Hypertension", variable=self.fam_hypertension, style="checkbox.TCheckbutton"
        ).pack(side="left", padx=(0, 10))
        ttk.Checkbutton(
            fam_box, text="Diabetes", variable=self.fam_diabetes, style="checkbox.TCheckbutton"
        ).pack(side="left")

        # 3. Medical History
        med_row = fam_row + 1
        tk.Label(
            form_frame, text="Medical History", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=med_row, column=0, sticky="w", pady=4)

        med_box = tk.Frame(form_frame, bg=globals.BACKGROUND_COLOR)
        med_box.grid(row=med_row, column=1, sticky="w", pady=4)

        self.med_penicillin = tk.BooleanVar(value=False)
        self.med_asthma = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            med_box, text="Allergy: Penicillin", variable=self.med_penicillin, style="checkbox.TCheckbutton"
        ).pack(side="left", padx=(0, 10))
        ttk.Checkbutton(
            med_box, text="Asthma", variable=self.med_asthma, style="checkbox.TCheckbutton"
        ).pack(side="left")

        # 4. Immunizations
        imm_row = med_row + 1
        vac_options = ["Not Vaccinated", "Fully Vaccinated", "Up to date"]

        tk.Label(
            form_frame, text="COVID-19 Status", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=imm_row, column=0, sticky="w", pady=8)

        self.imm_covid = tk.StringVar(value="Fully Vaccinated")
        ttk.Combobox(
            form_frame, textvariable=self.imm_covid, values=vac_options, state="readonly", width=18,
            style="dropdown.TCombobox"
        ).grid(row=imm_row, column=1, sticky="w", pady=8, padx=(4, 16))

        tk.Label(
            form_frame, text="Tetanus Status", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=imm_row, column=2, sticky="w", pady=8)

        self.imm_tetanus = tk.StringVar(value="Up to date")
        ttk.Combobox(
            form_frame, textvariable=self.imm_tetanus, values=vac_options, state="readonly", width=18,
            style="dropdown.TCombobox"
        ).grid(row=imm_row, column=3, sticky="w", pady=8, padx=(4, 16))

        # 5. Psychosocial & Sexual History
        psy_row = imm_row + 1

        tk.Label(
            form_frame, text="Stress Level", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=psy_row, column=0, sticky="w", pady=8)

        self.psy_stress = tk.StringVar(value="Moderate")
        ttk.Combobox(
            form_frame, textvariable=self.psy_stress, values=["Low", "Moderate", "High"], state="readonly", width=18,
            style="dropdown.TCombobox"
        ).grid(row=psy_row, column=1, sticky="w", pady=8, padx=(4, 16))

        tk.Label(
            form_frame, text="Sexual History", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=psy_row, column=2, sticky="w", pady=8)

        self.sex_active = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form_frame, text="Sexually Active", variable=self.sex_active, style="checkbox.TCheckbutton"
        ).grid(row=psy_row, column=3, sticky="w", pady=8, padx=(4, 16))

        # --- BUTTONS ---
        button_frame = tk.Frame(container, bg=globals.BACKGROUND_COLOR)
        button_frame.pack(pady=15)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_close_attempt,
            style="BTN.TButton",
            cursor="hand2"
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Submit",
            command=self.add_staff_record,
            style="BTN.TButton",
            cursor="hand2"
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_fields,
            style="BTN_RED.TButton",
            cursor="hand2"
        ).grid(row=0, column=3, padx=5)

    def add_staff_record(self):
        if self.is_form_empty():
            messagebox.showerror("Form is Empty!", "Error! Form is empty, please fill in the form.")
            return

        data = self.get_form_data()
        query = """
                INSERT INTO student 
                    (name, section, address, date_of_birth, religion, nationality, emergency_contact_number, 
                    family_history, medical_history, immunizations, psychosocial_history, sexual_history)
                VALUES (%(name)s, %(section)s, %(address)s, %(date_of_birth)s, %(religion)s, %(nationality)s,
                    %(emergency_contact_number)s, %(family_history)s, %(medical_history)s, %(immunizations)s,
                    %(psychosocial_history)s, %(sexual_history)s)
                """
        try:
            self.controller.cursor.execute(query, data)
            self.controller.connection.commit()
            self.controller.add_log(f"Created a student profile for {data['name']} in student table.")
            messagebox.showinfo(
                "Success",
                "Student record has been added successfully."
            )
            self.parent.search_records()
            self.close_window()

        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror(
                "Database Error",
                f"Could not add record.\n\n{e}"
            )

    def clear_fields(self):
        for entry in self.entry_widgets.values():
            entry.delete(0, tk.END)

        # Reset DOB
        self.dob_month.set("January")
        self.dob_day.set("01")
        self.dob_year.set("2005")

        # Reset medical & history values
        self.fam_hypertension.set(False)
        self.fam_diabetes.set(False)
        self.med_penicillin.set(False)
        self.med_asthma.set(False)
        self.imm_covid.set("Fully Vaccinated")
        self.imm_tetanus.set("Up to date")
        self.psy_stress.set("Moderate")
        self.sex_active.set(False)

    def is_form_empty(self) -> bool:
        for entry in self.entry_widgets.values():
            if entry.get().strip():
                return False
        return True

    def get_form_data(self) -> dict:
        form_data = {}

        # Collect standard text inputs
        for label, entry in self.entry_widgets.items():
            form_data[label] = entry.get()

        # Map full month name to numeric string (e.g., "January" -> "01")
        selected_month_num = self.month_map.get(self.dob_month.get(), "01")

        # Format Date of Birth into MySQL DATE format (YYYY-MM-DD)
        form_data["date_of_birth"] = f"{self.dob_year.get()}-{selected_month_num}-{self.dob_day.get()}"

        # Build JSON strings for history fields
        form_data["family_history"] = json.dumps({
            "hypertension": self.fam_hypertension.get(),
            "diabetes": self.fam_diabetes.get()
        })
        form_data["medical_history"] = json.dumps({
            "allergies": ["Penicillin"] if self.med_penicillin.get() else [],
            "asthma": self.med_asthma.get()
        })
        form_data["immunizations"] = json.dumps({
            "covid19": self.imm_covid.get(),
            "tetanus": self.imm_tetanus.get()
        })
        form_data["psychosocial_history"] = json.dumps({
            "stress_level": self.psy_stress.get()
        })
        form_data["sexual_history"] = json.dumps({
            "active": self.sex_active.get()
        })

        return form_data

    def on_close_attempt(self):
        if self.is_form_empty() or messagebox.askokcancel(
            "Do you wish to close this window?",
            "Are you sure you want to close this window? Any data you have inputted will not be saved"
        ):
            self.close_window()

    def close_window(self):
        self.grab_release()
        self.destroy()