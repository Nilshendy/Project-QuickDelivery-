# Dashboard Tabs Implementatie

## Overzicht
We hebben tabbed navigatie geïmplementeerd voor de **Chauffeur**, **Klant** en **Manager** dashboards, vergelijkbaar met het bestaande Planner dashboard.

---

## Wat is er veranderd?

### 1. Navigatie Structuur (`_pages_for_role`)
De functie die bepaalt welke tabs elke rol ziet is uitgebreid:

**Voorheen:** Elke rol had slechts 1 pagina  
**Nu:** Elke rol heeft meerdere tabs

---

## Nieuwe Tabs per Rol

### Chauffeur (3 tabs)
| Tab | Functie | Beschrijving |
|-----|---------|--------------|
| **Dashboard** | `_build_chauffeur_dashboard_page` | Overzicht met statistieken, volgende levering en actieknoppen |
| **Mijn Leveringen** | `_build_chauffeur_leveringen_page` | Tabel met alle toegewezen leveringen |
| **Route** | `_build_chauffeur_route_page` | Route overzicht met aantal stops en geschatte duur |

### Manager (4 tabs)
| Tab | Functie | Beschrijving |
|-----|---------|--------------|
| **Dashboard** | `_build_manager_dashboard_page` | KPI's en chauffeur prestaties overzicht |
| **Prestaties** | `_build_manager_prestaties_page` | Gedetailleerde chauffeur prestatie tabel |
| **Gebruikers** | `_build_manager_users_page` | Account beheer (aanmaken/verwijderen) |
| **Rapporten** | `_build_manager_rapporten_page` | Export opties (CSV) en samenvatting statistieken |

### Klant (3 tabs)
| Tab | Functie | Beschrijving |
|-----|---------|--------------|
| **Dashboard** | `_build_klant_dashboard_page` | Overzicht met status en recente bestellingen |
| **Bestellingen** | `_build_klant_bestellingen_page` | Tabel met alle bestellingen en zoekfunctie |
| **Tracking** | `_build_klant_tracking_page` | Live tracking met status updates |

---

## Technische Wijzigingen

### Aangepaste Bestanden
- `desktop_main.py` - Hoofdbestand met alle GUI logica

### Aangepaste Functies
1. **`_pages_for_role()`** - Definieert de tabs per rol
2. **`show_page()`** - Routeert naar de juiste pagina builder
3. **`_login_success()`** - Redirect naar correcte dashboard na login

### Nieuwe Functies
- `_build_chauffeur_dashboard_page()`
- `_build_chauffeur_leveringen_page()`
- `_build_chauffeur_route_page()`
- `_build_manager_dashboard_page()`
- `_build_manager_prestaties_page()`
- `_build_manager_users_page()`
- `_build_manager_rapporten_page()`
- `_build_klant_dashboard_page()`
- `_build_klant_bestellingen_page()`
- `_build_klant_tracking_page()`
- `_export_all_bestellingen_csv()`

---

## Hoe het werkt

1. Gebruiker logt in met een account
2. Systeem bepaalt de rol (planner/chauffeur/manager/klant)
3. `_pages_for_role()` geeft de beschikbare tabs terug
4. Navigatiebalk wordt opgebouwd met deze tabs
5. Klikken op een tab roept `show_page()` aan
6. `show_page()` roept de juiste `_build_*_page()` functie aan

---

## Test Accounts
| Rol | Email | Wachtwoord |
|-----|-------|------------|
| Planner | planner@gmail.com | wachtwoord |
| Chauffeur | chaffeur@gmail.com | wachtwoord |
| Klant | klant@gmail.com | wachtwoord |
| Manager | manager@gmail.com | wachtwoord |

---

## Resultaat
Alle rollen hebben nu een consistente tab-gebaseerde navigatie, waardoor gebruikers makkelijk kunnen schakelen tussen verschillende functies binnen hun dashboard.
