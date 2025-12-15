import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


class QuickDeliveryApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("QuickDelivery - Desktopapplicatie")
        self.geometry("900x600")

        # Hoofdcontainer
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # In-memory opslag voor klanten en bestellingen
        self.klanten_data: list[dict] = []
        self.bestellingen_data: list[dict] = []

        # Databaseverbinding (SQLite) voor persistente opslag
        self.db_conn = sqlite3.connect("quickdelivery.db")
        self.db_conn.row_factory = sqlite3.Row
        self._init_database()
        self._load_data_from_database()

        # Eenvoudige dummy-orders voor de planning/route-pagina
        # In een later stadium kun je dit koppelen aan echte bestellingen
        self.dummy_orders: list[dict] = [
            {"id": 1, "klant": "Klant A", "adres": "Straat 1, Stad", "afstand": 5},
            {"id": 2, "klant": "Klant B", "adres": "Straat 2, Stad", "afstand": 12},
            {"id": 3, "klant": "Klant C", "adres": "Straat 3, Stad", "afstand": 3},
            {"id": 4, "klant": "Klant D", "adres": "Straat 4, Stad", "afstand": 9},
        ]

        self._create_header()
        self._create_navigation()
        self._create_content_area()

        # Standaardpagina
        self.show_page("dashboard")

    def _init_database(self) -> None:
        cur = self.db_conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS klanten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                naam TEXT NOT NULL,
                adres TEXT NOT NULL,
                contact TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bestellingen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                klant TEXT NOT NULL,
                ophaal TEXT NOT NULL,
                aflever TEXT NOT NULL,
                datum TEXT,
                status TEXT
            )
            """
        )

        self.db_conn.commit()

    def _load_data_from_database(self) -> None:
        self.klanten_data.clear()
        self.bestellingen_data.clear()

        cur = self.db_conn.cursor()

        for row in cur.execute("SELECT id, naam, adres, contact FROM klanten ORDER BY id"):
            self.klanten_data.append(
                {"id": row["id"], "naam": row["naam"], "adres": row["adres"], "contact": row["contact"]}
            )

        for row in cur.execute(
            "SELECT id, klant, ophaal, aflever, datum, status FROM bestellingen ORDER BY id"
        ):
            self.bestellingen_data.append(
                {
                    "id": row["id"],
                    "klant": row["klant"],
                    "ophaal": row["ophaal"],
                    "aflever": row["aflever"],
                    "datum": row["datum"],
                    "status": row["status"],
                }
            )

    def _create_header(self) -> None:
        header = ttk.Frame(self, padding=(16, 8))
        header.grid(row=0, column=0, sticky="ew")

        title_label = ttk.Label(header, text="QuickDelivery", font=("Segoe UI", 18, "bold"))
        subtitle_label = ttk.Label(header, text="Plannings- en trackingsysteem", font=("Segoe UI", 10))

        title_label.grid(row=0, column=0, sticky="w")
        subtitle_label.grid(row=1, column=0, sticky="w")

    def _create_navigation(self) -> None:
        nav = ttk.Frame(self, padding=(16, 0))
        nav.grid(row=1, column=0, sticky="nw")

        buttons = [
            ("Dashboard", "dashboard"),
            ("Klanten", "klanten"),
            ("Bestellingen", "bestellingen"),
            ("Planning", "planning"),
            ("Tracking", "tracking"),
        ]

        self.nav_buttons = {}

        for idx, (label, page_name) in enumerate(buttons):
            btn = ttk.Button(nav, text=label, command=lambda p=page_name: self.show_page(p))
            btn.grid(row=0, column=idx, padx=(0, 8), pady=(8, 0), sticky="w")
            self.nav_buttons[page_name] = btn

    def _create_content_area(self) -> None:
        content_wrapper = ttk.Frame(self, padding=16)
        content_wrapper.grid(row=2, column=0, sticky="nsew")

        content_wrapper.columnconfigure(0, weight=1)
        content_wrapper.rowconfigure(0, weight=1)

        self.content = ttk.Frame(content_wrapper, padding=16, relief="groove")
        self.content.grid(row=0, column=0, sticky="nsew")

        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def show_page(self, page_name: str) -> None:
        for child in self.content.winfo_children():
            child.destroy()

        if page_name == "dashboard":
            self._build_dashboard_page()
        elif page_name == "klanten":
            self._build_klanten_page()
        elif page_name == "bestellingen":
            self._build_bestellingen_page()
        elif page_name == "planning":
            self._build_planning_page()
        elif page_name == "tracking":
            self._build_tracking_page()

    def _build_dashboard_page(self) -> None:
        title = ttk.Label(self.content, text="Dashboard", font=("Segoe UI", 14, "bold"))
        desc = ttk.Label(
            self.content,
            text=(
                "Welkom bij het QuickDelivery plannings- en trackingsysteem.\n"
                "Gebruik de knoppen bovenin om naar Klanten, Bestellingen, Planning of Tracking te gaan."
            ),
            justify="left",
        )

        title.grid(row=0, column=0, sticky="w")
        desc.grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _build_klanten_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        title = ttk.Label(self.content, text="Klanten", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w")

        form_frame = ttk.Frame(self.content)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Naam *").grid(row=0, column=0, sticky="w")
        self.entry_klant_naam = ttk.Entry(form_frame)
        self.entry_klant_naam.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(form_frame, text="Adres *").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.entry_klant_adres = ttk.Entry(form_frame)
        self.entry_klant_adres.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        ttk.Label(form_frame, text="Contact (telefoon of e-mail)").grid(
            row=2,
            column=0,
            sticky="w",
            pady=(4, 0),
        )
        self.entry_klant_contact = ttk.Entry(form_frame)
        self.entry_klant_contact.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        button_row = ttk.Frame(form_frame)
        button_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        button_row.columnconfigure(0, weight=1)

        delete_button = ttk.Button(button_row, text="Geselecteerde klant verwijderen", command=self._delete_selected_klant)
        delete_button.grid(row=0, column=0, sticky="w")

        add_button = ttk.Button(button_row, text="Toevoegen", command=self._add_klant)
        add_button.grid(row=0, column=1, sticky="e")

        # Overzicht
        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=2, column=0, sticky="nsew")
        self.content.rowconfigure(2, weight=1)

        columns = ("id", "naam", "adres", "contact")
        self.klanten_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10,
        )

        self.klanten_tree.heading("id", text="ID")
        self.klanten_tree.heading("naam", text="Naam")
        self.klanten_tree.heading("adres", text="Adres")
        self.klanten_tree.heading("contact", text="Contact")

        self.klanten_tree.column("id", width=40, anchor="w")
        self.klanten_tree.column("naam", width=160, anchor="w")
        self.klanten_tree.column("adres", width=260, anchor="w")
        self.klanten_tree.column("contact", width=160, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.klanten_tree.yview)
        self.klanten_tree.configure(yscrollcommand=scrollbar.set)

        self.klanten_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self._refresh_klanten_table()

    def _delete_selected_klant(self) -> None:
        if not hasattr(self, "klanten_tree"):
            return

        selected = self.klanten_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een klant in de tabel.")
            return

        item_id = selected[0]
        values = self.klanten_tree.item(item_id, "values")
        klant_id = values[0] if values else None

        if not klant_id:
            return

        if not messagebox.askyesno("Bevestigen", "Weet je zeker dat je deze klant wilt verwijderen?"):
            return

        cur = self.db_conn.cursor()
        cur.execute("DELETE FROM klanten WHERE id = ?", (klant_id,))
        self.db_conn.commit()

        self._load_data_from_database()
        self._refresh_klanten_table()

    def _add_klant(self) -> None:
        naam = self.entry_klant_naam.get().strip()
        adres = self.entry_klant_adres.get().strip()
        contact = self.entry_klant_contact.get().strip()

        if not naam or not adres:
            messagebox.showwarning("Validatie", "Naam en adres zijn verplicht voor een klant.")
            return

        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT INTO klanten (naam, adres, contact) VALUES (?, ?, ?)",
            (naam, adres, contact),
        )
        self.db_conn.commit()

        self._load_data_from_database()

        self.entry_klant_naam.delete(0, tk.END)
        self.entry_klant_adres.delete(0, tk.END)
        self.entry_klant_contact.delete(0, tk.END)

        self._refresh_klanten_table()

    def _refresh_klanten_table(self) -> None:
        if not hasattr(self, "klanten_tree"):
            return

        for row in self.klanten_tree.get_children():
            self.klanten_tree.delete(row)

        for klant in self.klanten_data:
            self.klanten_tree.insert("", tk.END, values=(klant["id"], klant["naam"], klant["adres"], klant["contact"]))

    def _build_bestellingen_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(2, weight=1)

        title = ttk.Label(self.content, text="Bestellingen", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w")

        form_frame = ttk.Frame(self.content)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Klantnaam *").grid(row=0, column=0, sticky="w")
        self.entry_best_klant = ttk.Entry(form_frame)
        self.entry_best_klant.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(form_frame, text="Ophaaladres *").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.entry_best_ophaal = ttk.Entry(form_frame)
        self.entry_best_ophaal.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        ttk.Label(form_frame, text="Afleveradres *").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.entry_best_aflever = ttk.Entry(form_frame)
        self.entry_best_aflever.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        ttk.Label(form_frame, text="Datum (bijv. 2025-12-15)").grid(row=3, column=0, sticky="w", pady=(4, 0))
        self.entry_best_datum = ttk.Entry(form_frame)
        self.entry_best_datum.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        ttk.Label(form_frame, text="Status").grid(row=4, column=0, sticky="w", pady=(4, 0))
        self.combo_best_status = ttk.Combobox(form_frame, state="readonly", values=[
            "Gepland",
            "Onderweg",
            "Afgeleverd",
            "Geannuleerd",
        ])
        self.combo_best_status.set("Gepland")
        self.combo_best_status.grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        add_button = ttk.Button(form_frame, text="Bestelling toevoegen", command=self._add_bestelling)
        add_button.grid(row=5, column=0, columnspan=2, sticky="e", pady=(8, 0))

        # Overzichtstabel
        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=2, column=0, sticky="nsew")

        columns = ("id", "klant", "ophaal", "aflever", "datum", "status")
        self.bestellingen_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.bestellingen_tree.heading("id", text="ID")
        self.bestellingen_tree.heading("klant", text="Klant")
        self.bestellingen_tree.heading("ophaal", text="Ophaaladres")
        self.bestellingen_tree.heading("aflever", text="Afleveradres")
        self.bestellingen_tree.heading("datum", text="Datum")
        self.bestellingen_tree.heading("status", text="Status")

        self.bestellingen_tree.column("id", width=40, anchor="w")
        self.bestellingen_tree.column("klant", width=120, anchor="w")
        self.bestellingen_tree.column("ophaal", width=180, anchor="w")
        self.bestellingen_tree.column("aflever", width=180, anchor="w")
        self.bestellingen_tree.column("datum", width=110, anchor="w")
        self.bestellingen_tree.column("status", width=100, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.bestellingen_tree.yview)
        self.bestellingen_tree.configure(yscrollcommand=scrollbar.set)

        self.bestellingen_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self._refresh_bestellingen_table()

    def _add_bestelling(self) -> None:
        klant = self.entry_best_klant.get().strip()
        ophaal = self.entry_best_ophaal.get().strip()
        aflever = self.entry_best_aflever.get().strip()
        datum = self.entry_best_datum.get().strip()
        status = self.combo_best_status.get().strip() or "Gepland"

        if not klant or not ophaal or not aflever:
            messagebox.showwarning(
                "Validatie",
                "Klantnaam, ophaaladres en afleveradres zijn verplicht voor een bestelling.",
            )
            return

        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT INTO bestellingen (klant, ophaal, aflever, datum, status) VALUES (?, ?, ?, ?, ?)",
            (klant, ophaal, aflever, datum, status),
        )
        self.db_conn.commit()

        self._load_data_from_database()

        self.entry_best_klant.delete(0, tk.END)
        self.entry_best_ophaal.delete(0, tk.END)
        self.entry_best_aflever.delete(0, tk.END)
        self.entry_best_datum.delete(0, tk.END)
        self.combo_best_status.set("Gepland")

        self._refresh_bestellingen_table()
        # Trackingoverzicht ook verversen als er een nieuwe bestelling is
        self._refresh_tracking_table()

    def _delete_selected_bestelling(self) -> None:
        if not hasattr(self, "bestellingen_tree"):
            return

        selected = self.bestellingen_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een bestelling in de tabel.")
            return

        item_id = selected[0]
        values = self.bestellingen_tree.item(item_id, "values")
        best_id = values[0] if values else None

        if not best_id:
            return

        if not messagebox.askyesno("Bevestigen", "Weet je zeker dat je deze bestelling wilt verwijderen?"):
            return

        cur = self.db_conn.cursor()
        cur.execute("DELETE FROM bestellingen WHERE id = ?", (best_id,))
        self.db_conn.commit()

        self._load_data_from_database()
        self._refresh_bestellingen_table()
        self._refresh_tracking_table()

    def _refresh_bestellingen_table(self) -> None:
        if not hasattr(self, "bestellingen_tree"):
            return

        for row in self.bestellingen_tree.get_children():
            self.bestellingen_tree.delete(row)

        for best in self.bestellingen_data:
            self.bestellingen_tree.insert(
                "",
                tk.END,
                values=(
                    best["id"],
                    best["klant"],
                    best["ophaal"],
                    best["aflever"],
                    best["datum"],
                    best["status"],
                ),
            )

    def _build_planning_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(2, weight=1)

        title = ttk.Label(self.content, text="Planning & Routes", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w")

        uitleg = ttk.Label(
            self.content,
            text=(
                "Eenvoudige demo van routeplanning met dummy-orders.\n"
                "Later kun je dit koppelen aan echte bestellingen en chauffeurs."
            ),
            justify="left",
        )
        uitleg.grid(row=1, column=0, sticky="w", pady=(4, 8))

        # Tabel met beschikbare stops (dummy-orders)
        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=2, column=0, sticky="nsew")

        columns = ("id", "klant", "adres", "afstand")
        self.planning_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        self.planning_tree.heading("id", text="ID")
        self.planning_tree.heading("klant", text="Klant")
        self.planning_tree.heading("adres", text="Adres")
        self.planning_tree.heading("afstand", text="Afstand (km)")

        self.planning_tree.column("id", width=40, anchor="w")
        self.planning_tree.column("klant", width=120, anchor="w")
        self.planning_tree.column("adres", width=260, anchor="w")
        self.planning_tree.column("afstand", width=100, anchor="e")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.planning_tree.yview)
        self.planning_tree.configure(yscrollcommand=scroll.set)

        self.planning_tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Knop om een eenvoudige "route" te berekenen
        button_frame = ttk.Frame(self.content)
        button_frame.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        calc_button = ttk.Button(button_frame, text="Bereken eenvoudige route", command=self._calculate_simple_route)
        calc_button.grid(row=0, column=0, sticky="w")

        self.route_result_label = ttk.Label(button_frame, text="")
        self.route_result_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self._refresh_planning_table()

    def _refresh_planning_table(self) -> None:
        if not hasattr(self, "planning_tree"):
            return

        for row in self.planning_tree.get_children():
            self.planning_tree.delete(row)

        for order in self.dummy_orders:
            self.planning_tree.insert("", tk.END, values=(order["id"], order["klant"], order["adres"], order["afstand"]))

    def _calculate_simple_route(self) -> None:
        # Heel eenvoudige "route-optimalisatie": sorteer op afstand (kortste afstand eerst)
        sorted_orders = sorted(self.dummy_orders, key=lambda o: o["afstand"])
        volgorde_ids = [str(o["id"]) for o in sorted_orders]
        totale_afstand = sum(o["afstand"] for o in sorted_orders)

        tekst = f"Voorgestelde volgorde van stops (op basis van afstand): {', '.join(volgorde_ids)}. "
        tekst += f"Totale geschatte afstand: {totale_afstand} km."
        self.route_result_label.config(text=tekst)

    def _build_tracking_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(2, weight=1)

        title = ttk.Label(self.content, text="Tracking & Status", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w")

        uitleg = ttk.Label(
            self.content,
            text=(
                "Overzicht van alle bestellingen en hun actuele status.\n"
                "Gebruik de filter om bijvoorbeeld alleen 'Onderweg' of 'Afgeleverd' te tonen."
            ),
            justify="left",
        )
        uitleg.grid(row=1, column=0, sticky="w", pady=(4, 8))

        # Filter op status
        filter_frame = ttk.Frame(self.content)
        filter_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(filter_frame, text="Filter op status:").grid(row=0, column=0, sticky="w")
        self.combo_track_status = ttk.Combobox(
            filter_frame,
            state="readonly",
            values=["Alle", "Gepland", "Onderweg", "Afgeleverd", "Geannuleerd"],
        )
        self.combo_track_status.set("Alle")
        self.combo_track_status.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.combo_track_status.bind("<<ComboboxSelected>>", lambda _event: self._refresh_tracking_table())

        # Tabel met bestellingen
        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=3, column=0, sticky="nsew")
        self.content.rowconfigure(3, weight=1)

        columns = ("id", "klant", "ophaal", "aflever", "datum", "status")
        self.tracking_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.tracking_tree.heading("id", text="ID")
        self.tracking_tree.heading("klant", text="Klant")
        self.tracking_tree.heading("ophaal", text="Ophaaladres")
        self.tracking_tree.heading("aflever", text="Afleveradres")
        self.tracking_tree.heading("datum", text="Datum")
        self.tracking_tree.heading("status", text="Status")

        self.tracking_tree.column("id", width=40, anchor="w")
        self.tracking_tree.column("klant", width=120, anchor="w")
        self.tracking_tree.column("ophaal", width=180, anchor="w")
        self.tracking_tree.column("aflever", width=180, anchor="w")
        self.tracking_tree.column("datum", width=110, anchor="w")
        self.tracking_tree.column("status", width=100, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tracking_tree.yview)
        self.tracking_tree.configure(yscrollcommand=scrollbar.set)

        self.tracking_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self._refresh_tracking_table()

    def _refresh_tracking_table(self) -> None:
        if not hasattr(self, "tracking_tree"):
            return

        for row in self.tracking_tree.get_children():
            self.tracking_tree.delete(row)

        geselecteerde_status = "Alle"
        if hasattr(self, "combo_track_status"):
            geselecteerde_status = self.combo_track_status.get() or "Alle"

        for best in self.bestellingen_data:
            if geselecteerde_status != "Alle" and best.get("status") != geselecteerde_status:
                continue

            self.tracking_tree.insert(
                "",
                tk.END,
                values=(
                    best["id"],
                    best["klant"],
                    best["ophaal"],
                    best["aflever"],
                    best["datum"],
                    best["status"],
                ),
            )


if __name__ == "__main__":
    app = QuickDeliveryApp()
    app.mainloop()
