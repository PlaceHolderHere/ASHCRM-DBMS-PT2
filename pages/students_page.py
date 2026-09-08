import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import csv
import json

class StudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Students Page", font=("Arial", 18), bg="#ecf0f1").pack(pady=20)

        home_button = tk.Button(self, text="Go to Home Page",
                            command=lambda: self.controller.render_page("HOME"))
        home_button.pack()
        upload_button = ttk.Button(self, text="Upload a CSV", command=self.upload_csv)
        upload_button.pack()

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