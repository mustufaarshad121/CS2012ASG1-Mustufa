# cpy-333
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from backend import FinPayEngine, CreditTransaction


class FinPayApp(tk.Tk):
    """Main Tkinter controller owning the shared FinPayEngine and all three UI screens."""

    def __init__(self):
        super().__init__()

        self.title("FinPay - Transaction Manager")
        self.geometry("950x620")
        self.minsize(850, 550)

        # Shared backend engine instance across all screens
        self.engine = FinPayEngine()

        # Configure clean native styling
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Helvetica", 10))

        # Container holding stacked frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for ScreenClass in (WelcomeScreen, UploadScreen, DashboardScreen):
            page_name = ScreenClass.__name__
            frame = ScreenClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeScreen")

    def show_frame(self, page_name: str):
        """Brings the requested screen frame to the front."""
        frame = self.frames[page_name]
        frame.tkraise()


class WelcomeScreen(tk.Frame):
    """Landing screen introducing the FinPay Internal Finance Portal."""

    def __init__(self, parent, controller: FinPayApp):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        lbl_title = ttk.Label(self, text="Welcome to FinPay", font=("Helvetica", 26, "bold"))
        lbl_title.grid(row=1, column=0, pady=(10, 5))

        lbl_subtitle = ttk.Label(
            self,
            text="Internal Finance Department Portal — Transaction Ingestion, Audit & Analytics",
            font=("Helvetica", 12),
        )
        lbl_subtitle.grid(row=2, column=0, pady=(0, 20))

        btn_start = ttk.Button(
            self,
            text="Get Started  →",
            command=lambda: controller.show_frame("UploadScreen"),
        )
        btn_start.grid(row=3, column=0, pady=10, ipadx=16, ipady=6)


class UploadScreen(tk.Frame):
    """File selection and ingestion screen wired to FinPayEngine.load_data()."""

    def __init__(self, parent, controller: FinPayApp):
        super().__init__(parent)
        self.controller = controller
        self.selected_filepath = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        lbl_header = ttk.Label(self, text="Load Transaction Data", font=("Helvetica", 20, "bold"))
        lbl_header.grid(row=0, column=0, pady=20, sticky="s")

        upload_frame = ttk.LabelFrame(self, text="Transaction File Ingestion", padding=35)
        upload_frame.grid(row=1, column=0, pady=15)

        lbl_info = ttk.Label(
            upload_frame,
            text="Select a transaction ledger file to buffer through IngestionQueue.\nSupported formats: .csv and .json",
            justify="center",
        )
        lbl_info.pack(pady=(0, 12))

        self.lbl_filename = ttk.Label(
            upload_frame,
            text="No file selected",
            foreground="gray",
            font=("Helvetica", 10, "italic"),
        )
        self.lbl_filename.pack(pady=6)

        btn_browse = ttk.Button(upload_frame, text="Browse File...", command=self.browse_file)
        btn_browse.pack(pady=10, ipadx=10, ipady=3)

        # Navigation buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, pady=20)

        btn_back = ttk.Button(
            btn_frame,
            text="← Back",
            command=lambda: controller.show_frame("WelcomeScreen"),
        )
        btn_back.grid(row=0, column=0, padx=10, ipadx=10, ipady=4)

        self.btn_load = ttk.Button(
            btn_frame,
            text="Load Data  →",
            state="disabled",
            command=self.handle_load_data,
        )
        self.btn_load.grid(row=0, column=1, padx=10, ipadx=10, ipady=4)

    def browse_file(self):
        """Opens native OS file dialog and enables Load Data once a file is chosen."""
        filepath = filedialog.askopenfilename(
            title="Select Transaction File",
            filetypes=(
                ("Supported Files", "*.csv *.json"),
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*"),
            ),
        )
        if filepath:
            self.selected_filepath = filepath
            self.lbl_filename.config(text=os.path.basename(filepath), foreground="#1b5e20")
            self.btn_load.config(state="normal")

    def handle_load_data(self):
        """Calls backend load_data(), handles validation errors, and opens DashboardScreen."""
        if not self.selected_filepath:
            messagebox.showwarning("No File", "Please select a .csv or .json file first.")
            return

        try:
            loaded_count, skipped_count = self.controller.engine.load_data(self.selected_filepath)
        except (FileNotFoundError, ValueError, OSError) as exc:
            messagebox.showerror("Load Error", str(exc))
            return

        messagebox.showinfo(
            "Ingestion Complete",
            f"Successfully loaded {loaded_count} valid transaction(s).\n"
            f"Skipped {skipped_count} invalid/corrupt row(s).",
        )

        # Populate dashboard dropdowns & table before switching screens
        dashboard: DashboardScreen = self.controller.frames["DashboardScreen"]
        dashboard.refresh_filter_options()
        dashboard.refresh_table()
        self.controller.show_frame("DashboardScreen")


