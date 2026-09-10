import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import globals

class StaffPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.cursor = controller.cursor

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
            command=lambda : controller.render_page("HOME"),
            style = "BTN.TButton",
            cursor = "hand2")
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
        keyword = self.search_entry.get().strip()

        if not keyword:
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

            search_value = f"%{keyword}%"

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
                                    f"Could not find any staff members who's attributes containing {keyword}")
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
