# Installatie Instructies

## Windows

### Stap 1: Python installeren
1. Download Python van [python.org](https://www.python.org/downloads/)
2. Installeer Python (versie 3.10 of hoger)
3. Zorg dat "Add Python to PATH" aangevinkt is tijdens installatie

### Stap 2: Project downloaden
```bash
git clone <repository-url>
cd team7
```

Of download als ZIP en pak uit.

### Stap 3: Dependencies installeren (optioneel)
```bash
pip install -r requirements.txt
```

**Let op:** Flask is alleen nodig als je de webserver wilt gebruiken. De desktop applicatie werkt zonder extra dependencies.

### Stap 4: Applicatie starten
```bash
pythonw desktop_main.pyw
```

Of dubbelklik op `desktop_main.pyw` in Windows Verkenner.

## Linux/Mac

### Stap 1: Python controleren
```bash
python3 --version
```

Python 3.10 of hoger is vereist.

### Stap 2: Project downloaden
```bash
git clone <repository-url>
cd team7
```

### Stap 3: Dependencies installeren (optioneel)
```bash
pip3 install -r requirements.txt
```

### Stap 4: Applicatie starten
```bash
python3 desktop_main.pyw
```

## Eerste gebruik

Bij het eerste opstarten:
1. De database wordt automatisch aangemaakt
2. Test accounts worden aangemaakt
3. Test data (klanten, chauffeurs) wordt toegevoegd

Log in met een van de test accounts (zie README.md).

## Problemen oplossen

### "No module named 'tkinter'"
**Windows:** Herinstalleer Python met "tcl/tk and IDLE" aangevinkt.

**Linux:**
```bash
sudo apt-get install python3-tk
```

**Mac:**
Tkinter is standaard meegeleverd met Python op Mac.

### Database errors
Verwijder `quickdelivery.db` en start de applicatie opnieuw. De database wordt opnieuw aangemaakt.

### Logo ontbreekt
Bij eerste start wordt gevraagd om een logo te selecteren. Dit is optioneel en kan overgeslagen worden.
