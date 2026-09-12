import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import globals

class StaffPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.cursor = controller.cursor
        self.controller = controller
        self.keyword = ""
        self._create_widgets()

        # Run a function when a user double clicks on a row
        self.tree.bind("<Double-1>", self.open_details_popup)

    def open_details_popup(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        values_dict = dict(zip(self.tree["columns"], values))

        # Will open instantly the window from the separate file
        StaffDetailWindow(self.controller, self, values_dict)

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

        query = "DELETE FROM staff WHERE staff_id = %s;"
        try:
            self.cursor.executemany(query, selected_ids)
            self.controller.connection.commit()
            self.search_records()
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
        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=row
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
                    staff_id,
                    name,
                    position,
                    email,
                    contact_number
                FROM staff
                WHERE staff_id LIKE %s
                    OR name LIKE %s
                    OR position LIKE %s
                    OR email LIKE %s
                    OR contact_number LIKE %s
                ORDER BY staff_id
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
                messagebox.showinfo("No Staff Members Found",
                                f"Could not find any staff members who's attributes containing {self.keyword}")
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
                    staff_id,
                    name,
                    position,
                    email,
                    contact_number
                FROM staff
                ORDER BY staff_id
            """

            self.cursor.execute(query)

            rows = self.cursor.fetchall()

            self.display_records(rows)

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                f"Could not Load Staff Records. \n\n{e}"
            )

    def open_create_staff_popup(self):
        create_staff_popup = CreateStaffProfilePopUp(self.controller, self)
        self.wait_window(create_staff_popup)

    def _create_widgets(self):
        # SEARCH
        search_frame = tk.Frame(self)
        search_frame.pack(
            fill="x",
            padx=20,
            pady=(4, 8),
            ipady=16,
            ipadx=32
        )

        # Home
        home_button = ttk.Button(
            search_frame,
            text="← Home",
            command=lambda: self.controller.render_page("HOME"),
            style="BTN.TButton",
            cursor="hand2")
        home_button.pack(side="left")

        tk.Label(
            search_frame,
            text="Search:"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.search_entry = ttk.Entry(
            search_frame,
            width=40,
            style="ENTRY.TEntry"
        )

        self.search_entry.pack(
            side="left"
        )

        ttk.Button(
            search_frame,
            text="Search",
            width=12,
            command=self.search_records,
            style="BTN.TButton",
            cursor="hand2"
        ).pack(
            side="left",
            padx=4
        )

        # Show All Button
        ttk.Button(
            search_frame,
            text="Show All",
            width=12,
            command=self.load_records,
            style="BTN.TButton",
            cursor="hand2"
        ).pack(
            side="left"
        )

        ttk.Button(
            search_frame,
            text="Create Profile",
            command=self.open_create_staff_popup,
            style="BTN.TButton",
            cursor="hand2"
        ).pack(
            side="left",
            padx=(8, 0)
        )

        ttk.Button(
            search_frame,
            text="Delete Selected",
            command=self.delete_selected,
            style="BTN.TButton",
            cursor="hand2"
        ).pack(
            side="left",
            padx=(8, 0)
        )

        # Search Results Table
        table_frame = tk.Frame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(4, 8),
            ipady=16,
            ipadx=32
        )

        columns = (
            "staff_id",
            "name",
            "position",
            "email",
            "contact_number"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # COLUMN HEADINGS
        headings = {
            "staff_id": "Staff ID",
            "name": "Name",
            "position": "Position",
            "email": "Email",
            "contact_number": "Contact Number"
        }

        # COLUMN WIDTHS
        widths = {
            "staff_id": 100,
            "name": 180,
            "position": 120,
            "email": 120,
            "contact_number": 120
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
            command=self.tree.yview
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
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

class StaffDetailWindow(tk.Toplevel):
    def __init__(self, controller, parent, staff_data):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent
        self.staff_data = staff_data

        # Window Configuration
        self.title("Create a Staff Profile")
        self.geometry(f"{globals.window_width // 2}x{globals.window_height // 2}")
        self.resizable(False, False)

        # Center relative to parent
        x, y = controller.get_screen_center(globals.window_width // 2, globals.window_height // 2)
        self.geometry(
            f"+{x}+{y}"
        )

        self.transient(controller.root)  # Keeps window on top of parent
        self.grab_set()  # Routes all user events strictly to this window

        # Run a Function When the User Closes the Window
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create UI Widgets
        self._create_widgets()

    def _create_widgets(self):
        container = tk.Frame(self, background=globals.BACKGROUND_COLOR)
        container.pack(expand=True, fill="both")

        # TITLE
        tk.Label(
            container,
            text="STAFF",
            font=("Arial", 22, "bold"),
            foreground=globals.ACCENT_COLOR,
            background=globals.BACKGROUND_COLOR
        ).pack(
            pady=(15, 5)
        )

        # DETAILS FRAME
        info_frame = tk.Frame(
            container,
            padx=20,
            pady=10,
            bg=globals.BACKGROUND_COLOR
        )

        info_frame.pack(
            fill="both",
            expand=True)

        # It loops through the data/labels while generating a counter to tell the program
        # which row to place each piece of text on
        self.entry_widgets = {}
        num_of_cols = 2
        for index, (label_text, value_text) in enumerate(self.staff_data.items()):
            column = index % num_of_cols
            row = index // num_of_cols

            # THE LABELS/COLUMN OF INFO
            tk.Label(
                info_frame,
                text=label_text.title(),
                font=("Helvetica", 11, "bold"),
                foreground=globals.ACCENT_COLOR,
                background=globals.BACKGROUND_COLOR
            ).grid(
                row=row,
                column=column * num_of_cols,
                sticky="w",
                pady=8
            )

            # THE ACTUAL DATA
            if label_text == "staff_id":
                tk.Label(
                    info_frame,
                    text=value_text,
                    font=("Helvetica", 11, "bold"),
                    background=globals.BACKGROUND_COLOR
                ).grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16)
                )
            else:
                self.entry_widgets[label_text] = ttk.Entry(
                    info_frame,
                    style="ENTRY.TEntry"
                )
                self.entry_widgets[label_text].insert(0, value_text)
                self.entry_widgets[label_text].grid(
                    row=row,
                    column=(column * num_of_cols) + 1,
                    sticky="w",
                    pady=8,
                    padx=(4, 16)
                    )

        # SAVE BUTTON
        ttk.Button(
            container,
            text="Save",
            width=15,
            style="BTN_SOLID.TButton",
            command=self.save_update
        ).pack(
            pady=16,
            side="right",
            padx=(8, 32)
        )

        # CLOSE BUTTON
        ttk.Button(
            container,
            text="Cancel",
            width=15,
            style="BTN.TButton",
            command=self.on_close
        ).pack(
            pady=16,
            side="right",
            padx=8
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
        for key, value in self.staff_data.items():
            if value != entry_data.get(key):
                return True
        return False

    def get_entry_data(self) -> dict:
        output = {entry[0]: entry[1].get() for entry in self.entry_widgets.items()}
        output["staff_id"] = self.staff_data.get("staff_id")
        return output

    def save_update(self):
        if not self.is_data_changed():
            messagebox.showinfo("No Changes to Be Saved", "No changes have been made to be saved to the database.")
            return

        form_data = self.get_entry_data()
        if form_data.get("staff_id") is None:
            messagebox.showerror("ERROR! Invalid Staff ID", "Error! Invalid Staff ID.")
            return

        query = """
            UPDATE staff
            SET
                name = %(name)s,
                position = %(position)s,
                email = %(email)s,
                contact_number = %(contact_number)s
            WHERE 
                staff_id = %(staff_id)s
        """
        try:
            self.controller.cursor.execute(query, form_data)
            self.controller.connection.commit()
            messagebox.showinfo("Updated Successfully!",
                                f"Updated the Information of {form_data.get("name")} successfully!")
            self.parent.search_records()
            self.destroy()
        except mysql.connector.Error as e:
            self.controller.connection.rollback()
            messagebox.showerror("ERROR! Could not Update Record",
                f"An erorr occurred while trying to update the profile of {form_data.get("name")}"
                f"\n\nError Message: {e}")

class CreateStaffProfilePopUp(tk.Toplevel):
    def __init__(self, controller, parent):
        super().__init__(controller.root)
        self.controller = controller
        self.parent = parent

        # Window Configuration
        self.title("Create a Staff Profile")
        self.geometry(f"{globals.window_width // 2}x{globals.window_height // 2}")
        self.resizable(False, False)

        # Center relative to parent
        x, y = controller.get_screen_center(globals.window_width // 2, globals.window_height // 2)
        self.geometry(
            f"+{x}+{y}"
        )

        self.transient(controller.root)  # Keeps window on top of parent
        self.grab_set()  # Routes all user events strictly to this window

        # Run a Function When the User Closes the Window
        self.protocol("WM_DELETE_WINDOW", self.on_close_attempt)

        # Create UI Widgets
        self._create_widgets()

    def _create_widgets(self):
        container = tk.Frame(self, bg=globals.BACKGROUND_COLOR)
        container.pack(fill="both", expand=True)

        # TITLE
        title = tk.Label(
            container,
            text="CLINIC STAFF",
            font=("Arial", 22, "bold"),
            background=globals.BACKGROUND_COLOR,
            foreground=globals.ACCENT_COLOR
        )

        title.pack(pady=(15, 5))

        # FORM
        form_frame = tk.LabelFrame(
            container,
            text="Staff Information",
            padx=16,
            pady=16
        )

        form_frame.pack(
            fill="x",
            padx=20,
            pady=4
        )

        # STAFF NAME
        tk.Label(
            form_frame,
            text="Staff Name"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.name_entry = ttk.Entry(
            form_frame,
            width=25,
            style="ENTRY.TEntry"
        )
        self.name_entry.grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        # STAFF POSITION
        tk.Label(
            form_frame,
            text="Position"
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=5,
            pady=5
        )

        self.position_entry = ttk.Entry(
            form_frame,
            width=25,
            style="ENTRY.TEntry"
        )

        self.position_entry.grid(
            row=0,
            column=3,
            padx=5,
            pady=5
        )

        # STAFF CONTACT NUMBER
        tk.Label(
            form_frame,
            text="Contact Number"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.contact_number_entry = ttk.Entry(
            form_frame,
            width=25,
            style="ENTRY.TEntry"
        )

        self.contact_number_entry.grid(
            row=1,
            column=1,
            padx=5,
            pady=5
        )

        # STAFF EMAIL
        tk.Label(
            form_frame,
            text="Email"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=(20, 5),
            pady=5
        )

        self.email_entry = ttk.Entry(
            form_frame,
            width=25,
            style="ENTRY.TEntry"
        )

        self.email_entry.grid(
            row=1,
            column=3,
            padx=5,
            pady=5
        )

        # BUTTONS
        button_frame = tk.Frame(container)
        button_frame.pack(pady=10)

        # UPDATE RECORD
        ttk.Button(
            button_frame,
            text="Cancel",
            width=15,
            command=self.on_close_attempt,
            style="BTN.TButton",
            cursor="hand2"
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        # ADD RECORD
        ttk.Button(
            button_frame,
            text="Submit",
            width=15,
            command=self.add_staff_record,
            style="BTN.TButton",
            cursor="hand2"
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        # CLEAR STAFF FIELDS
        ttk.Button(
            button_frame,
            text="Clear",
            width=15,
            command=self.clear_fields,
            style="BTN.TButton",
            cursor="hand2"
        ).grid(
            row=0,
            column=3,
            padx=5
        )


    def add_staff_record(self):
        data = self.get_form_data()
        query = """
                INSERT INTO staff (name, position, email, contact_number)
                VALUES (%(NAME)s, %(POSITION)s, %(EMAIL)s, %(CONTACT)s);
                """

        try:
            self.controller.cursor.execute(
                query,
                data
            )

            self.controller.connection.commit()
            messagebox.showinfo(
                "Success",
            "Staff record has been added successfully."
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
        self.name_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.contact_number_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def get_form_data(self) -> dict:
        return {
            "NAME": self.name_entry.get(),
            "POSITION": self.position_entry.get(),
            "CONTACT": self.contact_number_entry.get(),
            "EMAIL": self.email_entry.get()
        }

    def on_close_attempt(self):
        if messagebox.askokcancel("Do you wish to close this window?",
                "Are you sure you want to close this window? Any data you have inputted will not be saved"):
            self.close_window()

    def close_window(self):
        self.grab_release()
        self.destroy()