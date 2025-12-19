import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import datetime
from itertools import combinations
from pathlib import Path
import shutil
import os
import sys


class QuickDeliveryApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("QuickDelivery - Desktopapplicatie")
        self.geometry("900x600")

        # Script directory
        if getattr(sys, 'frozen', False):
            self.script_dir = Path(sys.executable).parent
        else:
            self.script_dir = Path(__file__).resolve().parent

        # Branding
        self.brand_bg = "#FBF7F1"
        self.brand_surface = "#FFFFFF"
        self.brand_text = "#2D2A26"
        self.brand_accent = "#F07C7C"
        self.brand_accent_dark = "#E45F73"
        self._init_styles()

        self._init_background_texture()

        self._ensure_logo_asset()

        # Hoofdcontainer
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        # Klanten en bestellingen
        self.klanten_data: list[dict] = []
        self.bestellingen_data: list[dict] = []

        self.current_user_email: str | None = None
        self.current_role: str | None = None

        # Database
        db_path = self.script_dir / "quickdelivery.db"
        self.db_conn = sqlite3.connect(str(db_path))
        self.db_conn.row_factory = sqlite3.Row
        self._init_database()
        self._apply_db_migrations()
        self._ensure_seed_users()
        self._load_data_from_database()

        # Dummy orders voor planning
        self.dummy_orders: list[dict] = [
            {"id": 1, "klant": "Klant A", "adres": "Straat 1, Stad", "afstand": 5},
            {"id": 2, "klant": "Klant B", "adres": "Straat 2, Stad", "afstand": 12},
            {"id": 3, "klant": "Klant C", "adres": "Straat 3, Stad", "afstand": 3},
            {"id": 4, "klant": "Klant D", "adres": "Straat 4, Stad", "afstand": 9},
        ]

        self._create_header()
        self._create_navigation()
        self._create_content_area()

        # Start met login
        self.show_page("login")

    def _is_valid_iso_date(self, value: str) -> bool:
        """Validate Dutch date format DD-MM-YYYY."""
        v = (value or "").strip()
        if not v:
            return True
        try:
            datetime.datetime.strptime(v, "%d-%m-%Y")
            return True
        except ValueError:
            return False

    def _convert_date_to_db(self, dutch_date: str) -> str:
        """Convert DD-MM-YYYY to YYYY-MM-DD for database storage."""
        if not dutch_date or not dutch_date.strip():
            return ""
        try:
            dt = datetime.datetime.strptime(dutch_date.strip(), "%d-%m-%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return dutch_date

    def _convert_date_from_db(self, db_date: str) -> str:
        """Convert YYYY-MM-DD from database to DD-MM-YYYY for display."""
        if not db_date or not db_date.strip():
            return ""
        try:
            dt = datetime.datetime.strptime(db_date.strip(), "%Y-%m-%d")
            return dt.strftime("%d-%m-%Y")
        except ValueError:
            return db_date

    def _init_background_texture(self) -> None:
        self._bg_texture_img = None
        self._bg_texture_job = None
        self._bg_texture_last_size = (0, 0)

        self._bg_label = tk.Label(self, bd=0, highlightthickness=0)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self._bg_label.lower()

        self.bind("<Configure>", self._schedule_texture_redraw)
        self.after(0, self._redraw_texture)

    def _schedule_texture_redraw(self, event: tk.Event) -> None:
        if getattr(self, "_bg_texture_job", None) is not None:
            try:
                self.after_cancel(self._bg_texture_job)
            except Exception:
                pass
        self._bg_texture_job = self.after(120, self._redraw_texture)

    def _redraw_texture(self) -> None:
        self._bg_texture_job = None

        w = max(1, int(self.winfo_width()))
        h = max(1, int(self.winfo_height()))
        if (w, h) == getattr(self, "_bg_texture_last_size", (0, 0)):
            return
        self._bg_texture_last_size = (w, h)

        base = self.brand_bg
        dot1 = "#EDE0D8"
        dot2 = "#E7D6CC"

        img = tk.PhotoImage(width=w, height=h)
        img.put(base, to=(0, 0, w, h))

        step = 5
        for y in range(0, h, step):
            for x in range(0, w, step):
                n = (x * 1103515245 + y * 12345 + 67890) & 0xFFFFFFFF
                r = (n >> 16) & 0xFF
                if r < 55:
                    img.put(dot1, to=(x, y, x + 2, y + 2))
                elif r < 80:
                    img.put(dot2, to=(x + 1, y + 1, x + 3, y + 3))

        self._bg_texture_img = img
        self._bg_label.configure(image=self._bg_texture_img)
        self._bg_label.lower()

    def _asset_path(self, filename: str) -> Path:
        return self.script_dir / "assets" / filename

    def _ensure_logo_asset(self) -> None:
        logo_path = self._asset_path("quickdelivery_logo.png")
        logo_path.parent.mkdir(parents=True, exist_ok=True)

        missing_or_empty = (not logo_path.exists()) or (logo_path.exists() and logo_path.stat().st_size == 0)
        if not missing_or_empty:
            return

        if not messagebox.askyesno(
            "Logo instellen",
            "Het logo-bestand ontbreekt of is leeg. Wil je nu het QuickDelivery logo kiezen (PNG)?",
        ):
            return

        src = filedialog.askopenfilename(
            title="Kies QuickDelivery logo (PNG)",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )
        if not src:
            return

        try:
            shutil.copyfile(src, logo_path)
        except OSError:
            messagebox.showerror("Fout", "Kon het logo niet kopiëren naar assets/quickdelivery_logo.png")

    def _init_styles(self) -> None:
        self.configure(background=self.brand_bg)
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background=self.brand_bg)
        style.configure("Surface.TFrame", background=self.brand_surface)
        style.configure("TLabel", background=self.brand_surface, foreground=self.brand_text)
        style.configure("App.TLabel", background=self.brand_bg, foreground=self.brand_text)
        style.configure("Header.TLabel", background=self.brand_bg, foreground=self.brand_text)
        style.configure("TFrame", background=self.brand_surface)
        style.configure("TCheckbutton", background=self.brand_surface, foreground=self.brand_text)
        style.configure("Nav.TFrame", background=self.brand_bg)
        style.configure("NavBar.TFrame", background="#E7DBD5")
        style.configure("Divider.TFrame", background=self.brand_accent)

        style.configure(
            "Accent.TButton",
            background=self.brand_accent,
            foreground="white",
            padding=(12, 6),
            relief="flat",
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.brand_accent_dark), ("pressed", self.brand_accent_dark)],
            foreground=[("disabled", "#FFFFFF")],
        )

        style.configure(
            "Nav.TButton",
            background="#EFE6E0",
            foreground=self.brand_text,
            padding=(18, 10),
            relief="flat",
        )
        style.map(
            "Nav.TButton",
            background=[("active", "#E7DBD5"), ("pressed", "#E2D2CB")],
        )

        style.configure(
            "NavActive.TButton",
            background=self.brand_surface,
            foreground=self.brand_text,
            padding=(18, 10),
            relief="flat",
        )
        style.map(
            "NavActive.TButton",
            background=[("active", self.brand_surface), ("pressed", self.brand_surface)],
        )

        style.configure(
            "Treeview",
            rowheight=26,
            fieldbackground=self.brand_surface,
            background=self.brand_surface,
            foreground=self.brand_text,
        )
        style.configure(
            "Treeview.Heading",
            background="#F3E7E4",
            foreground=self.brand_text,
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", "#EED8D6")])

        self._tracking_auto_refresh_enabled = False
        self._tracking_auto_refresh_ms = 2000
        self._tracking_simulate_enabled = False

    def _estimate_distance_km(self, a: str, b: str) -> float:
        aa = (a or "").strip().lower()
        bb = (b or "").strip().lower()
        if not aa or not bb:
            return 10.0
        if aa == bb:
            return 0.0
        # Afstand schatting op basis van adres
        a_tokens = {t for t in aa.replace(",", " ").split() if t}
        b_tokens = {t for t in bb.replace(",", " ").split() if t}
        common = len(a_tokens & b_tokens)
        base = 12.0
        dist = base - (common * 2.5)
        # Begrenzing
        if dist < 1.0:
            dist = 1.0
        if dist > 25.0:
            dist = 25.0
        return dist

    def _route_length(self, stops: list[dict]) -> float:
        if len(stops) < 2:
            return 0.0
        total = 0.0
        for i in range(len(stops) - 1):
            total += self._estimate_distance_km(stops[i]["adres"], stops[i + 1]["adres"])
        return total

    def _nearest_neighbor_route(self, stops: list[dict]) -> list[dict]:
        if not stops:
            return []
        remaining = stops[1:]
        route = [stops[0]]
        while remaining:
            last = route[-1]
            best_idx = 0
            best_d = float("inf")
            for idx, cand in enumerate(remaining):
                d = self._estimate_distance_km(last["adres"], cand["adres"])
                if d < best_d:
                    best_d = d
                    best_idx = idx
            route.append(remaining.pop(best_idx))
        return route

    def _two_opt(self, route: list[dict], max_passes: int = 50) -> list[dict]:
        if len(route) < 4:
            return route

        best = route[:]
        best_len = self._route_length(best)

        improved = True
        passes = 0
        while improved and passes < max_passes:
            improved = False
            passes += 1
            # Segment grenzen
            for i, j in combinations(range(1, len(best) - 1), 2):
                if j <= i:
                    continue
                candidate = best[:i] + list(reversed(best[i:j + 1])) + best[j + 1 :]
                cand_len = self._route_length(candidate)
                if cand_len + 1e-6 < best_len:
                    best = candidate
                    best_len = cand_len
                    improved = True
                    break
            # Herstart na verbetering
        return best

    def _get_planning_stops_from_bestellingen(self) -> list[dict]:
        # Stops op basis van afleveradressen
        status_filter = "Alle"
        if hasattr(self, "combo_plan_status"):
            status_filter = self.combo_plan_status.get() or "Alle"

        stops: list[dict] = []
        for best in self.bestellingen_data:
            if status_filter != "Alle" and best.get("status") != status_filter:
                continue
            adres = (best.get("aflever") or "").strip()
            if not adres:
                continue
            stops.append({"id": best["id"], "klant": best.get("klant") or "", "adres": adres})
        return stops

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

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chauffeurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                naam TEXT NOT NULL,
                voertuig TEXT,
                beschikbaar INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS status_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bestelling_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                opmerking TEXT,
                FOREIGN KEY(bestelling_id) REFERENCES bestellingen(id)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                chauffeur_id INTEGER,
                FOREIGN KEY(chauffeur_id) REFERENCES chauffeurs(id)
            )
            """
        )

        self.db_conn.commit()

    def _ensure_seed_users(self) -> None:
        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (email, password, role) VALUES (?, ?, ?)",
            ("planner@gmail.com", "wachtwoord", "planner"),
        )
        cur.execute(
            "INSERT OR IGNORE INTO users (email, password, role) VALUES (?, ?, ?)",
            ("chaffeur@gmail.com", "wachtwoord", "chauffeur"),
        )
        cur.execute(
            "INSERT OR IGNORE INTO users (email, password, role) VALUES (?, ?, ?)",
            ("klant@gmail.com", "wachtwoord", "klant"),
        )
        cur.execute(
            "INSERT OR IGNORE INTO users (email, password, role) VALUES (?, ?, ?)",
            ("manager@gmail.com", "wachtwoord", "manager"),
        )
        self.db_conn.commit()

        # Test chauffeur
        row = cur.execute("SELECT id FROM chauffeurs WHERE naam = 'Test Chauffeur'").fetchone()
        if not row:
            cur.execute("INSERT INTO chauffeurs (naam, voertuig, beschikbaar) VALUES (?, ?, ?)", ("Test Chauffeur", "Bestelbus", 1))
            self.db_conn.commit()
            row = cur.execute("SELECT id FROM chauffeurs WHERE naam = 'Test Chauffeur'").fetchone()
        if row:
            cur.execute("UPDATE users SET chauffeur_id = ? WHERE lower(email) = 'chaffeur@gmail.com' AND (chauffeur_id IS NULL OR chauffeur_id != ?)", (row[0], row[0]))
            self.db_conn.commit()

        # Test klanten
        test_klanten = [
            ("Klant 1", "Hoofdstraat 10, Amsterdam", "06-12345671"),
            ("Klant 2", "Kerkstraat 25, Rotterdam", "06-12345672"),
            ("Klant 3", "Marktplein 5, Utrecht", "06-12345673"),
        ]
        for naam, adres, contact in test_klanten:
            existing = cur.execute("SELECT id FROM klanten WHERE naam = ?", (naam,)).fetchone()
            if not existing:
                cur.execute("INSERT INTO klanten (naam, adres, contact) VALUES (?, ?, ?)", (naam, adres, contact))
        self.db_conn.commit()

    def _get_user_by_email(self, email: str) -> dict | None:
        cur = self.db_conn.cursor()
        row = cur.execute(
            "SELECT id, email, password, role, chauffeur_id FROM users WHERE lower(email) = lower(?)",
            (email,),
        ).fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "email": row[1],
            "password": row[2],
            "role": row[3],
            "chauffeur_id": row[4],
        }

    def _apply_db_migrations(self) -> None:
        # Database migratie
        cur = self.db_conn.cursor()
        cols = cur.execute("PRAGMA table_info(bestellingen)").fetchall()
        existing = {c[1] for c in cols}
        if "chauffeur_id" not in existing:
            cur.execute("ALTER TABLE bestellingen ADD COLUMN chauffeur_id INTEGER")
            self.db_conn.commit()

    def _load_data_from_database(self) -> None:
        self.klanten_data.clear()
        self.bestellingen_data.clear()
        self.chauffeurs_data: list[dict] = []

        cur = self.db_conn.cursor()

        for row in cur.execute("SELECT id, naam, adres, contact FROM klanten ORDER BY id"):
            self.klanten_data.append(
                {"id": row["id"], "naam": row["naam"], "adres": row["adres"], "contact": row["contact"]}
            )

        for row in cur.execute(
            "SELECT id, klant, ophaal, aflever, datum, status, chauffeur_id FROM bestellingen ORDER BY id"
        ):
            self.bestellingen_data.append(
                {
                    "id": row["id"],
                    "klant": row["klant"],
                    "ophaal": row["ophaal"],
                    "aflever": row["aflever"],
                    "datum": row["datum"],
                    "status": row["status"],
                    "chauffeur_id": row["chauffeur_id"],
                }
            )

        for row in cur.execute("SELECT id, naam, voertuig, beschikbaar FROM chauffeurs ORDER BY id"):
            self.chauffeurs_data.append(
                {
                    "id": row["id"],
                    "naam": row["naam"],
                    "voertuig": row["voertuig"],
                    "beschikbaar": bool(row["beschikbaar"]),
                }
            )

    def _now_iso(self) -> str:
        cur = self.db_conn.cursor()
        row = cur.execute("SELECT datetime('now','localtime')").fetchone()
        return row[0] if row else ""

    def _log_status_event(self, bestelling_id: int, status: str, opmerking: str | None = None) -> None:
        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT INTO status_events (bestelling_id, status, timestamp, opmerking) VALUES (?, ?, ?, ?)",
            (bestelling_id, status, self._now_iso(), opmerking or ""),
        )
        self.db_conn.commit()

    def _get_status_events_for_bestelling(self, bestelling_id: int) -> list[dict]:
        cur = self.db_conn.cursor()
        rows = cur.execute(
            "SELECT id, bestelling_id, status, timestamp, opmerking FROM status_events WHERE bestelling_id = ? ORDER BY id DESC",
            (bestelling_id,),
        ).fetchall()
        events: list[dict] = []
        for r in rows:
            events.append(
                {
                    "id": r["id"],
                    "bestelling_id": r["bestelling_id"],
                    "status": r["status"],
                    "timestamp": r["timestamp"],
                    "opmerking": r["opmerking"],
                }
            )
        return events

    def _create_header(self) -> None:
        header = ttk.Frame(self, padding=(16, 8), style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew")

        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=0)

        # Logo
        self._header_logo_img = None
        logo_path = self._asset_path("quickdelivery_logo.png")
        if logo_path.exists() and logo_path.stat().st_size > 0:
            try:
                img = tk.PhotoImage(file=str(logo_path))
                # Logo schalen
                try:
                    max_h = 96
                    max_w = 180

                    h = img.height() or 0
                    w = img.width() or 0

                    if h > 0 and w > 0:
                        factor_h = int((h + max_h - 1) / max_h) if h > max_h else 1
                        factor_w = int((w + max_w - 1) / max_w) if w > max_w else 1
                        factor = max(1, factor_h, factor_w)
                        if factor > 1:
                            img = img.subsample(factor, factor)
                except Exception:
                    pass

                self._header_logo_img = img
                ttk.Label(header, image=self._header_logo_img, style="Header.TLabel").grid(
                    row=0, column=0, rowspan=2, sticky="w", padx=(0, 12)
                )

                # Window icon
                try:
                    self.iconphoto(True, self._header_logo_img)
                except tk.TclError:
                    pass
            except tk.TclError:
                self._header_logo_img = None

        title_label = ttk.Label(header, text="QuickDelivery", font=("Segoe UI", 18, "bold"), style="Header.TLabel")
        subtitle_label = ttk.Label(
            header,
            text="Plannings- en trackingsysteem",
            font=("Segoe UI", 10),
            style="Header.TLabel",
        )

        title_label.grid(row=0, column=1, sticky="w")
        subtitle_label.grid(row=1, column=1, sticky="w")

        self.btn_logout = ttk.Button(header, text="Uitloggen", command=self._logout)
        self.btn_logout.grid(row=0, column=2, rowspan=2, sticky="e")
        self.btn_logout.grid_remove()

    def _create_navigation(self) -> None:
        self._rebuild_navigation()

    def _pages_for_role(self, role: str | None) -> list[tuple[str, str]]:
        if role == "planner":
            return [
                ("Dashboard", "dashboard"),
                ("Klanten", "klanten"),
                ("Chauffeurs", "chauffeurs"),
                ("Bestellingen", "bestellingen"),
                ("Planning", "planning"),
                ("Tracking", "tracking"),
            ]
        if role == "chauffeur":
            return [
                ("Chauffeur", "chauffeur"),
            ]
        if role == "manager":
            return [
                ("Manager", "manager"),
            ]
        if role == "klant":
            return [
                ("Klant", "klant"),
            ]
        return []

    def _rebuild_navigation(self) -> None:
        if hasattr(self, "nav_bar") and self.nav_bar.winfo_exists():
            self.nav_bar.destroy()

        self.nav_bar = ttk.Frame(self, padding=0, style="NavBar.TFrame")
        self.nav_bar.grid(row=1, column=0, sticky="ew")
        self.nav_bar.columnconfigure(0, weight=1)

        nav = ttk.Frame(self.nav_bar, padding=(16, 0), style="NavBar.TFrame")
        nav.grid(row=0, column=0, sticky="ew")

        buttons = self._pages_for_role(self.current_role)
        self.nav_buttons = {}

        if not buttons:
            divider = ttk.Frame(self.nav_bar, height=3, style="Divider.TFrame")
            divider.grid(row=1, column=0, sticky="ew", pady=(8, 0))
            return

        for idx in range(len(buttons)):
            nav.columnconfigure(idx, weight=1, uniform="nav")

        for idx, (label, page_name) in enumerate(buttons):
            btn = ttk.Button(nav, text=label, command=lambda p=page_name: self.show_page(p), style="Nav.TButton")
            btn.grid(row=0, column=idx, padx=(0, 10), pady=(8, 0), sticky="ew")
            self.nav_buttons[page_name] = btn

        divider = ttk.Frame(self.nav_bar, height=3, style="Divider.TFrame")
        divider.grid(row=1, column=0, sticky="ew", pady=(8, 0))

    def _create_content_area(self) -> None:
        content_wrapper = ttk.Frame(self, padding=16, style="App.TFrame")
        content_wrapper.grid(row=2, column=0, sticky="nsew")

        content_wrapper.columnconfigure(0, weight=1)
        content_wrapper.rowconfigure(0, weight=1)

        self.content = ttk.Frame(content_wrapper, padding=16, relief="groove", style="Surface.TFrame")
        self.content.grid(row=0, column=0, sticky="nsew")

        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def show_page(self, page_name: str) -> None:
        self.content.columnconfigure(0, weight=1)
        for i in range(0, 10):
            self.content.rowconfigure(i, weight=0)

        for child in self.content.winfo_children():
            child.destroy()

        if page_name != "login" and not self.current_role:
            page_name = "login"

        if page_name == "login":
            self._build_login_page()
        elif page_name == "dashboard":
            self._build_dashboard_page()
        elif page_name == "klanten":
            self._build_klanten_page()
        elif page_name == "chauffeurs":
            self._build_chauffeurs_page()
        elif page_name == "bestellingen":
            self._build_bestellingen_page()
        elif page_name == "planning":
            self._build_planning_page()
        elif page_name == "tracking":
            self._build_tracking_page()
        elif page_name == "chauffeur":
            self._build_chauffeur_page()
        elif page_name == "manager":
            self._build_manager_page()
        elif page_name == "klant":
            self._build_klant_page()

        self._set_active_nav(page_name)

        if hasattr(self, "btn_logout"):
            if self.current_role and page_name != "login":
                self.btn_logout.grid()
            else:
                self.btn_logout.grid_remove()

    def _set_active_nav(self, active_page: str) -> None:
        for page_name, btn in getattr(self, "nav_buttons", {}).items():
            btn.configure(style="NavActive.TButton" if page_name == active_page else "Nav.TButton")

    def _build_login_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=0)
        self.content.rowconfigure(1, weight=0)

        title = ttk.Label(self.content, text="Inloggen", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w")

        form = ttk.Frame(self.content)
        form.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="E-mail").grid(row=0, column=0, sticky="w")
        self.entry_login_email = ttk.Entry(form)
        self.entry_login_email.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(form, text="Wachtwoord").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.entry_login_password = ttk.Entry(form, show="*")
        self.entry_login_password.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))

        login_btn = ttk.Button(form, text="Inloggen", command=self._login)
        login_btn.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))

        hint = ttk.Label(
            self.content,
            text=(
                "Test accounts:\n"
                "planner@gmail.com / wachtwoord\n"
                "chaffeur@gmail.com / wachtwoord\n"
                "klant@gmail.com / wachtwoord\n"
                "manager@gmail.com / wachtwoord"
            ),
            justify="left",
        )
        hint.grid(row=2, column=0, sticky="w", pady=(12, 0))

    def _login(self) -> None:
        email = (self.entry_login_email.get() or "").strip().lower() if hasattr(self, "entry_login_email") else ""
        pw = (self.entry_login_password.get() or "").strip() if hasattr(self, "entry_login_password") else ""

        user = self._get_user_by_email(email)
        if not user or user.get("password") != pw:
            messagebox.showerror("Inloggen mislukt", "Onjuiste e-mail of wachtwoord.")
            return

        self.current_user_email = user.get("email")
        self.current_role = user.get("role")
        self.current_chauffeur_id = user.get("chauffeur_id")
        self._rebuild_navigation()

        if self.current_role == "planner":
            self.show_page("dashboard")
        elif self.current_role == "chauffeur":
            self.show_page("chauffeur")
        elif self.current_role == "manager":
            self.show_page("manager")
        elif self.current_role == "klant":
            self.show_page("klant")
        else:
            self.show_page("dashboard")

    def _logout(self) -> None:
        self.current_user_email = None
        self.current_role = None
        self.current_chauffeur_id = None
        self._rebuild_navigation()
        self.show_page("login")

    def _build_chauffeur_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        title = ttk.Label(self.content, text="Chauffeur Dashboard", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 12))

        # Main dashboard container
        main_frame = ttk.Frame(self.content)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # LEFT PANEL - Stats & Info
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_panel.columnconfigure(0, weight=1)

        # Dashboard summary
        self._load_data_from_database()
        deliveries = self._get_chauffeur_deliveries_sorted()
        active = [d for d in deliveries if not d.get("is_done")]
        done = [d for d in deliveries if d.get("is_done")]

        chauffeur_name = ""
        voertuig = ""
        if self.current_chauffeur_id:
            ch = next((c for c in getattr(self, "chauffeurs_data", []) if c.get("id") == self.current_chauffeur_id), None)
            if ch:
                chauffeur_name = ch.get("naam", "")
                voertuig = ch.get("voertuig", "")

        # Welcome card
        welcome_card = ttk.LabelFrame(left_panel, text="Welkom")
        welcome_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        welcome_card.columnconfigure(0, weight=1)

        ttk.Label(welcome_card, text=chauffeur_name or "Chauffeur", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))
        ttk.Label(welcome_card, text=f"Voertuig: {voertuig or 'Niet ingesteld'}", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))

        # Stats card
        stats_card = ttk.LabelFrame(left_panel, text="Vandaag")
        stats_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        stats_card.columnconfigure(1, weight=1)

        ttk.Label(stats_card, text="Totaal leveringen:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        ttk.Label(stats_card, text=str(len(deliveries)), font=("Segoe UI", 12, "bold")).grid(row=0, column=1, sticky="e", padx=12, pady=(8, 2))

        ttk.Label(stats_card, text="Afgerond:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=12, pady=2)
        ttk.Label(stats_card, text=str(len(done)), font=("Segoe UI", 12, "bold"), foreground="#27AE60").grid(row=1, column=1, sticky="e", padx=12, pady=2)

        ttk.Label(stats_card, text="Nog te doen:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=12, pady=2)
        ttk.Label(stats_card, text=str(len(active)), font=("Segoe UI", 12, "bold"), foreground="#E67E22").grid(row=2, column=1, sticky="e", padx=12, pady=2)

        # Progress
        progress_pct = 0
        if len(deliveries) > 0:
            progress_pct = int((len(done) / len(deliveries)) * 100)
        ttk.Label(stats_card, text=f"Voortgang: {progress_pct}%", font=("Segoe UI", 10)).grid(row=3, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 8))

        # Next delivery card
        next_card = ttk.LabelFrame(left_panel, text="Volgende Levering")
        next_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        next_card.columnconfigure(0, weight=1)

        if active:
            next_del = active[0]
            ttk.Label(next_card, text=next_del['klant'], font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
            ttk.Label(next_card, text=next_del['adres'], font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=12, pady=2)
            ttk.Label(next_card, text=f"ETA: {next_del['eta']}", font=("Segoe UI", 10, "bold"), foreground="#E67E22").grid(row=2, column=0, sticky="w", padx=12, pady=(2, 8))
        else:
            ttk.Label(next_card, text="Alle leveringen afgerond!", font=("Segoe UI", 11), foreground="#27AE60").grid(row=0, column=0, sticky="w", padx=12, pady=12)

        # Action buttons in left panel
        action_card = ttk.LabelFrame(left_panel, text="Acties")
        action_card.grid(row=3, column=0, sticky="ew")
        action_card.columnconfigure(0, weight=1)
        action_card.columnconfigure(1, weight=1)

        self.btn_chauffeur_onderweg = ttk.Button(action_card, text="Markeer Onderweg", command=lambda: self._chauffeur_update_status("Onderweg"))
        self.btn_chauffeur_onderweg.grid(row=0, column=0, sticky="ew", padx=(12, 4), pady=12)

        self.btn_chauffeur_afgeleverd = ttk.Button(action_card, text="Markeer Afgeleverd", command=lambda: self._chauffeur_update_status("Afgeleverd"))
        self.btn_chauffeur_afgeleverd.grid(row=0, column=1, sticky="ew", padx=(4, 12), pady=12)

        refresh_btn = ttk.Button(action_card, text="Ververs", command=self._refresh_chauffeur_deliveries)
        refresh_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

        # RIGHT PANEL - Deliveries table
        right_panel = ttk.LabelFrame(main_frame, text="Mijn Leveringen")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        columns = ("volgorde", "id", "klant", "adres", "eta", "status")
        self.chauffeur_tree = ttk.Treeview(right_panel, columns=columns, show="headings", height=14)
        self.chauffeur_tree.heading("volgorde", text="#")
        self.chauffeur_tree.heading("id", text="ID")
        self.chauffeur_tree.heading("klant", text="Klant")
        self.chauffeur_tree.heading("adres", text="Afleveradres")
        self.chauffeur_tree.heading("eta", text="ETA")
        self.chauffeur_tree.heading("status", text="Status")

        self.chauffeur_tree.column("volgorde", width=40, anchor="center")
        self.chauffeur_tree.column("id", width=50, anchor="w")
        self.chauffeur_tree.column("klant", width=120, anchor="w")
        self.chauffeur_tree.column("adres", width=200, anchor="w")
        self.chauffeur_tree.column("eta", width=70, anchor="w")
        self.chauffeur_tree.column("status", width=90, anchor="w")

        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.chauffeur_tree.yview)
        self.chauffeur_tree.configure(yscrollcommand=scrollbar.set)
        self.chauffeur_tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)

        # Tag for delivered items
        self.chauffeur_tree.tag_configure("delivered", foreground="#888888")

        self._refresh_chauffeur_deliveries()

    def _get_chauffeur_deliveries_sorted(self) -> list[dict]:
        """Get deliveries for current chauffeur, sorted by optimized route order with ETA."""
        if not self.current_chauffeur_id:
            return []

        # Filter bestellingen voor deze chauffeur
        my_orders = [b for b in self.bestellingen_data if b.get("chauffeur_id") == self.current_chauffeur_id]
        if not my_orders:
            return []

        # Separate active vs completed
        active = [b for b in my_orders if b.get("status") not in ("Afgeleverd", "Geannuleerd")]
        completed = [b for b in my_orders if b.get("status") in ("Afgeleverd", "Geannuleerd")]

        # Build stops for route optimization (active only)
        stops = []
        for b in active:
            adres = (b.get("aflever") or "").strip()
            if adres:
                stops.append({"id": b["id"], "klant": b.get("klant", ""), "adres": adres, "order": b})

        # Optimize route
        if stops:
            initial = self._nearest_neighbor_route(stops)
            optimized = self._two_opt(initial)
        else:
            optimized = []

        # Bereken ETA
        result = []
        current_time_minutes = 8 * 60  # 08:00
        prev_adres = "Depot"

        for idx, stop in enumerate(optimized):
            dist = self._estimate_distance_km(prev_adres, stop["adres"])
            travel_min = int((dist / 30) * 60)
            current_time_minutes += travel_min
            eta_h = current_time_minutes // 60
            eta_m = current_time_minutes % 60
            eta_str = f"{eta_h:02d}:{eta_m:02d}"

            order = stop["order"]
            result.append({
                "volgorde": idx + 1,
                "id": order["id"],
                "klant": order.get("klant", ""),
                "adres": stop["adres"],
                "eta": eta_str,
                "status": order.get("status", ""),
                "is_done": False,
            })

            current_time_minutes += 5
            prev_adres = stop["adres"]

        # Add completed at the end
        for b in completed:
            result.append({
                "volgorde": "-",
                "id": b["id"],
                "klant": b.get("klant", ""),
                "adres": b.get("aflever", ""),
                "eta": "-",
                "status": b.get("status", ""),
                "is_done": True,
            })

        return result

    def _refresh_chauffeur_deliveries(self) -> None:
        if not hasattr(self, "chauffeur_tree"):
            return

        for row in self.chauffeur_tree.get_children():
            self.chauffeur_tree.delete(row)

        self._load_data_from_database()
        deliveries = self._get_chauffeur_deliveries_sorted()

        for d in deliveries:
            tags = ("delivered",) if d["is_done"] else ()
            self.chauffeur_tree.insert(
                "",
                tk.END,
                values=(d["volgorde"], d["id"], d["klant"], d["adres"], d["eta"], d["status"]),
                tags=tags,
            )

    def _chauffeur_update_status(self, new_status: str) -> None:
        if not hasattr(self, "chauffeur_tree"):
            return

        selected = self.chauffeur_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een levering in de tabel.")
            return

        values = self.chauffeur_tree.item(selected[0], "values")
        best_id = int(values[1]) if values and len(values) > 1 else None
        if not best_id:
            return

        cur = self.db_conn.cursor()
        cur.execute("UPDATE bestellingen SET status = ? WHERE id = ?", (new_status, best_id))
        self.db_conn.commit()
        self._log_status_event(best_id, new_status, "Chauffeur update")

        self._refresh_chauffeur_deliveries()

    def _build_manager_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        title = ttk.Label(self.content, text="Manager Dashboard", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Tab buttons
        tab_frame = ttk.Frame(self.content)
        tab_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self._manager_current_tab = getattr(self, "_manager_current_tab", "dashboard")

        btn_dashboard = ttk.Button(tab_frame, text="Dashboard", command=lambda: self._switch_manager_tab("dashboard"))
        btn_dashboard.grid(row=0, column=0, sticky="w", padx=(0, 8))

        btn_users = ttk.Button(tab_frame, text="Gebruikersbeheer", command=lambda: self._switch_manager_tab("users"))
        btn_users.grid(row=0, column=1, sticky="w")

        # Tab content container
        self.manager_tab_content = ttk.Frame(self.content)
        self.manager_tab_content.grid(row=2, column=0, sticky="nsew")
        self.manager_tab_content.columnconfigure(0, weight=1)
        self.manager_tab_content.rowconfigure(0, weight=1)
        self.content.rowconfigure(2, weight=1)

        self._switch_manager_tab(self._manager_current_tab)

    def _switch_manager_tab(self, tab_name: str) -> None:
        self._manager_current_tab = tab_name
        for child in self.manager_tab_content.winfo_children():
            child.destroy()

        if tab_name == "dashboard":
            self._build_manager_dashboard_tab()
        elif tab_name == "users":
            self._build_manager_users_tab()

    def _build_manager_dashboard_tab(self) -> None:
        self.manager_tab_content.columnconfigure(0, weight=1)
        self.manager_tab_content.rowconfigure(0, weight=1)

        # Main dashboard container
        main_frame = ttk.Frame(self.manager_tab_content)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        stats = self._calculate_manager_stats()
        perf = self._calculate_chauffeur_performance()

        # LEFT PANEL - Stats & KPIs
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_panel.columnconfigure(0, weight=1)

        # Overview card
        overview_card = ttk.LabelFrame(left_panel, text="Overzicht")
        overview_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        overview_card.columnconfigure(1, weight=1)

        ttk.Label(overview_card, text="Totaal bestellingen:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        ttk.Label(overview_card, text=str(stats['totaal']), font=("Segoe UI", 12, "bold")).grid(row=0, column=1, sticky="e", padx=12, pady=(8, 2))

        ttk.Label(overview_card, text="Afgeleverd:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=12, pady=2)
        ttk.Label(overview_card, text=str(stats['afgeleverd']), font=("Segoe UI", 12, "bold"), foreground="#27AE60").grid(row=1, column=1, sticky="e", padx=12, pady=2)

        ttk.Label(overview_card, text="Onderweg:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=12, pady=2)
        ttk.Label(overview_card, text=str(stats['onderweg']), font=("Segoe UI", 12, "bold"), foreground="#E67E22").grid(row=2, column=1, sticky="e", padx=12, pady=2)

        ttk.Label(overview_card, text="Gepland:", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", padx=12, pady=2)
        ttk.Label(overview_card, text=str(stats['gepland']), font=("Segoe UI", 12, "bold"), foreground="#666666").grid(row=3, column=1, sticky="e", padx=12, pady=2)

        ttk.Label(overview_card, text="Geannuleerd:", font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", padx=12, pady=(2, 8))
        ttk.Label(overview_card, text=str(stats['geannuleerd']), font=("Segoe UI", 12, "bold"), foreground="#C0392B").grid(row=4, column=1, sticky="e", padx=12, pady=(2, 8))

        # Success rate card
        success_card = ttk.LabelFrame(left_panel, text="Succes Ratio")
        success_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        success_card.columnconfigure(0, weight=1)

        success_rate = 0
        if stats['totaal'] > 0:
            success_rate = round((stats['afgeleverd'] / stats['totaal']) * 100, 1)
        color = "#27AE60" if success_rate >= 80 else "#E67E22" if success_rate >= 50 else "#C0392B"
        ttk.Label(success_card, text=f"{success_rate}%", font=("Segoe UI", 24, "bold"), foreground=color).grid(row=0, column=0, padx=12, pady=12)

        # Top performers card
        top_card = ttk.LabelFrame(left_panel, text="Top Prestaties")
        top_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        top_card.columnconfigure(1, weight=1)

        if perf:
            best = max((p for p in perf if p['afgeleverd'] > 0), key=lambda x: x['afgeleverd'], default=None)
            if best:
                ttk.Label(top_card, text="Meeste leveringen:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
                ttk.Label(top_card, text=best['chauffeur'], font=("Segoe UI", 10, "bold"), foreground="#27AE60").grid(row=0, column=1, sticky="e", padx=12, pady=(8, 2))
                ttk.Label(top_card, text=f"{best['afgeleverd']} leveringen", font=("Segoe UI", 9)).grid(row=1, column=1, sticky="e", padx=12, pady=(0, 8))

            busy = max((p for p in perf if p['onderweg'] > 0), key=lambda x: x['onderweg'], default=None)
            if busy:
                ttk.Label(top_card, text="Meest actief:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=12, pady=(8, 2))
                ttk.Label(top_card, text=busy['chauffeur'], font=("Segoe UI", 10, "bold"), foreground="#E67E22").grid(row=2, column=1, sticky="e", padx=12, pady=(8, 2))
                ttk.Label(top_card, text=f"{busy['onderweg']} onderweg", font=("Segoe UI", 9)).grid(row=3, column=1, sticky="e", padx=12, pady=(0, 8))
        else:
            ttk.Label(top_card, text="Geen data beschikbaar", font=("Segoe UI", 10), foreground="#666666").grid(row=0, column=0, padx=12, pady=12)

        # Actions card
        action_card = ttk.LabelFrame(left_panel, text="Acties")
        action_card.grid(row=3, column=0, sticky="ew")
        action_card.columnconfigure(0, weight=1)

        refresh_btn = ttk.Button(action_card, text="Ververs", command=self._refresh_manager_stats)
        refresh_btn.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))

        export_btn = ttk.Button(action_card, text="Export CSV", command=self._export_manager_csv)
        export_btn.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 12))

        # RIGHT PANEL - Chauffeur performance table
        right_panel = ttk.LabelFrame(main_frame, text="Chauffeur Prestaties")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        columns = ("chauffeur", "totaal", "afgeleverd", "onderweg", "gepland", "gem_levertijd")
        self.manager_tree = ttk.Treeview(right_panel, columns=columns, show="headings", height=14)
        self.manager_tree.heading("chauffeur", text="Chauffeur")
        self.manager_tree.heading("totaal", text="Totaal")
        self.manager_tree.heading("afgeleverd", text="Afgeleverd")
        self.manager_tree.heading("onderweg", text="Onderweg")
        self.manager_tree.heading("gepland", text="Gepland")
        self.manager_tree.heading("gem_levertijd", text="Gem. tijd")

        self.manager_tree.column("chauffeur", width=140, anchor="w")
        self.manager_tree.column("totaal", width=60, anchor="center")
        self.manager_tree.column("afgeleverd", width=80, anchor="center")
        self.manager_tree.column("onderweg", width=80, anchor="center")
        self.manager_tree.column("gepland", width=60, anchor="center")
        self.manager_tree.column("gem_levertijd", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.manager_tree.yview)
        self.manager_tree.configure(yscrollcommand=scrollbar.set)
        self.manager_tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)

        self._refresh_manager_stats()

    def _build_manager_users_tab(self) -> None:
        self.manager_tab_content.columnconfigure(0, weight=1)
        self.manager_tab_content.rowconfigure(1, weight=1)

        # Form for creating new users
        form_frame = ttk.LabelFrame(self.manager_tab_content, text="Nieuw Account Aanmaken")
        form_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="E-mail:").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        self.entry_manager_user_email = ttk.Entry(form_frame)
        self.entry_manager_user_email.grid(row=0, column=1, sticky="ew", padx=(8, 12), pady=(12, 4))

        ttk.Label(form_frame, text="Wachtwoord:").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        self.entry_manager_user_password = ttk.Entry(form_frame, show="*")
        self.entry_manager_user_password.grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=4)

        ttk.Label(form_frame, text="Rol:").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        self.combo_manager_user_role = ttk.Combobox(form_frame, state="readonly", values=["klant", "planner", "chauffeur", "manager"])
        self.combo_manager_user_role.set("klant")
        self.combo_manager_user_role.grid(row=2, column=1, sticky="ew", padx=(8, 12), pady=4)

        btn_create = ttk.Button(form_frame, text="Account Aanmaken", command=self._manager_create_user)
        btn_create.grid(row=3, column=0, columnspan=2, sticky="e", padx=12, pady=(8, 12))

        # List of existing users
        list_frame = ttk.LabelFrame(self.manager_tab_content, text="Bestaande Gebruikers")
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("id", "email", "role")
        self.manager_users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.manager_users_tree.heading("id", text="ID")
        self.manager_users_tree.heading("email", text="E-mail")
        self.manager_users_tree.heading("role", text="Rol")

        self.manager_users_tree.column("id", width=50, anchor="w")
        self.manager_users_tree.column("email", width=250, anchor="w")
        self.manager_users_tree.column("role", width=100, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.manager_users_tree.yview)
        self.manager_users_tree.configure(yscrollcommand=scrollbar.set)
        self.manager_users_tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

        ttk.Button(btn_frame, text="Verwijder Geselecteerde", command=self._manager_delete_user).grid(row=0, column=0, sticky="w")
        ttk.Button(btn_frame, text="Ververs", command=self._refresh_manager_users).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self._refresh_manager_users()

    def _manager_create_user(self) -> None:
        email = (self.entry_manager_user_email.get() or "").strip().lower()
        pw = (self.entry_manager_user_password.get() or "").strip()
        role = (self.combo_manager_user_role.get() or "").strip()

        if not email or not pw or not role:
            messagebox.showwarning("Validatie", "Alle velden zijn verplicht.")
            return

        if "@" not in email:
            messagebox.showwarning("Validatie", "Voer een geldig e-mailadres in.")
            return

        if len(pw) < 6:
            messagebox.showwarning("Validatie", "Wachtwoord moet minimaal 6 tekens zijn.")
            return

        # Check bestaand account
        existing = self._get_user_by_email(email)
        if existing:
            messagebox.showerror("Account bestaat al", "Dit e-mailadres is al geregistreerd.")
            return

        # Account aanmaken
        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (email, pw, role),
        )
        self.db_conn.commit()

        messagebox.showinfo("Succes", f"Account aangemaakt voor {email} met rol {role}.")
        
        # Formulier leegmaken
        self.entry_manager_user_email.delete(0, tk.END)
        self.entry_manager_user_password.delete(0, tk.END)
        self.combo_manager_user_role.set("klant")
        
        self._refresh_manager_users()

    def _manager_delete_user(self) -> None:
        if not hasattr(self, "manager_users_tree"):
            return

        selected = self.manager_users_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een gebruiker.")
            return

        values = self.manager_users_tree.item(selected[0], "values")
        user_id = int(values[0]) if values else None
        email = values[1] if len(values) > 1 else ""

        if not user_id:
            return

        # Eigen account niet verwijderen
        if email.lower() == self.current_user_email.lower():
            messagebox.showerror("Fout", "Je kunt je eigen account niet verwijderen.")
            return

        if not messagebox.askyesno("Bevestigen", f"Weet je zeker dat je het account {email} wilt verwijderen?"):
            return

        cur = self.db_conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.db_conn.commit()

        self._refresh_manager_users()

    def _refresh_manager_users(self) -> None:
        if not hasattr(self, "manager_users_tree"):
            return

        for row in self.manager_users_tree.get_children():
            self.manager_users_tree.delete(row)

        cur = self.db_conn.cursor()
        rows = cur.execute("SELECT id, email, role FROM users ORDER BY role, email").fetchall()

        for row in rows:
            self.manager_users_tree.insert("", tk.END, values=(row[0], row[1], row[2]))

    def _calculate_manager_stats(self) -> dict:
        self._load_data_from_database()

        totaal = len(self.bestellingen_data)
        afgeleverd = sum(1 for b in self.bestellingen_data if b.get("status") == "Afgeleverd")
        onderweg = sum(1 for b in self.bestellingen_data if b.get("status") == "Onderweg")
        gepland = sum(1 for b in self.bestellingen_data if b.get("status") == "Gepland")
        geannuleerd = sum(1 for b in self.bestellingen_data if b.get("status") == "Geannuleerd")

        return {
            "totaal": totaal,
            "afgeleverd": afgeleverd,
            "onderweg": onderweg,
            "gepland": gepland,
            "geannuleerd": geannuleerd,
        }

    def _calculate_chauffeur_performance(self) -> list[dict]:
        chauffeur_map = {c["id"]: c["naam"] for c in getattr(self, "chauffeurs_data", [])}

        # Groepeer per chauffeur
        perf: dict[int | None, dict] = {}
        for best in self.bestellingen_data:
            ch_id = best.get("chauffeur_id")
            if ch_id not in perf:
                perf[ch_id] = {"totaal": 0, "afgeleverd": 0, "onderweg": 0, "gepland": 0, "levertijden": []}
            perf[ch_id]["totaal"] += 1
            status = best.get("status", "")
            if status == "Afgeleverd":
                perf[ch_id]["afgeleverd"] += 1
                # Bereken levertijd
                events = self._get_status_events_for_bestelling(best["id"])
                if len(events) >= 2:
                    # Tijd tussen eerste en laatste event
                    try:
                        first = events[-1]["timestamp"]
                        last = events[0]["timestamp"]
                        t1 = datetime.datetime.fromisoformat(first)
                        t2 = datetime.datetime.fromisoformat(last)
                        delta_min = (t2 - t1).total_seconds() / 60
                        if delta_min > 0:
                            perf[ch_id]["levertijden"].append(delta_min)
                    except (ValueError, TypeError):
                        pass
            elif status == "Onderweg":
                perf[ch_id]["onderweg"] += 1
            elif status == "Gepland":
                perf[ch_id]["gepland"] += 1

        # Resultaat
        result = []
        for ch_id, data in perf.items():
            naam = chauffeur_map.get(ch_id, "(Geen chauffeur)") if ch_id else "(Geen chauffeur)"
            gem_levertijd = "-"
            if data["levertijden"]:
                avg = sum(data["levertijden"]) / len(data["levertijden"])
                if avg < 60:
                    gem_levertijd = f"{int(avg)} min"
                else:
                    gem_levertijd = f"{avg / 60:.1f} uur"
            result.append({
                "chauffeur": naam,
                "totaal": data["totaal"],
                "afgeleverd": data["afgeleverd"],
                "onderweg": data["onderweg"],
                "gepland": data["gepland"],
                "gem_levertijd": gem_levertijd,
            })

        # Sorteer op totaal
        result.sort(key=lambda x: x["totaal"], reverse=True)
        return result

    def _refresh_manager_stats(self) -> None:
        if not hasattr(self, "manager_tree"):
            return

        for row in self.manager_tree.get_children():
            self.manager_tree.delete(row)

        perf = self._calculate_chauffeur_performance()
        for p in perf:
            self.manager_tree.insert(
                "",
                tk.END,
                values=(p["chauffeur"], p["totaal"], p["afgeleverd"], p["onderweg"], p["gepland"], p["gem_levertijd"]),
            )

    def _export_manager_csv(self) -> None:
        perf = self._calculate_chauffeur_performance()
        if not perf:
            messagebox.showinfo("Export", "Geen data om te exporteren.")
            return

        path = filedialog.asksaveasfilename(
            title="Exporteer prestaties naar CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Chauffeur", "Totaal", "Afgeleverd", "Onderweg", "Gepland", "Gem. levertijd"])
                for p in perf:
                    w.writerow([p["chauffeur"], p["totaal"], p["afgeleverd"], p["onderweg"], p["gepland"], p["gem_levertijd"]])
        except OSError:
            messagebox.showerror("Fout", "Kon het CSV bestand niet opslaan.")
            return

        messagebox.showinfo("Export", "CSV export is opgeslagen.")

    def _build_klant_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        title = ttk.Label(self.content, text="Klant Dashboard", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 12))

        # Main dashboard container
        main_frame = ttk.Frame(self.content)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # Dashboard summary
        self._load_data_from_database()
        all_orders = self.bestellingen_data
        active = [b for b in all_orders if b.get("status") in ("Gepland", "Onderweg")]
        delivered = [b for b in all_orders if b.get("status") == "Afgeleverd"]
        onderweg = [b for b in all_orders if b.get("status") == "Onderweg"]
        gepland = [b for b in all_orders if b.get("status") == "Gepland"]

        # LEFT PANEL - Stats & Info
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_panel.columnconfigure(0, weight=1)

        # Stats card
        stats_card = ttk.LabelFrame(left_panel, text="Overzicht")
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        stats_card.columnconfigure(1, weight=1)

        ttk.Label(stats_card, text="Totaal bestellingen:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        ttk.Label(stats_card, text=str(len(all_orders)), font=("Segoe UI", 12, "bold")).grid(row=0, column=1, sticky="e", padx=12, pady=(8, 2))

        ttk.Label(stats_card, text="Gepland:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=12, pady=2)
        ttk.Label(stats_card, text=str(len(gepland)), font=("Segoe UI", 12, "bold"), foreground="#666666").grid(row=1, column=1, sticky="e", padx=12, pady=2)

        ttk.Label(stats_card, text="Onderweg:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=12, pady=2)
        ttk.Label(stats_card, text=str(len(onderweg)), font=("Segoe UI", 12, "bold"), foreground="#E67E22").grid(row=2, column=1, sticky="e", padx=12, pady=2)

        ttk.Label(stats_card, text="Bezorgd:", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", padx=12, pady=(2, 8))
        ttk.Label(stats_card, text=str(len(delivered)), font=("Segoe UI", 12, "bold"), foreground="#27AE60").grid(row=3, column=1, sticky="e", padx=12, pady=(2, 8))

        # Current order highlight
        current_card = ttk.LabelFrame(left_panel, text="Huidige Status")
        current_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        current_card.columnconfigure(0, weight=1)

        if onderweg:
            latest = onderweg[0]
            ttk.Label(current_card, text="Nu onderweg!", font=("Segoe UI", 11, "bold"), foreground="#E67E22").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))
            ttk.Label(current_card, text=f"Bestelling #{latest['id']}", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=12, pady=2)
            ttk.Label(current_card, text=f"Naar: {latest.get('aflever', '')}", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=12, pady=(2, 8))
        elif gepland:
            latest = gepland[0]
            ttk.Label(current_card, text="Volgende bestelling", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))
            ttk.Label(current_card, text=f"Bestelling #{latest['id']}", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=12, pady=2)
            ttk.Label(current_card, text="Status: Gepland", font=("Segoe UI", 10), foreground="#666666").grid(row=2, column=0, sticky="w", padx=12, pady=(2, 8))
        else:
            ttk.Label(current_card, text="Geen actieve bestellingen", font=("Segoe UI", 11), foreground="#666666").grid(row=0, column=0, sticky="w", padx=12, pady=12)

        # Event log card
        eventlog_card = ttk.LabelFrame(left_panel, text="Status Updates")
        eventlog_card.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        eventlog_card.columnconfigure(0, weight=1)
        eventlog_card.rowconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)

        ev_columns = ("timestamp", "status", "opmerking")
        self.klant_eventlog_tree = ttk.Treeview(eventlog_card, columns=ev_columns, show="headings", height=6)
        self.klant_eventlog_tree.heading("timestamp", text="Tijd")
        self.klant_eventlog_tree.heading("status", text="Status")
        self.klant_eventlog_tree.heading("opmerking", text="Opmerking")
        self.klant_eventlog_tree.column("timestamp", width=100, anchor="w")
        self.klant_eventlog_tree.column("status", width=70, anchor="w")
        self.klant_eventlog_tree.column("opmerking", width=100, anchor="w")

        ev_scroll = ttk.Scrollbar(eventlog_card, orient="vertical", command=self.klant_eventlog_tree.yview)
        self.klant_eventlog_tree.configure(yscrollcommand=ev_scroll.set)
        self.klant_eventlog_tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        ev_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)

        # Actions card
        action_card = ttk.LabelFrame(left_panel, text="Acties")
        action_card.grid(row=3, column=0, sticky="ew")
        action_card.columnconfigure(0, weight=1)

        refresh_btn = ttk.Button(action_card, text="Ververs", command=self._refresh_klant_bestellingen)
        refresh_btn.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))

        self.var_klant_auto = tk.IntVar(value=0)
        chk_auto = ttk.Checkbutton(action_card, text="Auto-refresh (5 sec)", variable=self.var_klant_auto, command=self._toggle_klant_auto_refresh)
        chk_auto.grid(row=1, column=0, sticky="w", padx=12, pady=(4, 12))

        # RIGHT PANEL - Orders table
        right_panel = ttk.LabelFrame(main_frame, text="Mijn Bestellingen")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)

        # Search
        search_frame = ttk.Frame(right_panel)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 8))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Zoek:").grid(row=0, column=0, sticky="w")
        self.entry_klant_search = ttk.Entry(search_frame)
        self.entry_klant_search.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.entry_klant_search.bind("<KeyRelease>", lambda _e: self._refresh_klant_bestellingen())

        columns = ("id", "klant", "aflever", "status", "eta")
        self.klant_tree = ttk.Treeview(right_panel, columns=columns, show="headings", height=14)
        self.klant_tree.heading("id", text="#")
        self.klant_tree.heading("klant", text="Klant")
        self.klant_tree.heading("aflever", text="Afleveradres")
        self.klant_tree.heading("status", text="Status")
        self.klant_tree.heading("eta", text="ETA")

        self.klant_tree.column("id", width=50, anchor="w")
        self.klant_tree.column("klant", width=100, anchor="w")
        self.klant_tree.column("aflever", width=180, anchor="w")
        self.klant_tree.column("status", width=80, anchor="w")
        self.klant_tree.column("eta", width=80, anchor="w")

        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.klant_tree.yview)
        self.klant_tree.configure(yscrollcommand=scrollbar.set)
        self.klant_tree.grid(row=1, column=0, sticky="nsew", padx=(12, 0), pady=(0, 12))
        scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 12), pady=(0, 12))

        # Status colors
        self.klant_tree.tag_configure("gepland", foreground="#666666")
        self.klant_tree.tag_configure("onderweg", foreground="#E67E22")
        self.klant_tree.tag_configure("afgeleverd", foreground="#27AE60")
        self.klant_tree.tag_configure("geannuleerd", foreground="#C0392B")

        # Event log for selected order
        self.klant_tree.bind("<<TreeviewSelect>>", lambda _e: self._refresh_klant_eventlog())

        self._klant_auto_refresh_enabled = False
        self._refresh_klant_bestellingen()

    def _refresh_klant_bestellingen(self) -> None:
        if not hasattr(self, "klant_tree"):
            return

        for row in self.klant_tree.get_children():
            self.klant_tree.delete(row)

        self._load_data_from_database()

        term = ""
        if hasattr(self, "entry_klant_search"):
            term = (self.entry_klant_search.get() or "").strip().lower()

        for best in self.bestellingen_data:
            # Filter op zoekterm
            if term:
                hay = f"{best.get('id', '')} {best.get('klant', '')}".lower()
                if term not in hay:
                    continue

            # Bereken ETA
            status = best.get("status", "")
            if status == "Afgeleverd":
                eta = "Bezorgd"
            elif status == "Geannuleerd":
                eta = "-"
            elif status == "Onderweg":
                eta = "Binnenkort"
            else:
                eta = "Wordt gepland"

            # Tag voor kleuren
            tag = status.lower() if status else "gepland"

            self.klant_tree.insert(
                "",
                tk.END,
                values=(best["id"], best.get("klant", ""), best.get("aflever", ""), status, eta),
                tags=(tag,),
            )

    def _refresh_klant_eventlog(self) -> None:
        if not hasattr(self, "klant_eventlog_tree"):
            return

        for row in self.klant_eventlog_tree.get_children():
            self.klant_eventlog_tree.delete(row)

        if not hasattr(self, "klant_tree"):
            return

        selected = self.klant_tree.selection()
        if not selected:
            return

        values = self.klant_tree.item(selected[0], "values")
        best_id = int(values[0]) if values else None
        if not best_id:
            return

        events = self._get_status_events_for_bestelling(best_id)
        for ev in events:
            self.klant_eventlog_tree.insert("", tk.END, values=(ev["timestamp"], ev["status"], ev["opmerking"] or ""))

    def _toggle_klant_auto_refresh(self) -> None:
        self._klant_auto_refresh_enabled = bool(self.var_klant_auto.get()) if hasattr(self, "var_klant_auto") else False
        if self._klant_auto_refresh_enabled:
            self._schedule_klant_refresh()

    def _schedule_klant_refresh(self) -> None:
        if not self._klant_auto_refresh_enabled:
            return
        self.after(5000, self._klant_refresh_tick)

    def _klant_refresh_tick(self) -> None:
        if self._klant_auto_refresh_enabled:
            self._refresh_klant_bestellingen()
            self._refresh_klant_eventlog()
            self._schedule_klant_refresh()

    def _build_chauffeurs_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(2, weight=1)

        title = ttk.Label(self.content, text="Chauffeurs", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w")

        form_frame = ttk.Frame(self.content)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Naam *").grid(row=0, column=0, sticky="w")
        self.entry_chauffeur_naam = ttk.Entry(form_frame)
        self.entry_chauffeur_naam.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(form_frame, text="Voertuig").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.entry_chauffeur_voertuig = ttk.Entry(form_frame)
        self.entry_chauffeur_voertuig.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        self.var_chauffeur_beschikbaar = tk.IntVar(value=1)
        chk = ttk.Checkbutton(form_frame, text="Beschikbaar", variable=self.var_chauffeur_beschikbaar)
        chk.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(4, 0))

        button_row = ttk.Frame(form_frame)
        button_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        button_row.columnconfigure(0, weight=1)

        delete_button = ttk.Button(
            button_row,
            text="Geselecteerde chauffeur verwijderen",
            command=self._delete_selected_chauffeur,
        )
        delete_button.grid(row=0, column=0, sticky="w")

        add_button = ttk.Button(button_row, text="Toevoegen", command=self._add_chauffeur)
        add_button.grid(row=0, column=1, sticky="e")

        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=2, column=0, sticky="nsew")

        columns = ("id", "naam", "voertuig", "beschikbaar")
        self.chauffeurs_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.chauffeurs_tree.heading("id", text="ID")
        self.chauffeurs_tree.heading("naam", text="Naam")
        self.chauffeurs_tree.heading("voertuig", text="Voertuig")
        self.chauffeurs_tree.heading("beschikbaar", text="Beschikbaar")

        self.chauffeurs_tree.column("id", width=40, anchor="w")
        self.chauffeurs_tree.column("naam", width=160, anchor="w")
        self.chauffeurs_tree.column("voertuig", width=160, anchor="w")
        self.chauffeurs_tree.column("beschikbaar", width=110, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.chauffeurs_tree.yview)
        self.chauffeurs_tree.configure(yscrollcommand=scrollbar.set)

        self.chauffeurs_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self._refresh_chauffeurs_table()

    def _add_chauffeur(self) -> None:
        naam = self.entry_chauffeur_naam.get().strip()
        voertuig = self.entry_chauffeur_voertuig.get().strip()
        beschikbaar = 1 if self.var_chauffeur_beschikbaar.get() else 0

        if not naam:
            messagebox.showwarning("Validatie", "Naam is verplicht voor een chauffeur.")
            return

        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT INTO chauffeurs (naam, voertuig, beschikbaar) VALUES (?, ?, ?)",
            (naam, voertuig, beschikbaar),
        )
        self.db_conn.commit()

        self._load_data_from_database()
        self.entry_chauffeur_naam.delete(0, tk.END)
        self.entry_chauffeur_voertuig.delete(0, tk.END)
        self.var_chauffeur_beschikbaar.set(1)
        self._refresh_chauffeurs_table()

    def _delete_selected_chauffeur(self) -> None:
        if not hasattr(self, "chauffeurs_tree"):
            return

        selected = self.chauffeurs_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een chauffeur in de tabel.")
            return

        item_id = selected[0]
        values = self.chauffeurs_tree.item(item_id, "values")
        chauffeur_id = values[0] if values else None

        if not chauffeur_id:
            return

        if not messagebox.askyesno("Bevestigen", "Weet je zeker dat je deze chauffeur wilt verwijderen?"):
            return

        cur = self.db_conn.cursor()
        cur.execute("DELETE FROM chauffeurs WHERE id = ?", (chauffeur_id,))
        self.db_conn.commit()

        self._load_data_from_database()
        self._refresh_chauffeurs_table()

    def _refresh_chauffeurs_table(self) -> None:
        if not hasattr(self, "chauffeurs_tree"):
            return

        for row in self.chauffeurs_tree.get_children():
            self.chauffeurs_tree.delete(row)

        for ch in getattr(self, "chauffeurs_data", []):
            self.chauffeurs_tree.insert(
                "",
                tk.END,
                values=(ch["id"], ch["naam"], ch["voertuig"] or "", "Ja" if ch["beschikbaar"] else "Nee"),
            )

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
        self.content.rowconfigure(0, weight=0)
        self.content.rowconfigure(1, weight=0)
        self.content.rowconfigure(2, weight=1)

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

        delete_button = ttk.Button(button_row, text="Verwijderen", command=self._delete_selected_klant)
        delete_button.grid(row=0, column=0, sticky="w")

        edit_button = ttk.Button(button_row, text="Wijzigen", command=self._edit_selected_klant)
        edit_button.grid(row=0, column=1, sticky="w", padx=(8, 0))

        add_button = ttk.Button(button_row, text="Toevoegen", command=self._add_klant)
        add_button.grid(row=0, column=2, sticky="e")

        # Tabel
        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=2, column=0, sticky="nsew", pady=(6, 0))

        search_row = ttk.Frame(table_frame)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        search_row.columnconfigure(1, weight=1)
        ttk.Label(search_row, text="Zoek:").grid(row=0, column=0, sticky="w")
        self.entry_klant_search = ttk.Entry(search_row)
        self.entry_klant_search.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.entry_klant_search.bind("<KeyRelease>", lambda _event: self._refresh_klanten_table())

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

        self.klanten_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)

        self._editing_klant_id: int | None = None
        self._refresh_klanten_table()

    def _edit_selected_klant(self) -> None:
        """Load selected klant into form for editing."""
        if not hasattr(self, "klanten_tree"):
            return

        selected = self.klanten_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een klant in de tabel.")
            return

        values = self.klanten_tree.item(selected[0], "values")
        klant_id = int(values[0]) if values else None
        if not klant_id:
            return

        klant = next((k for k in self.klanten_data if k.get("id") == klant_id), None)
        if not klant:
            return

        # Fill form with klant data
        self.entry_klant_naam.delete(0, tk.END)
        self.entry_klant_naam.insert(0, klant.get("naam", ""))
        self.entry_klant_adres.delete(0, tk.END)
        self.entry_klant_adres.insert(0, klant.get("adres", ""))
        self.entry_klant_contact.delete(0, tk.END)
        self.entry_klant_contact.insert(0, klant.get("contact", "") or "")

        self._editing_klant_id = klant_id
        messagebox.showinfo("Wijzigen", f"Klant {klant_id} geladen. Pas de gegevens aan en klik op 'Toevoegen' om op te slaan.")

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

        # Check if we are editing an existing klant
        editing_id = getattr(self, "_editing_klant_id", None)
        if editing_id:
            cur.execute(
                "UPDATE klanten SET naam = ?, adres = ?, contact = ? WHERE id = ?",
                (naam, adres, contact, editing_id),
            )
            self._editing_klant_id = None
        else:
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

        term = ""
        if hasattr(self, "entry_klant_search"):
            term = (self.entry_klant_search.get() or "").strip().lower()

        for klant in self.klanten_data:
            if term:
                hay = f"{klant.get('naam','')} {klant.get('adres','')} {klant.get('contact','')}".lower()
                if term not in hay:
                    continue
            self.klanten_tree.insert("", tk.END, values=(klant["id"], klant["naam"], klant["adres"], klant["contact"]))

    def _build_bestellingen_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=0)
        self.content.rowconfigure(1, weight=0)
        self.content.rowconfigure(2, weight=1)

        header_row = ttk.Frame(self.content)
        header_row.grid(row=0, column=0, sticky="ew")
        header_row.columnconfigure(0, weight=1)

        title = ttk.Label(header_row, text="Bestellingen", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w")

        form_frame = ttk.Frame(self.content)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Klantnaam *").grid(row=0, column=0, sticky="w")
        self.combo_best_klant = ttk.Combobox(form_frame, state="readonly")
        self.combo_best_klant.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.combo_best_klant.bind("<<ComboboxSelected>>", self._on_klant_selected)

        ttk.Label(form_frame, text="Ophaaladres *").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.entry_best_ophaal = ttk.Entry(form_frame)
        self.entry_best_ophaal.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        ttk.Label(form_frame, text="Afleveradres *").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.entry_best_aflever = ttk.Entry(form_frame)
        self.entry_best_aflever.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        ttk.Label(form_frame, text="Datum (DD-MM-JJJJ)").grid(row=3, column=0, sticky="w", pady=(4, 0))
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

        ttk.Label(form_frame, text="Chauffeur").grid(row=5, column=0, sticky="w", pady=(4, 0))
        self.combo_best_chauffeur = ttk.Combobox(form_frame, state="readonly")
        self.combo_best_chauffeur.grid(row=5, column=1, sticky="ew", padx=(8, 0), pady=(4, 0))

        button_row = ttk.Frame(form_frame)
        button_row.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        button_row.columnconfigure(0, weight=1)

        delete_button = ttk.Button(
            button_row,
            text="Geselecteerde bestelling verwijderen",
            command=self._delete_selected_bestelling,
        )
        delete_button.grid(row=0, column=0, sticky="w")

        add_button = ttk.Button(button_row, text="Bestelling toevoegen", command=self._add_bestelling)
        add_button.grid(row=0, column=1, sticky="e")

        table_wrapper = ttk.Frame(self.content)
        table_wrapper.grid(row=2, column=0, sticky="nsew")
        table_wrapper.columnconfigure(0, weight=1)
        table_wrapper.rowconfigure(1, weight=1)

        filter_row = ttk.Frame(table_wrapper)
        filter_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        filter_row.columnconfigure(7, weight=1)

        ttk.Label(filter_row, text="Status:").grid(row=0, column=0, sticky="w")
        self.combo_best_filter_status = ttk.Combobox(
            filter_row,
            state="readonly",
            values=["Alle", "Gepland", "Onderweg", "Afgeleverd", "Geannuleerd"],
            width=14,
        )
        self.combo_best_filter_status.set("Alle")
        self.combo_best_filter_status.grid(row=0, column=1, sticky="w", padx=(8, 12))
        self.combo_best_filter_status.bind("<<ComboboxSelected>>", lambda _event: self._refresh_bestellingen_table())

        ttk.Label(filter_row, text="Chauffeur:").grid(row=0, column=2, sticky="w")
        chauffeur_filter_values = ["Alle", "(Geen)"] + [f"{c['id']}: {c['naam']}" for c in getattr(self, "chauffeurs_data", [])]
        self.combo_best_filter_chauffeur = ttk.Combobox(filter_row, state="readonly", values=chauffeur_filter_values, width=16)
        self.combo_best_filter_chauffeur.set("Alle")
        self.combo_best_filter_chauffeur.grid(row=0, column=3, sticky="w", padx=(8, 12))
        self.combo_best_filter_chauffeur.bind("<<ComboboxSelected>>", lambda _event: self._refresh_bestellingen_table())

        ttk.Label(filter_row, text="Datum:").grid(row=0, column=4, sticky="w")
        self.entry_best_filter_date = ttk.Entry(filter_row, width=12)
        self.entry_best_filter_date.grid(row=0, column=5, sticky="w", padx=(8, 12))
        self.entry_best_filter_date.bind("<KeyRelease>", lambda _event: self._refresh_bestellingen_table())

        ttk.Label(filter_row, text="Zoek:").grid(row=0, column=6, sticky="w")
        self.entry_best_search = ttk.Entry(filter_row)
        self.entry_best_search.grid(row=0, column=7, sticky="ew", padx=(8, 12))
        self.entry_best_search.bind("<KeyRelease>", lambda _event: self._refresh_bestellingen_table())

        export_btn = ttk.Button(filter_row, text="Export CSV", command=self._export_bestellingen_csv)
        export_btn.grid(row=0, column=8, sticky="e")

        main_frame = ttk.Frame(table_wrapper)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        columns = ("id", "klant", "ophaal", "aflever", "datum", "status", "chauffeur")
        self.bestellingen_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.bestellingen_tree.heading("id", text="ID")
        self.bestellingen_tree.heading("klant", text="Klant")
        self.bestellingen_tree.heading("ophaal", text="Ophaaladres")
        self.bestellingen_tree.heading("aflever", text="Afleveradres")
        self.bestellingen_tree.heading("datum", text="Datum")
        self.bestellingen_tree.heading("status", text="Status")
        self.bestellingen_tree.heading("chauffeur", text="Chauffeur")

        self.bestellingen_tree.column("id", width=40, anchor="w")
        self.bestellingen_tree.column("klant", width=120, anchor="w")
        self.bestellingen_tree.column("ophaal", width=180, anchor="w")
        self.bestellingen_tree.column("aflever", width=180, anchor="w")
        self.bestellingen_tree.column("datum", width=110, anchor="w")
        self.bestellingen_tree.column("status", width=100, anchor="w")
        self.bestellingen_tree.column("chauffeur", width=140, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.bestellingen_tree.yview)
        self.bestellingen_tree.configure(yscrollcommand=scrollbar.set)

        self.bestellingen_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        detail_frame = ttk.Frame(main_frame)
        detail_frame.grid(row=0, column=1, sticky="nsew")
        detail_frame.columnconfigure(1, weight=1)

        ttk.Label(detail_frame, text="Details", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(detail_frame, text="ID:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.lbl_best_detail_id = ttk.Label(detail_frame, text="-")
        self.lbl_best_detail_id.grid(row=1, column=1, sticky="w", pady=(6, 0))

        ttk.Label(detail_frame, text="Klant:").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.lbl_best_detail_klant = ttk.Label(detail_frame, text="-")
        self.lbl_best_detail_klant.grid(row=2, column=1, sticky="w", pady=(4, 0))

        ttk.Label(detail_frame, text="Ophaal:").grid(row=3, column=0, sticky="w", pady=(4, 0))
        self.lbl_best_detail_ophaal = ttk.Label(detail_frame, text="-")
        self.lbl_best_detail_ophaal.grid(row=3, column=1, sticky="w", pady=(4, 0))

        ttk.Label(detail_frame, text="Aflever:").grid(row=4, column=0, sticky="w", pady=(4, 0))
        self.lbl_best_detail_aflever = ttk.Label(detail_frame, text="-")
        self.lbl_best_detail_aflever.grid(row=4, column=1, sticky="w", pady=(4, 0))

        ttk.Label(detail_frame, text="Datum:").grid(row=5, column=0, sticky="w", pady=(6, 0))
        self.entry_best_detail_datum = ttk.Entry(detail_frame)
        self.entry_best_detail_datum.grid(row=5, column=1, sticky="ew", pady=(6, 0))

        ttk.Label(detail_frame, text="Status:").grid(row=6, column=0, sticky="w", pady=(6, 0))
        self.combo_best_detail_status = ttk.Combobox(
            detail_frame,
            state="readonly",
            values=["Gepland", "Onderweg", "Afgeleverd", "Geannuleerd"],
            width=14,
        )
        self.combo_best_detail_status.grid(row=6, column=1, sticky="w", pady=(6, 0))

        ttk.Label(detail_frame, text="Chauffeur:").grid(row=7, column=0, sticky="w", pady=(6, 0))
        chauffeur_values_detail = ["(Geen)"] + [f"{c['id']}: {c['naam']}" for c in getattr(self, "chauffeurs_data", [])]
        self.combo_best_detail_chauffeur = ttk.Combobox(detail_frame, state="readonly", values=chauffeur_values_detail, width=16)
        self.combo_best_detail_chauffeur.set("(Geen)")
        self.combo_best_detail_chauffeur.grid(row=7, column=1, sticky="w", pady=(6, 0))

        ttk.Label(detail_frame, text="Opmerking:").grid(row=8, column=0, sticky="w", pady=(6, 0))
        self.entry_best_detail_note = ttk.Entry(detail_frame)
        self.entry_best_detail_note.grid(row=8, column=1, sticky="ew", pady=(6, 0))

        self.btn_best_detail_apply = ttk.Button(
            detail_frame,
            text="Wijzigingen toepassen",
            command=self._update_selected_bestelling_from_details,
        )
        self.btn_best_detail_apply.grid(row=9, column=0, columnspan=2, sticky="e", pady=(10, 0))

        self.bestellingen_tree.bind("<<TreeviewSelect>>", lambda _event: self._on_bestelling_selected_in_table())

        self._load_klanten_in_combobox()
        self._load_chauffeurs_in_combobox()
        self._refresh_bestellingen_table()

    def _load_klanten_in_combobox(self) -> None:
        """Load klanten from database into the combobox."""
        if not hasattr(self, "combo_best_klant"):
            return
        
        self._load_data_from_database()
        klanten_names = [k.get("naam", "") for k in self.klanten_data]
        self.combo_best_klant.configure(values=klanten_names)

    def _load_chauffeurs_in_combobox(self) -> None:
        """Load chauffeurs from database into the combobox."""
        if not hasattr(self, "combo_best_chauffeur"):
            return
        
        self._load_data_from_database()
        chauffeur_options = ["(Geen)"] + [f"{c.get('id')}: {c.get('naam', '')}" for c in self.chauffeurs_data]
        self.combo_best_chauffeur.configure(values=chauffeur_options)
        self.combo_best_chauffeur.set("(Geen)")

    def _on_klant_selected(self, event=None) -> None:
        """Auto-fill afleveradres when klant is selected."""
        if not hasattr(self, "combo_best_klant") or not hasattr(self, "entry_best_aflever"):
            return
        
        selected_name = self.combo_best_klant.get()
        if not selected_name:
            return
        
        # Find klant in database
        for klant in self.klanten_data:
            if klant.get("naam") == selected_name:
                # Auto-fill afleveradres with klant's adres
                self.entry_best_aflever.delete(0, tk.END)
                self.entry_best_aflever.insert(0, klant.get("adres", ""))
                break

    def _open_chauffeur_picker(self) -> None:
        """Open a popup dialog to select a chauffeur."""
        picker = tk.Toplevel(self)
        picker.title("Kies chauffeur")
        picker.geometry("400x300")
        picker.transient(self)
        picker.grab_set()

        ttk.Label(picker, text="Selecteer een chauffeur:", font=("Segoe UI", 11, "bold")).pack(pady=(12, 8), padx=12, anchor="w")

        # Listbox with chauffeurs
        frame = ttk.Frame(picker)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        listbox = tk.Listbox(frame, font=("Segoe UI", 10), selectmode="single")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add "(Geen)" option
        listbox.insert(tk.END, "(Geen)")
        chauffeur_ids = [None]

        for ch in getattr(self, "chauffeurs_data", []):
            naam = ch.get("naam", "")
            beschikbaar = ch.get("beschikbaar", True)
            ch_id = ch.get("id")

            if beschikbaar:
                listbox.insert(tk.END, f"{ch_id}: {naam}")
                chauffeur_ids.append(ch_id)
            else:
                listbox.insert(tk.END, f"{ch_id}: {naam} (niet beschikbaar)")
                chauffeur_ids.append(None)  # Mark as not selectable
                # Grey out this item
                idx = listbox.size() - 1
                listbox.itemconfig(idx, fg="#999999")

        def on_select():
            sel = listbox.curselection()
            if not sel:
                picker.destroy()
                return
            idx = sel[0]
            if idx == 0:  # (Geen)
                self._selected_chauffeur_id = None
                self.lbl_selected_chauffeur.config(text="(Geen)")
            else:
                ch_id = chauffeur_ids[idx]
                if ch_id is None:  # Not available
                    messagebox.showwarning("Niet beschikbaar", "Deze chauffeur is niet beschikbaar.", parent=picker)
                    return
                ch = next((c for c in self.chauffeurs_data if c.get("id") == ch_id), None)
                if ch:
                    self._selected_chauffeur_id = ch_id
                    self.lbl_selected_chauffeur.config(text=f"{ch_id}: {ch.get('naam', '')}")
            picker.destroy()

        btn_frame = ttk.Frame(picker)
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Button(btn_frame, text="OK", command=on_select).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="Annuleren", command=picker.destroy).pack(side="right")

    def _add_bestelling(self) -> None:
        klant = (self.combo_best_klant.get() or "").strip()
        ophaal = (self.entry_best_ophaal.get() or "").strip()
        aflever = (self.entry_best_aflever.get() or "").strip()
        datum = (self.entry_best_datum.get() or "").strip()
        status = (self.combo_best_status.get() or "").strip()
        
        # Get chauffeur ID from combobox
        chauffeur_selection = (self.combo_best_chauffeur.get() or "").strip()
        chauffeur_id = None
        if chauffeur_selection and chauffeur_selection != "(Geen)":
            try:
                chauffeur_id = int(chauffeur_selection.split(":")[0])
            except (ValueError, IndexError):
                chauffeur_id = None

        if not klant or not ophaal or not aflever:
            messagebox.showwarning(
                "Validatie",
                "Klantnaam, ophaaladres en afleveradres zijn verplicht voor een bestelling.",
            )
            return

        if datum and not self._is_valid_iso_date(datum):
            messagebox.showwarning("Validatie", "Datum moet het formaat DD-MM-JJJJ hebben.")
            return

        # Convert Dutch date to database format
        db_datum = self._convert_date_to_db(datum) if datum else ""
        
        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT INTO bestellingen (klant, ophaal, aflever, datum, status, chauffeur_id) VALUES (?, ?, ?, ?, ?, ?)",
            (klant, ophaal, aflever, db_datum, status, chauffeur_id),
        )
        self.db_conn.commit()

        bestelling_id = cur.lastrowid
        if bestelling_id:
            self._log_status_event(int(bestelling_id), status, "Aangemaakt")

        self._load_data_from_database()

        self.combo_best_klant.set("")
        self.entry_best_ophaal.delete(0, tk.END)
        self.entry_best_aflever.delete(0, tk.END)
        self.entry_best_datum.delete(0, tk.END)
        self.combo_best_status.set("Gepland")
        self.combo_best_chauffeur.set("(Geen)")

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

        geselecteerde_status = "Alle"
        if hasattr(self, "combo_best_filter_status"):
            geselecteerde_status = self.combo_best_filter_status.get() or "Alle"

        chauffeur_filter = "Alle"
        if hasattr(self, "combo_best_filter_chauffeur"):
            chauffeur_filter = self.combo_best_filter_chauffeur.get() or "Alle"

        date_filter = ""
        if hasattr(self, "entry_best_filter_date"):
            date_filter = (self.entry_best_filter_date.get() or "").strip()

        term = ""
        if hasattr(self, "entry_best_search"):
            term = (self.entry_best_search.get() or "").strip().lower()

        chauffeur_map = {c["id"]: c["naam"] for c in getattr(self, "chauffeurs_data", [])}

        for best in self.bestellingen_data:
            if geselecteerde_status != "Alle" and best.get("status") != geselecteerde_status:
                continue

            if date_filter and (best.get("datum") or "") != date_filter:
                continue

            best_chauffeur_id = best.get("chauffeur_id")
            chauffeur_name = chauffeur_map.get(best_chauffeur_id, "") if best_chauffeur_id else ""

            if chauffeur_filter != "Alle":
                if chauffeur_filter == "(Geen)" and best_chauffeur_id:
                    continue
                if chauffeur_filter != "(Geen)":
                    try:
                        wanted_id = int(chauffeur_filter.split(":", 1)[0])
                    except ValueError:
                        wanted_id = None
                    if wanted_id and best_chauffeur_id != wanted_id:
                        continue

            if term:
                hay = f"{best.get('klant','')} {best.get('ophaal','')} {best.get('aflever','')} {best.get('datum','')} {best.get('status','')} {chauffeur_name}".lower()
                if term not in hay:
                    continue

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
                    chauffeur_name,
                ),
            )

        if hasattr(self, "lbl_best_detail_id"):
            self._on_bestelling_selected_in_table()

    def _get_bestellingen_filtered(self) -> list[dict]:
        geselecteerde_status = "Alle"
        if hasattr(self, "combo_best_filter_status"):
            geselecteerde_status = self.combo_best_filter_status.get() or "Alle"

        chauffeur_filter = "Alle"
        if hasattr(self, "combo_best_filter_chauffeur"):
            chauffeur_filter = self.combo_best_filter_chauffeur.get() or "Alle"

        date_filter = ""
        if hasattr(self, "entry_best_filter_date"):
            date_filter = (self.entry_best_filter_date.get() or "").strip()

        term = ""
        if hasattr(self, "entry_best_search"):
            term = (self.entry_best_search.get() or "").strip().lower()

        chauffeur_map = {c["id"]: c["naam"] for c in getattr(self, "chauffeurs_data", [])}

        out: list[dict] = []
        for best in self.bestellingen_data:
            if geselecteerde_status != "Alle" and best.get("status") != geselecteerde_status:
                continue
            if date_filter and (best.get("datum") or "") != date_filter:
                continue

            best_chauffeur_id = best.get("chauffeur_id")
            chauffeur_name = chauffeur_map.get(best_chauffeur_id, "") if best_chauffeur_id else ""

            if chauffeur_filter != "Alle":
                if chauffeur_filter == "(Geen)" and best_chauffeur_id:
                    continue
                if chauffeur_filter != "(Geen)":
                    try:
                        wanted_id = int(chauffeur_filter.split(":", 1)[0])
                    except ValueError:
                        wanted_id = None
                    if wanted_id and best_chauffeur_id != wanted_id:
                        continue

            if term:
                hay = f"{best.get('klant','')} {best.get('ophaal','')} {best.get('aflever','')} {best.get('datum','')} {best.get('status','')} {chauffeur_name}".lower()
                if term not in hay:
                    continue

            item = dict(best)
            item["chauffeur_naam"] = chauffeur_name
            out.append(item)
        return out

    def _export_bestellingen_csv(self) -> None:
        rows = self._get_bestellingen_filtered()
        if not rows:
            messagebox.showinfo("Export", "Geen bestellingen om te exporteren (op basis van je filters/zoekterm).")
            return

        path = filedialog.asksaveasfilename(
            title="Exporteer bestellingen naar CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id", "klant", "ophaal", "aflever", "datum", "status", "chauffeur"])
                for b in rows:
                    w.writerow(
                        [
                            b.get("id", ""),
                            b.get("klant", ""),
                            b.get("ophaal", ""),
                            b.get("aflever", ""),
                            b.get("datum", ""),
                            b.get("status", ""),
                            b.get("chauffeur_naam", ""),
                        ]
                    )
        except OSError:
            messagebox.showerror("Fout", "Kon het CSV bestand niet opslaan.")
            return

        messagebox.showinfo("Export", "CSV export is opgeslagen.")

    def _on_bestelling_selected_in_table(self) -> None:
        if not hasattr(self, "bestellingen_tree"):
            return

        selected = self.bestellingen_tree.selection()
        if not selected:
            if hasattr(self, "lbl_best_detail_id"):
                self.lbl_best_detail_id.config(text="-")
            if hasattr(self, "lbl_best_detail_klant"):
                self.lbl_best_detail_klant.config(text="-")
            if hasattr(self, "lbl_best_detail_ophaal"):
                self.lbl_best_detail_ophaal.config(text="-")
            if hasattr(self, "lbl_best_detail_aflever"):
                self.lbl_best_detail_aflever.config(text="-")
            if hasattr(self, "entry_best_detail_datum"):
                self.entry_best_detail_datum.delete(0, tk.END)
            if hasattr(self, "combo_best_detail_status"):
                self.combo_best_detail_status.set("")
            if hasattr(self, "combo_best_detail_chauffeur"):
                self.combo_best_detail_chauffeur.set("(Geen)")
            if hasattr(self, "entry_best_detail_note"):
                self.entry_best_detail_note.delete(0, tk.END)
            return

        values = self.bestellingen_tree.item(selected[0], "values")
        best_id = int(values[0]) if values else None
        if not best_id:
            return

        best = next((b for b in self.bestellingen_data if int(b.get("id")) == best_id), None)
        if not best:
            return

        if hasattr(self, "lbl_best_detail_id"):
            self.lbl_best_detail_id.config(text=str(best.get("id", "")))
        if hasattr(self, "lbl_best_detail_klant"):
            self.lbl_best_detail_klant.config(text=str(best.get("klant", "")))
        if hasattr(self, "lbl_best_detail_ophaal"):
            self.lbl_best_detail_ophaal.config(text=str(best.get("ophaal", "")))
        if hasattr(self, "lbl_best_detail_aflever"):
            self.lbl_best_detail_aflever.config(text=str(best.get("aflever", "")))

        if hasattr(self, "entry_best_detail_datum"):
            self.entry_best_detail_datum.delete(0, tk.END)
            db_datum = str(best.get("datum", "") or "")
            # Convert database date to Dutch format for display
            dutch_datum = self._convert_date_from_db(db_datum) if db_datum else ""
            self.entry_best_detail_datum.insert(0, dutch_datum)

        if hasattr(self, "combo_best_detail_status"):
            self.combo_best_detail_status.set(str(best.get("status", "") or ""))

        if hasattr(self, "combo_best_detail_chauffeur"):
            chauffeur_id = best.get("chauffeur_id")
            if chauffeur_id:
                name = next((c.get("naam", "") for c in getattr(self, "chauffeurs_data", []) if c.get("id") == chauffeur_id), "")
                self.combo_best_detail_chauffeur.set(f"{chauffeur_id}: {name}" if name else "(Geen)")
            else:
                self.combo_best_detail_chauffeur.set("(Geen)")

        if hasattr(self, "entry_best_detail_note"):
            self.entry_best_detail_note.delete(0, tk.END)

    def _update_selected_bestelling_from_details(self) -> None:
        if not hasattr(self, "bestellingen_tree"):
            return

        selected = self.bestellingen_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een bestelling in de tabel.")
            return

        values = self.bestellingen_tree.item(selected[0], "values")
        best_id = int(values[0]) if values else None
        if not best_id:
            return

        best = next((b for b in self.bestellingen_data if int(b.get("id")) == best_id), None)
        if not best:
            return

        new_status = (self.combo_best_detail_status.get() or "").strip() if hasattr(self, "combo_best_detail_status") else ""
        if not new_status:
            messagebox.showwarning("Validatie", "Kies een status.")
            return


        self._load_data_from_database()
        self._refresh_bestellingen_table()
        self._refresh_tracking_table()
        self._refresh_eventlog_table()

        if hasattr(self, "entry_best_detail_note"):
            self.entry_best_detail_note.delete(0, tk.END)

    def _build_planning_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(3, weight=1)

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

        filter_frame = ttk.Frame(self.content)
        filter_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        filter_frame.columnconfigure(3, weight=1)

        ttk.Label(filter_frame, text="Bestellingen status:").grid(row=0, column=0, sticky="w")
        self.combo_plan_status = ttk.Combobox(
            filter_frame,
            state="readonly",
            values=["Alle", "Gepland", "Onderweg", "Afgeleverd", "Geannuleerd"],
            width=14,
        )
        self.combo_plan_status.set("Alle")
        self.combo_plan_status.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.combo_plan_status.bind("<<ComboboxSelected>>", lambda _event: self._refresh_planning_table())

        # Tabel met beschikbare stops (bestellingen)
        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=3, column=0, sticky="nsew")

        columns = ("id", "klant", "adres")
        self.planning_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        self.planning_tree.heading("id", text="ID")
        self.planning_tree.heading("klant", text="Klant")
        self.planning_tree.heading("adres", text="Adres")

        self.planning_tree.column("id", width=40, anchor="w")
        self.planning_tree.column("klant", width=120, anchor="w")
        self.planning_tree.column("adres", width=420, anchor="w")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.planning_tree.yview)
        self.planning_tree.configure(yscrollcommand=scroll.set)

        self.planning_tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Knop om een eenvoudige "route" te berekenen
        button_frame = ttk.Frame(self.content)
        button_frame.grid(row=4, column=0, sticky="ew", pady=(8, 0))

        calc_button = ttk.Button(button_frame, text="Bereken route (optimaliseer)", command=self._calculate_simple_route)
        calc_button.grid(row=0, column=0, sticky="w")

        self.route_result_label = ttk.Label(button_frame, text="")
        self.route_result_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self._refresh_planning_table()

    def _refresh_planning_table(self) -> None:
        if not hasattr(self, "planning_tree"):
            return

        for row in self.planning_tree.get_children():
            self.planning_tree.delete(row)

        stops = self._get_planning_stops_from_bestellingen()
        if not stops:
            # fallback: laat dummy data zien als er nog geen bestellingen zijn
            for order in self.dummy_orders:
                self.planning_tree.insert("", tk.END, values=(order["id"], order["klant"], order["adres"]))
            return

        for s in stops:
            self.planning_tree.insert("", tk.END, values=(s["id"], s["klant"], s["adres"]))

    def _calculate_simple_route(self) -> None:
        stops = self._get_planning_stops_from_bestellingen()
        if not stops:
            sorted_orders = sorted(self.dummy_orders, key=lambda o: o["afstand"])
            volgorde_ids = [str(o["id"]) for o in sorted_orders]
            totale_afstand = sum(o["afstand"] for o in sorted_orders)
            tekst = f"Voorgestelde volgorde van stops (demo): {', '.join(volgorde_ids)}. "
            tekst += f"Totale geschatte afstand: {totale_afstand} km."
            self.route_result_label.config(text=tekst)
            return

        initial = self._nearest_neighbor_route(stops)
        improved = self._two_opt(initial)
        volgorde_ids = [str(o["id"]) for o in improved]
        totale_afstand = round(self._route_length(improved), 1)

        tekst = f"Voorgestelde volgorde van bestellingen (heuristisch): {', '.join(volgorde_ids)}. "
        tekst += f"Totale geschatte afstand: {totale_afstand} km."
        self.route_result_label.config(text=tekst)

    def _build_tracking_page(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(3, weight=1)

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

        control_frame = ttk.Frame(self.content)
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        control_frame.columnconfigure(13, weight=1)

        ttk.Label(control_frame, text="Filter op status:").grid(row=0, column=0, sticky="w")
        self.combo_track_status = ttk.Combobox(
            control_frame,
            state="readonly",
            values=["Alle", "Gepland", "Onderweg", "Afgeleverd", "Geannuleerd"],
        )
        self.combo_track_status.set("Alle")
        self.combo_track_status.grid(row=0, column=1, sticky="w", padx=(8, 12))
        self.combo_track_status.bind("<<ComboboxSelected>>", lambda _event: self._refresh_tracking_table())

        ttk.Label(control_frame, text="Chauffeur:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        chauffeur_values = ["Alle", "(Geen)"] + [f"{c['id']}: {c['naam']}" for c in getattr(self, "chauffeurs_data", [])]
        self.combo_track_chauffeur = ttk.Combobox(control_frame, state="readonly", values=chauffeur_values, width=16)
        self.combo_track_chauffeur.set("Alle")
        self.combo_track_chauffeur.grid(row=0, column=3, sticky="w", padx=(8, 12))
        self.combo_track_chauffeur.bind("<<ComboboxSelected>>", lambda _event: self._refresh_tracking_table())

        ttk.Label(control_frame, text="Zoek:").grid(row=0, column=4, sticky="w")
        self.entry_track_search = ttk.Entry(control_frame, width=20)
        self.entry_track_search.grid(row=0, column=5, sticky="w", padx=(8, 12))
        self.entry_track_search.bind("<KeyRelease>", lambda _event: self._refresh_tracking_table())

        ttk.Label(control_frame, text="Update status:").grid(row=0, column=6, sticky="w")
        self.combo_track_update = ttk.Combobox(
            control_frame,
            state="readonly",
            values=["Gepland", "Onderweg", "Afgeleverd", "Geannuleerd"],
            width=14,
        )
        self.combo_track_update.set("Onderweg")
        self.combo_track_update.grid(row=0, column=7, sticky="w", padx=(8, 0))

        ttk.Label(control_frame, text="Opmerking:").grid(row=0, column=8, sticky="w", padx=(12, 0))
        self.entry_track_note = ttk.Entry(control_frame, width=24)
        self.entry_track_note.grid(row=0, column=9, sticky="w", padx=(8, 0))

        update_btn = ttk.Button(control_frame, text="Toepassen", command=self._update_selected_bestelling_status)
        update_btn.grid(row=0, column=10, sticky="w", padx=(12, 0))

        self.var_track_auto = tk.IntVar(value=0)
        chk_auto = ttk.Checkbutton(control_frame, text="Auto-refresh", variable=self.var_track_auto, command=self._toggle_tracking_auto)
        chk_auto.grid(row=0, column=11, sticky="w", padx=(14, 0))

        self.var_track_sim = tk.IntVar(value=0)
        chk_sim = ttk.Checkbutton(control_frame, text="Simuleer live", variable=self.var_track_sim, command=self._toggle_tracking_sim)
        chk_sim.grid(row=0, column=12, sticky="w", padx=(10, 0))

        # Tabel met bestellingen
        table_frame = ttk.Frame(self.content)
        table_frame.grid(row=3, column=0, sticky="nsew")

        columns = ("id", "klant", "ophaal", "aflever", "datum", "status", "chauffeur")
        self.tracking_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        self.tracking_tree.heading("id", text="ID")
        self.tracking_tree.heading("klant", text="Klant")
        self.tracking_tree.heading("ophaal", text="Ophaaladres")
        self.tracking_tree.heading("aflever", text="Afleveradres")
        self.tracking_tree.heading("datum", text="Datum")
        self.tracking_tree.heading("status", text="Status")
        self.tracking_tree.heading("chauffeur", text="Chauffeur")

        self.tracking_tree.column("id", width=40, anchor="w")
        self.tracking_tree.column("klant", width=120, anchor="w")
        self.tracking_tree.column("ophaal", width=180, anchor="w")
        self.tracking_tree.column("aflever", width=180, anchor="w")
        self.tracking_tree.column("datum", width=110, anchor="w")
        self.tracking_tree.column("status", width=100, anchor="w")
        self.tracking_tree.column("chauffeur", width=140, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tracking_tree.yview)
        self.tracking_tree.configure(yscrollcommand=scrollbar.set)

        self.tracking_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tracking_tree.bind("<<TreeviewSelect>>", lambda _event: self._refresh_eventlog_table())

        eventlog_frame = ttk.Frame(self.content)
        eventlog_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        self.content.rowconfigure(4, weight=1)

        ttk.Label(eventlog_frame, text="Status events (historie)", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        ev_table = ttk.Frame(eventlog_frame)
        ev_table.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        eventlog_frame.columnconfigure(0, weight=1)
        eventlog_frame.rowconfigure(1, weight=1)

        ev_columns = ("timestamp", "status", "opmerking")
        self.eventlog_tree = ttk.Treeview(ev_table, columns=ev_columns, show="headings", height=6)
        self.eventlog_tree.heading("timestamp", text="Tijd")
        self.eventlog_tree.heading("status", text="Status")
        self.eventlog_tree.heading("opmerking", text="Opmerking")
        self.eventlog_tree.column("timestamp", width=160, anchor="w")
        self.eventlog_tree.column("status", width=120, anchor="w")
        self.eventlog_tree.column("opmerking", width=320, anchor="w")

        ev_scroll = ttk.Scrollbar(ev_table, orient="vertical", command=self.eventlog_tree.yview)
        self.eventlog_tree.configure(yscrollcommand=ev_scroll.set)
        self.eventlog_tree.grid(row=0, column=0, sticky="nsew")
        ev_scroll.grid(row=0, column=1, sticky="ns")
        ev_table.columnconfigure(0, weight=1)
        ev_table.rowconfigure(0, weight=1)

        self._refresh_tracking_table()

    def _update_selected_bestelling_status(self) -> None:
        if not hasattr(self, "tracking_tree"):
            return

        selected = self.tracking_tree.selection()
        if not selected:
            messagebox.showinfo("Geen selectie", "Selecteer eerst een bestelling in de tabel.")
            return

        values = self.tracking_tree.item(selected[0], "values")
        best_id = int(values[0]) if values else None
        if not best_id:
            return

        new_status = (self.combo_track_update.get() or "").strip() if hasattr(self, "combo_track_update") else ""
        if not new_status:
            messagebox.showwarning("Validatie", "Kies een nieuwe status.")
            return

        note = self.entry_track_note.get().strip() if hasattr(self, "entry_track_note") else ""

        cur = self.db_conn.cursor()
        cur.execute("UPDATE bestellingen SET status = ? WHERE id = ?", (new_status, best_id))
        self.db_conn.commit()

        self._log_status_event(best_id, new_status, note)
        self._load_data_from_database()
        self._refresh_tracking_table()
        self._refresh_bestellingen_table()
        self._refresh_eventlog_table()

        if hasattr(self, "entry_track_note"):
            self.entry_track_note.delete(0, tk.END)

    def _refresh_eventlog_table(self) -> None:
        if not hasattr(self, "eventlog_tree"):
            return

        for row in self.eventlog_tree.get_children():
            self.eventlog_tree.delete(row)

        if not hasattr(self, "tracking_tree"):
            return

        selected = self.tracking_tree.selection()
        if not selected:
            return

        values = self.tracking_tree.item(selected[0], "values")
        best_id = int(values[0]) if values else None
        if not best_id:
            return

        events = self._get_status_events_for_bestelling(best_id)
        for ev in events:
            self.eventlog_tree.insert("", tk.END, values=(ev["timestamp"], ev["status"], ev["opmerking"] or ""))

    def _refresh_tracking_table(self) -> None:
        if not hasattr(self, "tracking_tree"):
            return

        for row in self.tracking_tree.get_children():
            self.tracking_tree.delete(row)

        geselecteerde_status = "Alle"
        if hasattr(self, "combo_track_status"):
            geselecteerde_status = self.combo_track_status.get() or "Alle"

        chauffeur_filter = "Alle"
        if hasattr(self, "combo_track_chauffeur"):
            chauffeur_filter = self.combo_track_chauffeur.get() or "Alle"

        term = ""
        if hasattr(self, "entry_track_search"):
            term = (self.entry_track_search.get() or "").strip().lower()

        chauffeur_map = {c["id"]: c["naam"] for c in getattr(self, "chauffeurs_data", [])}

        for best in self.bestellingen_data:
            if geselecteerde_status != "Alle" and best.get("status") != geselecteerde_status:
                continue

            best_chauffeur_id = best.get("chauffeur_id")
            best_chauffeur_name = chauffeur_map.get(best_chauffeur_id, "") if best_chauffeur_id else ""
            if chauffeur_filter != "Alle":
                if chauffeur_filter == "(Geen)" and best_chauffeur_id:
                    continue
                if chauffeur_filter != "(Geen)":
                    try:
                        wanted_id = int(chauffeur_filter.split(":", 1)[0])
                    except ValueError:
                        wanted_id = None
                    if wanted_id and best_chauffeur_id != wanted_id:
                        continue

            if term:
                hay = f"{best.get('klant','')} {best.get('ophaal','')} {best.get('aflever','')} {best.get('datum','')} {best.get('status','')} {best_chauffeur_name}".lower()
                if term not in hay:
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
                    best_chauffeur_name,
                ),
            )

    def _toggle_tracking_auto(self) -> None:
        self._tracking_auto_refresh_enabled = bool(self.var_track_auto.get()) if hasattr(self, "var_track_auto") else False
        if self._tracking_auto_refresh_enabled:
            self._schedule_tracking_tick()

    def _toggle_tracking_sim(self) -> None:
        self._tracking_simulate_enabled = bool(self.var_track_sim.get()) if hasattr(self, "var_track_sim") else False
        if self._tracking_simulate_enabled:
            self._schedule_tracking_tick()

    def _schedule_tracking_tick(self) -> None:
        if not (self._tracking_auto_refresh_enabled or self._tracking_simulate_enabled):
            return
        self.after(self._tracking_auto_refresh_ms, self._tracking_tick)

    def _tracking_tick(self) -> None:
        if self._tracking_simulate_enabled:
            self._simulate_one_status_step_for_selected()

        if self._tracking_auto_refresh_enabled or self._tracking_simulate_enabled:
            self._load_data_from_database()
            self._refresh_tracking_table()
            self._refresh_bestellingen_table()
            self._refresh_eventlog_table()
            self._schedule_tracking_tick()

    def _simulate_one_status_step_for_selected(self) -> None:
        if not hasattr(self, "tracking_tree"):
            return
        selected = self.tracking_tree.selection()
        if not selected:
            return

        values = self.tracking_tree.item(selected[0], "values")
        best_id = int(values[0]) if values else None
        if not best_id:
            return

        # Determine next status
        cur = self.db_conn.cursor()
        row = cur.execute("SELECT status FROM bestellingen WHERE id = ?", (best_id,)).fetchone()
        current = row[0] if row else "Gepland"
        next_status = None
        if current == "Gepland":
            next_status = "Onderweg"
        elif current == "Onderweg":
            next_status = "Afgeleverd"

        if not next_status:
            return

        cur.execute("UPDATE bestellingen SET status = ? WHERE id = ?", (next_status, best_id))
        self.db_conn.commit()
        self._log_status_event(best_id, next_status, "Simulatie")


if __name__ == "__main__":
    app = QuickDeliveryApp()
    app.mainloop()