class DashboardScreen(tk.Frame):
    """Interactive analytics, multi-criteria filtering, undo stack, and export screen."""

    def __init__(self, parent, controller: FinPayApp):
        super().__init__(parent)
        self.controller = controller

        # --- Top Filter Bar ---
        filter_frame = ttk.LabelFrame(self, text="Filter & History Controls", padding=10)
        filter_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))

        # City Filter
        ttk.Label(filter_frame, text="City:").pack(side="left", padx=(4, 2))
        self.cb_city = ttk.Combobox(filter_frame, values=["All"], state="readonly", width=13)
        self.cb_city.current(0)
        self.cb_city.pack(side="left", padx=4)

        # Date Filter
        ttk.Label(filter_frame, text="Date:").pack(side="left", padx=(8, 2))
        self.cb_date = ttk.Combobox(filter_frame, values=["All"], state="readonly", width=12)
        self.cb_date.current(0)
        self.cb_date.pack(side="left", padx=4)

        # Type Filter
        ttk.Label(filter_frame, text="Type:").pack(side="left", padx=(8, 2))
        self.cb_type = ttk.Combobox(filter_frame, values=["All", "Credit", "Debit"], state="readonly", width=9)
        self.cb_type.current(0)
        self.cb_type.pack(side="left", padx=4)

        # Action Buttons
        ttk.Button(filter_frame, text="Apply Filters", command=self.handle_apply_filters).pack(
            side="left", padx=(12, 4)
        )
        ttk.Button(filter_frame, text="Revert Filter", command=self.handle_revert_filter).pack(
            side="left", padx=4
        )
        ttk.Button(filter_frame, text="Clear Filters", command=self.handle_clear_filters).pack(
            side="left", padx=4
        )

        ttk.Button(
            filter_frame,
            text="← Upload More",
            command=lambda: controller.show_frame("UploadScreen"),
        ).pack(side="right", padx=4)

        # --- Center Data Table (Treeview) ---
        table_frame = ttk.Frame(self)
        table_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        columns = ("City", "Date", "Time", "Type", "Amount", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)

        col_widths = {
            "City": 130,
            "Date": 115,
            "Time": 105,
            "Type": 95,
            "Amount": 155,
            "Status": 115,
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths[col], anchor="center")

        # Color-tag rows for Credit vs Debit clarity
        self.tree.tag_configure("credit", foreground="#1b5e20")
        self.tree.tag_configure("debit", foreground="#b71c1c")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Bottom Summary & Export Bar ---
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(side="bottom", fill="x")

        self.lbl_summary = ttk.Label(
            bottom_frame,
            text="Displayed Records: 0  |  Net Impact: PKR 0.00",
            font=("Helvetica", 10, "bold"),
        )
        self.lbl_summary.pack(side="left", padx=5)

        ttk.Button(
            bottom_frame,
            text="Export CSV & Audit Log",
            command=self.handle_export,
        ).pack(side="right", padx=5, ipadx=10, ipady=4)

    def refresh_filter_options(self):
        """Syncs City and Date comboboxes with unique sets from FinPayEngine."""
        engine = self.controller.engine
        cities = ["All"] + sorted(engine.unique_cities)
        dates = ["All"] + sorted(engine.unique_dates)

        self.cb_city["values"] = cities
        self.cb_date["values"] = dates
        self.sync_comboboxes_to_current_filter()

    def sync_comboboxes_to_current_filter(self):
        """Sets the three dropdowns to match engine.current_filter (used after Revert or Clear)."""
        city, date, tx_type = self.controller.engine.current_filter
        self.cb_city.set(city if city in self.cb_city["values"] else "All")
        self.cb_date.set(date if date in self.cb_date["values"] else "All")
        self.cb_type.set(tx_type if tx_type in self.cb_type["values"] else "All")

    def refresh_table(self):
        """Clears Treeview and renders engine.displayed_transactions plus live summary metrics."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        engine = self.controller.engine
        for tx in engine.displayed_transactions:
            if isinstance(tx, CreditTransaction):
                tx_type = "Credit"
                amount_str = f"+ PKR {tx.amount:,.2f}"
                tag = "credit"
            else:
                tx_type = "Debit"
                amount_str = f"- PKR {tx.amount:,.2f}"
                tag = "debit"

            self.tree.insert(
                "",
                tk.END,
                values=(tx.city, tx.date, tx.time, tx_type, amount_str, tx.status),
                tags=(tag,),
            )

        count = len(engine.displayed_transactions)
        net_impact = sum(tx.get_net_impact() for tx in engine.displayed_transactions)
        self.lbl_summary.config(
            text=f"Displayed Records: {count} / {len(engine.all_transactions)}   |   Net Impact: PKR {net_impact:,.2f}"
        )

    def handle_apply_filters(self):
        """Applies selected City, Date, and Type filters and pushes prior state to stack."""
        city = self.cb_city.get()
        date = self.cb_date.get()
        tx_type = self.cb_type.get()

        self.controller.engine.apply_filters(city, date, tx_type)
        self.refresh_table()

    def handle_revert_filter(self):
        """Pops previous filter state from FilterHistoryStack and restores the table."""
        try:
            self.controller.engine.revert_last_filter()
        except IndexError as exc:
            messagebox.showinfo("Nothing to Revert", str(exc))
            return

        self.sync_comboboxes_to_current_filter()
        self.refresh_table()

    def handle_clear_filters(self):
        """Resets all filters to 'All' while preserving undo capability on the stack."""
        self.controller.engine.clear_filters()
        self.sync_comboboxes_to_current_filter()
        self.refresh_table()

    def handle_export(self):
        """Exports current displayed rows to CSV and full linked-list audit trail to TXT."""
        try:
            csv_path, log_path = self.controller.engine.export()
        except RuntimeError as exc:
            messagebox.showerror("Export Failed", str(exc))
            return

        messagebox.showinfo(
            "Export Successful",
            f"Files saved successfully:\n\n"
            f"• Transactions CSV:\n  {csv_path}\n\n"
            f"• Audit Trail Log:\n  {log_path}",
        )


if __name__ == "__main__":
    app = FinPayApp()
    app.mainloop()