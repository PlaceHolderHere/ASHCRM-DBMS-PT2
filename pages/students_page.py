import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import csv
import json
import mysql.connector
import globals
import cv2
from PIL import Image, ImageTk

class StudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        self.background_color = globals.BACKGROUND_COLOR
        tk.Frame.__init__(self, parent, bg=self.background_color)
        self.cursor = controller.cursor
        self.controller = controller
        self.keyword = ""
        self._TABLE_NAME = "student"
        self._create_widgets()
        self.scanned_qr = None

        self.tree.bind("<Double-1>", self.open_details_popup)

    def open_details_popup(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        student_id = self.tree.item(selected[0], "values")[0]

        # Will open instantly the window from the separate file
        StudentDetailWindow(self.controller, self, student_id, True)

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

        scan_qr_btn = ttk.Button(
            search_frame,
            text="Scan QR",
            command=self.open_scanner,
            style="BTN.TButton",
            cursor="hand2"
        )
        scan_qr_btn.grid(
            row=0,
            column=2,
            padx=(0, 6)
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

    def open_scanner(self):
        scanner = QRScannerPopUp(self.controller, self)
        self.wait_window(scanner)

class QRScannerPopUp(tk.Toplevel):
    def __init__(self, controller, parent):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent
        self._webcam_update = None

        # Window Configuration
        self.title("Scan a QR")
        self.geometry(f"{int(globals.window_width // 1.5)}x{int(globals.window_height // 1.5)}")
        self.resizable(False, False)

        # Center relative to parent
        x, y = controller.get_screen_center(globals.window_width // 2, globals.window_height // 2)
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.close)
        self._create_widgets()

        # Start camera hardware and begin video loop
        if self.controller.qr_scanner.camera_ready:
            self.update_video_feed()
        else:
            self.status_label.config(text="Error: Could not access webcam.")

    def _create_widgets(self):
        # Video Display Frame
        self.video_label = tk.Label(self, bg="black")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Status Label
        self.status_label = tk.Label(
            self,
            text="Point camera at a QR Code...",
            font=("Helvetica", 11, "bold"),
            bg=globals.BACKGROUND_COLOR,
            fg=globals.ACCENT_COLOR
        )
        self.status_label.pack(pady=(0, 5))

        # Buttons
        btn_frame = tk.Frame(self, bg=globals.BACKGROUND_COLOR)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            style="BTN_RED.TButton",
            cursor="hand2"
        ).pack()

    def update_video_feed(self):
        success, frame, qr_data = self.controller.qr_scanner.get_frame_and_qr()

        if success and frame is not None:
            # Convert OpenCV BGR frame to PIL RGB Image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update video label
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            # If a QR code was scanned successfully
            if qr_data:
                self.parent.scanned_qr = qr_data
                StudentDetailWindow(self.controller, self.parent, qr_data, True)
                self.close()
                return

        # Schedule next frame update (~30 FPS)
        self._webcam_update = self.after(30, self.update_video_feed)

    def close(self):
        if self._webcam_update is not None:
            self.after_cancel(self._webcam_update)
        self.destroy()

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

class StudentDetailWindow(tk.Toplevel):
    def __init__(self, controller, parent, student_id, can_edit):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent
        self.student_id = student_id
        self.student_data = {}
        self.can_edit = can_edit

        # Fetch student record from database
        if not self._fetch_student_data():
            self.destroy()
            return

        # Window Configuration
        self.title("Student Profile Details")
        self.geometry(f"{int(globals.window_width // 1.5)}x{int(globals.window_height // 1.5)}")
        self.resizable(False, False)

        # Center relative to parent
        x, y = controller.get_screen_center(globals.window_width // 2, globals.window_height // 2)
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)  # Keeps window on top of parent
        self.grab_set()  # Routes all user events strictly to this window

        # Run a Function When the User Closes the Window
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Month mapping dict for UI display -> MySQL conversion
        self.month_map = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }
        self.rev_month_map = {v: k for k, v in self.month_map.items()}

        # Create UI Widgets & populate
        self._create_widgets()
        if self.can_edit:
            self._load_student_data()

    def _fetch_student_data(self) -> bool:
        query = """
            SELECT 
                student_id, name, section, address, date_of_birth, religion, 
                nationality, emergency_contact_number, family_history, 
                medical_history, immunizations, psychosocial_history, sexual_history
            FROM student
            WHERE student_id = %s
        """
        try:
            self.controller.cursor.execute(query, (self.student_id,))
            record = self.controller.cursor.fetchone()

            if not record:
                messagebox.showerror("Error", f"No record found for Student ID: {self.student_id}")
                return False

            # Map tuple columns to dictionary keys matching database column names
            columns = [column[0] for column in self.controller.cursor.description]
            self.student_data = dict(zip(columns, record))
            return True

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch student data.\n\n{e}")
            return False

    def _create_widgets(self):
        # Base container canvas setup for scrolling
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

        # The inner container that holds all widgets
        container = tk.Frame(canvas, bg=globals.BACKGROUND_COLOR)
        canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")

        # Binds to handle scrolling region and full-width resizing
        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        self.bind("<Enter>", _bind_mousewheel)
        self.bind("<Leave>", _unbind_mousewheel)

        # TITLE
        tk.Label(
            container,
            text="STUDENTS",
            font=("Arial", 22, "bold"),
            foreground=globals.ACCENT_COLOR,
            background=globals.BACKGROUND_COLOR
        ).pack(pady=(15, 5))

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

        # 1. Standard Text Entries & Student ID
        form_entries = {
            "student_id": "Student ID",
            "name": "Name",
            "section": "Section",
            "address": "Address",
            "date_of_birth": "Date of Birth",
            "religion": "Religion",
            "nationality": "Nationality",
            "emergency_contact_number": "Emergency Contact Number"
        }

        self.entry_widgets = {}
        num_of_cols = 2
        last_row = 0
        for index, (key, label_text) in enumerate(form_entries.items()):
            column = index % num_of_cols
            row = index // num_of_cols
            last_row = row

            tk.Label(
                form_frame,
                text=label_text,
                font=("Helvetica", 11, "bold"),
                foreground=globals.ACCENT_COLOR,
                background=globals.BACKGROUND_COLOR
            ).grid(row=row, column=column * num_of_cols, sticky="w", pady=8)

            if key == "student_id":
                self.student_id_label = tk.Label(
                    form_frame,
                    text="",
                    font=("Helvetica", 11, "bold"),
                    background=globals.BACKGROUND_COLOR,
                    foreground=globals.ACCENT_COLOR
                )
                self.student_id_label.grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8, padx=(4, 16))

            elif self.can_edit:
                if key == "date_of_birth":
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
                    self.entry_widgets[key] = ttk.Entry(
                        form_frame,
                        style="ENTRY.TEntry"
                    )
                    self.entry_widgets[key].grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8,
                                                 padx=(4, 16))

            else:
                tk.Label(
                    form_frame,
                    text=f"{self.student_data.get(key)}",
                    font=("Helvetica", 11, "bold"),
                    background=globals.BACKGROUND_COLOR,
                    foreground=globals.ACCENT_COLOR
                ).grid(row=row, column=(column * num_of_cols) + 1, sticky="w", pady=8,
                                                 padx=(4, 16))
        # Separator Line
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
        ttk.Checkbutton(fam_box, text="Hypertension", variable=self.fam_hypertension,
                        style="checkbox.TCheckbutton").pack(side="left", padx=(0, 10))
        ttk.Checkbutton(fam_box, text="Diabetes", variable=self.fam_diabetes, style="checkbox.TCheckbutton").pack(
            side="left")

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
        ttk.Checkbutton(med_box, text="Allergy: Penicillin", variable=self.med_penicillin,
                        style="checkbox.TCheckbutton").pack(side="left", padx=(0, 10))
        ttk.Checkbutton(med_box, text="Asthma", variable=self.med_asthma, style="checkbox.TCheckbutton").pack(
            side="left")

        # 4. Immunizations
        imm_row = med_row + 1
        vac_options = ["Not Vaccinated", "Fully Vaccinated", "Up to date"]

        tk.Label(
            form_frame, text="COVID-19 Status", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=imm_row, column=0, sticky="w", pady=8)

        self.imm_covid = tk.StringVar(value="Fully Vaccinated")
        ttk.Combobox(form_frame, textvariable=self.imm_covid, values=vac_options, state="readonly", width=18,
                     style="dropdown.TCombobox").grid(row=imm_row, column=1, sticky="w", pady=8, padx=(4, 16))

        tk.Label(
            form_frame, text="Tetanus Status", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=imm_row, column=2, sticky="w", pady=8)

        self.imm_tetanus = tk.StringVar(value="Up to date")
        ttk.Combobox(form_frame, textvariable=self.imm_tetanus, values=vac_options, state="readonly", width=18,
                     style="dropdown.TCombobox").grid(row=imm_row, column=3, sticky="w", pady=8, padx=(4, 16))

        # 5. Psychosocial & Sexual History
        psy_row = imm_row + 1

        tk.Label(
            form_frame, text="Stress Level", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=psy_row, column=0, sticky="w", pady=8)

        self.psy_stress = tk.StringVar(value="Moderate")
        ttk.Combobox(form_frame, textvariable=self.psy_stress, values=["Low", "Moderate", "High"], state="readonly",
                     width=18, style="dropdown.TCombobox").grid(row=psy_row, column=1, sticky="w", pady=8, padx=(4, 16))

        tk.Label(
            form_frame, text="Sexual History", font=("Helvetica", 11, "bold"),
            foreground=globals.ACCENT_COLOR, background=globals.BACKGROUND_COLOR
        ).grid(row=psy_row, column=2, sticky="w", pady=8)

        self.sex_active = tk.BooleanVar(value=False)
        ttk.Checkbutton(form_frame, text="Sexually Active", variable=self.sex_active,
                        style="checkbox.TCheckbutton").grid(row=psy_row, column=3, sticky="w", pady=8, padx=(4, 16))

        # --- BUTTONS ---
        button_frame = tk.Frame(container, bg=globals.BACKGROUND_COLOR)
        button_frame.pack(pady=15)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_close,
            style="BTN.TButton",
            cursor="hand2"
        ).grid(row=0, column=0, padx=5)

        if self.can_edit:
            ttk.Button(
                button_frame,
                text="Save",
                command=self.save_update,
                style="BTN.TButton",
                cursor="hand2"
            ).grid(row=0, column=1, padx=5)

    def _parse_json_field(self, data) -> dict:
        if isinstance(data, dict):
            return data
        if isinstance(data, str) and data.strip():
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                pass
        return {}

    def _load_student_data(self):
        # Set Student ID Label
        self.student_id_label.config(text=str(self.student_data.get("student_id", "")))

        # Fill text entries
        for field, entry in self.entry_widgets.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.student_data.get(field, "")))

        # Parse Date of Birth (Expected format: YYYY-MM-DD)
        dob = str(self.student_data.get("date_of_birth", ""))
        if dob and len(dob.split("-")) == 3:
            y, m, d = dob.split("-")
            self.dob_year.set(y)
            self.dob_month.set(self.rev_month_map.get(m, "January"))
            self.dob_day.set(f"{int(d):02d}")

        # Parse Family History
        fam = self._parse_json_field(self.student_data.get("family_history"))
        self.fam_hypertension.set(fam.get("hypertension", False))
        self.fam_diabetes.set(fam.get("diabetes", False))

        # Parse Medical History
        med = self._parse_json_field(self.student_data.get("medical_history"))
        allergies = med.get("allergies", [])
        self.med_penicillin.set("Penicillin" in allergies)
        self.med_asthma.set(med.get("asthma", False))

        # Parse Immunizations
        imm = self._parse_json_field(self.student_data.get("immunizations"))
        self.imm_covid.set(imm.get("covid19", "Fully Vaccinated"))
        self.imm_tetanus.set(imm.get("tetanus", "Up to date"))

        # Parse Psychosocial & Sexual History
        psy = self._parse_json_field(self.student_data.get("psychosocial_history"))
        self.psy_stress.set(psy.get("stress_level", "Moderate"))

        sex = self._parse_json_field(self.student_data.get("sexual_history"))
        self.sex_active.set(sex.get("active", False))

    def get_entry_data(self) -> dict:
        form_data = {}
        for key, entry in self.entry_widgets.items():
            form_data[key] = entry.get()

        form_data["student_id"] = self.student_data.get("student_id")

        # Format Date of Birth for MySQL YYYY-MM-DD
        selected_month_num = self.month_map.get(self.dob_month.get(), "01")
        form_data["date_of_birth"] = f"{self.dob_year.get()}-{selected_month_num}-{self.dob_day.get()}"

        # Build JSON strings
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

    def is_data_changed(self) -> bool:
        current_data = self.get_entry_data()

        # Compare text entries and DOB
        for key in list(self.entry_widgets.keys()) + ["date_of_birth"]:
            if str(self.student_data.get(key, "")) != str(current_data.get(key, "")):
                return True

        # Compare JSON structures
        fam_orig = self._parse_json_field(self.student_data.get("family_history"))
        fam_curr = json.loads(current_data["family_history"])
        if fam_orig != fam_curr:
            return True

        med_orig = self._parse_json_field(self.student_data.get("medical_history"))
        med_curr = json.loads(current_data["medical_history"])
        if med_orig != med_curr:
            return True

        imm_orig = self._parse_json_field(self.student_data.get("immunizations"))
        imm_curr = json.loads(current_data["immunizations"])
        if imm_orig != imm_curr:
            return True

        psy_orig = self._parse_json_field(self.student_data.get("psychosocial_history"))
        psy_curr = json.loads(current_data["psychosocial_history"])
        if psy_orig != psy_curr:
            return True

        sex_orig = self._parse_json_field(self.student_data.get("sexual_history"))
        sex_curr = json.loads(current_data["sexual_history"])
        if sex_orig != sex_curr:
            return True

        return False

    def save_update(self):
        if not self.is_data_changed():
            self.destroy()
            return

        form_data = self.get_entry_data()
        if form_data.get("student_id") is None:
            messagebox.showerror("ERROR! Invalid Student ID", "Error! Invalid Student ID.")
            return

        query = """
            UPDATE student
            SET
                name = %(name)s,
                section = %(section)s,
                address = %(address)s,
                date_of_birth = %(date_of_birth)s,
                religion = %(religion)s,
                nationality = %(nationality)s,
                emergency_contact_number = %(emergency_contact_number)s,
                family_history = %(family_history)s,
                medical_history = %(medical_history)s,
                immunizations = %(immunizations)s,
                psychosocial_history = %(psychosocial_history)s,
                sexual_history = %(sexual_history)s
            WHERE 
                student_id = %(student_id)s
        """
        try:
            self.controller.cursor.execute(query, form_data)
            self.controller.connection.commit()
            self.controller.add_log(f"Updated the Information of {form_data.get('name')} in student table.")
            messagebox.showinfo("Updated Successfully!",
                                f"Updated the Information of {form_data.get('name')} successfully!")
            self.parent.search_records()
            self.destroy()
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror(
                "ERROR! Could not Update Record",
                f"An error occurred while trying to update the profile of {form_data.get('name')}\n\nError Message: {e}"
            )

    def on_close(self):
        if not self.can_edit:
            self.destroy()
            return

        if not self.is_data_changed():
            self.destroy()
            return

        if messagebox.askokcancel(
            "Unsaved Changes",
            "You have unsaved changes, are you sure you want to close this window?"
        ):
            self.destroy()