import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import globals

class StaffPage(tk.Frame):
    def __init__(self, parent, controller):
        self.background_color = globals.BACKGROUND_COLOR
        tk.Frame.__init__(self, parent, bg=self.background_color)
        self.cursor = controller.cursor
        self.controller = controller
        self.keyword = ""
        self._TABLE_NAME = "staff"
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

        query = f"DELETE FROM {self._TABLE_NAME} WHERE staff_id = %s;"
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
                    staff_id,
                    name,
                    position,
                    email,
                    contact_number
                FROM {self._TABLE_NAME}
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
                FROM {self._TABLE_NAME}
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
            text="Create Profile",
            command=self.open_create_staff_popup,
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
            "staff_id",
            "name",
            "position",
            "email",
            "contact_number"
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
        container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width)
        )

        def _on_mousewheel(event):
            # Windows/macOS event.delta vs Linux event.num
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            # Windows and macOS
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            # Linux (scroll up / scroll down)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        self.bind("<Enter>", _bind_mousewheel)
        self.bind("<Leave>", _unbind_mousewheel)

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
            self.destroy()
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
            self.controller.add_log(f"Updated the Information of {form_data.get("name")} in staff table")
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
        self.geometry(f"+{x}+{y}")

        self.transient(controller.root)  # Keeps window on top of parent
        self.grab_set()  # Routes all user events strictly to this window

        # Run a Function When the User Closes the Window
        self.protocol("WM_DELETE_WINDOW", self.on_close_attempt)

        # Create UI Widgets
        self._create_widgets()

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
        container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width)
        )

        def _on_mousewheel(event):
            # Windows/macOS event.delta vs Linux event.num
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            # Windows and macOS
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            # Linux (scroll up / scroll down)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        self.bind("<Enter>", _bind_mousewheel)
        self.bind("<Leave>", _unbind_mousewheel)

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
            pady=16,
            background=globals.BACKGROUND_COLOR
        )
        form_frame.pack(
            fill="x",
            padx=20,
            pady=4
        )

        form_entries = ["NAME", "POSITION", "CONTACT", "EMAIL"]
        self.entry_widgets = {}
        num_of_cols = 2
        for index, label in enumerate(form_entries):
            column = index % num_of_cols
            row = index // num_of_cols

            # THE LABELS/COLUMN OF INFO
            tk.Label(
                form_frame,
                text=label.title(),
                font=("Helvetica", 11, "bold"),
                foreground=globals.ACCENT_COLOR,
                background=globals.BACKGROUND_COLOR
            ).grid(
                row=row,
                column=column * num_of_cols,
                sticky="w",
                pady=8
            )

            self.entry_widgets[label] = ttk.Entry(
                form_frame,
                style="ENTRY.TEntry"
            )
            self.entry_widgets[label].grid(
                row=row,
                column=(column * num_of_cols) + 1,
                sticky="w",
                pady=8,
                padx=(4, 16)
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
            command=self.clear_fields,
            style="BTN_RED.TButton",
            cursor="hand2"
        ).grid(
            row=0,
            column=3,
            padx=5
        )

    def add_staff_record(self):
        if self.is_form_empty():
            messagebox.showerror("Form is Empty!", "Error! Form is empty, please fill in the form.")
            return

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
            self.controller.add_log(f"Created a staff profile for {data["NAME"]} in staff table.")
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
        for entry in self.entry_widgets.values():
            entry.delete(0, tk.END)

    def is_form_empty(self) -> bool:
        for entry in self.entry_widgets.values():
            if entry.get():
                return False

        return True

    def get_form_data(self) -> dict:
        return {label: entry.get() for label, entry in self.entry_widgets.items()}

    def on_close_attempt(self):
        if self.is_form_empty() or messagebox.askokcancel(
            "Do you wish to close this window?",
            "Are you sure you want to close this window? Any data you have inputted will not be saved"
        ):
            self.close_window()

    def close_window(self):
        self.grab_release()
        self.destroy()