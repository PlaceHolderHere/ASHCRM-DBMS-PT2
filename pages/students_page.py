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
            command=None
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