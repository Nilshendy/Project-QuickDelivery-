# QuickDelivery

Een plannings- en trackingsysteem voor leveringen met desktop applicatie.

## Vereisten

- Python 3.10 of hoger
- Tkinter (standaard meegeleverd met Python)

## Installatie

1. Clone de repository:
```bash
git clone <repository-url>
cd team7
```

2. Installeer dependencies:
```bash
pip install -r requirements.txt
```

## Applicatie starten

### Windows
```bash
pythonw desktop_main.pyw
```

### Linux/Mac
```bash
python3 desktop_main.pyw
```

De applicatie kan vanuit elke map gestart worden.

## Inloggen

De applicatie heeft standaard test accounts:

| E-mail | Wachtwoord | Rol |
|--------|-----------|-----|
| planner@gmail.com | wachtwoord | Planner |
| chaffeur@gmail.com | wachtwoord | Chauffeur |
| klant@gmail.com | wachtwoord | Klant |
| manager@gmail.com | wachtwoord | Manager |

## Functionaliteit

### Planner
- Klanten beheren
- Chauffeurs beheren
- Bestellingen aanmaken en beheren
- Routes plannen en optimaliseren
- Leveringen tracken

### Chauffeur
- Toegewezen leveringen bekijken
- Status updaten (Onderweg/Afgeleverd)
- Route volgorde met ETA

### Klant
- Bestellingen bekijken
- Status tracking
- Live updates

### Manager
- Prestatie dashboard
- Gebruikersbeheer
- CSV export van statistieken

## Database

De applicatie gebruikt SQLite. De database wordt automatisch aangemaakt bij eerste gebruik in de map waar het script staat.

## Structuur

```
team7/
├── desktop_main.py      # Hoofdapplicatie
├── desktop_main.pyw     # Windows launcher
├── app.py              # Flask webserver (optioneel)
├── requirements.txt    # Python dependencies
├── quickdelivery.db    # SQLite database (wordt automatisch aangemaakt)
├── assets/             # Logo en afbeeldingen
└── templates/          # HTML templates voor Flask
```
