# QuickDelivery

Een plannings- en trackingsysteem voor leveringen met desktop applicatie.

## Download

### Optie 1: Download ZIP (Makkelijkst)
1. Klik op de groene **Code** knop bovenaan deze pagina
2. Klik op **Download ZIP**
3. Pak het ZIP bestand uit
4. Ga naar de uitgepakte map

### Optie 2: Git Clone
```bash
git clone https://github.com/Nilshendy/Project-QuickDelivery-.git
cd Project-QuickDelivery-
```

## Vereisten

- Python 3.10 of hoger (download van [python.org](https://www.python.org/downloads/))
- Tkinter (standaard meegeleverd met Python)

## Installatie

**Geen installatie nodig!** De applicatie werkt direct zonder extra dependencies.

*(Optioneel: `pip install -r requirements.txt` alleen als je de Flask webserver wilt gebruiken)*

## Applicatie starten

### Windows
Dubbelklik op `desktop_main.pyw`

Of via command line:
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
