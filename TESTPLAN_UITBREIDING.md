# Testplan Uitbreiding - Dashboard Tabs

## Bestaande Tests (aanvulling)

### Test 8: Chauffeur markeren
| Veld | Waarde |
|------|--------|
| **TestID** | 8 |
| **Testscenario** | Chauffeur markeren |
| **Teststappen** | 1. Log in als chauffeur 2. Ga naar Dashboard of Mijn Leveringen 3. Selecteer een levering in de tabel 4. Klik op "Markeer Onderweg" of "Markeer Afgeleverd" |
| **Verwachte resultaat** | Status van de levering wordt bijgewerkt en tabel wordt ververst |

---

## Nieuwe Tests voor Dashboard Tabs

### Chauffeur Dashboard Tests

| TestID | Testscenario | Teststappen | Verwachte resultaat |
|--------|--------------|-------------|---------------------|
| 9 | Chauffeur tabs navigatie | 1. Log in als chauffeur 2. Klik op tab "Mijn Leveringen" 3. Klik op tab "Route" 4. Klik op tab "Dashboard" | Gebruiker kan schakelen tussen alle 3 tabs zonder errors |
| 10 | Chauffeur leveringen bekijken | 1. Log in als chauffeur 2. Ga naar tab "Mijn Leveringen" | Tabel toont alle toegewezen leveringen met volgorde, ID, klant, adres, ETA en status |
| 11 | Chauffeur route bekijken | 1. Log in als chauffeur 2. Ga naar tab "Route" | Route overzicht toont aantal stops en geschatte duur |
| 12 | Chauffeur levering status update | 1. Log in als chauffeur 2. Ga naar "Mijn Leveringen" 3. Selecteer levering 4. Klik "Markeer Onderweg" | Levering status verandert naar "Onderweg" |
| 13 | Chauffeur levering afleveren | 1. Log in als chauffeur 2. Selecteer levering met status "Onderweg" 3. Klik "Markeer Afgeleverd" | Levering status verandert naar "Afgeleverd" |

### Manager Dashboard Tests

| TestID | Testscenario | Teststappen | Verwachte resultaat |
|--------|--------------|-------------|---------------------|
| 14 | Manager tabs navigatie | 1. Log in als manager 2. Klik op alle tabs: Dashboard, Prestaties, Gebruikers, Rapporten | Gebruiker kan schakelen tussen alle 4 tabs zonder errors |
| 15 | Manager prestaties bekijken | 1. Log in als manager 2. Ga naar tab "Prestaties" | Tabel toont chauffeur prestaties met totaal, afgeleverd, onderweg, gepland en gem. levertijd |
| 16 | Manager gebruiker aanmaken | 1. Log in als manager 2. Ga naar tab "Gebruikers" 3. Vul email, wachtwoord en rol in 4. Klik "Account Aanmaken" | Nieuw account wordt aangemaakt en verschijnt in de tabel |
| 17 | Manager gebruiker verwijderen | 1. Log in als manager 2. Ga naar "Gebruikers" 3. Selecteer een gebruiker 4. Klik "Verwijder Geselecteerde" 5. Bevestig | Gebruiker wordt verwijderd uit de tabel |
| 18 | Manager CSV export prestaties | 1. Log in als manager 2. Ga naar tab "Rapporten" 3. Klik "Export Chauffeur Prestaties (CSV)" 4. Kies locatie | CSV bestand wordt opgeslagen met chauffeur prestatie data |
| 19 | Manager CSV export bestellingen | 1. Log in als manager 2. Ga naar "Rapporten" 3. Klik "Export Alle Bestellingen (CSV)" 4. Kies locatie | CSV bestand wordt opgeslagen met alle bestellingen |
| 20 | Manager statistieken bekijken | 1. Log in als manager 2. Ga naar tab "Rapporten" | Samenvatting toont totaal, afgeleverd, onderweg, gepland, geannuleerd en succes ratio |

### Klant Dashboard Tests

| TestID | Testscenario | Teststappen | Verwachte resultaat |
|--------|--------------|-------------|---------------------|
| 21 | Klant tabs navigatie | 1. Log in als klant 2. Klik op alle tabs: Dashboard, Bestellingen, Tracking | Gebruiker kan schakelen tussen alle 3 tabs zonder errors |
| 22 | Klant bestellingen bekijken | 1. Log in als klant 2. Ga naar tab "Bestellingen" | Tabel toont alle bestellingen met ID, klant, afleveradres, status en ETA |
| 23 | Klant bestellingen zoeken | 1. Log in als klant 2. Ga naar "Bestellingen" 3. Typ zoekterm in zoekveld | Tabel filtert bestellingen op basis van zoekterm |
| 24 | Klant tracking bekijken | 1. Log in als klant 2. Ga naar tab "Tracking" | Huidige status wordt getoond met recente status updates |
| 25 | Klant auto-refresh | 1. Log in als klant 2. Ga naar Dashboard 3. Vink "Auto-refresh (5 sec)" aan | Bestellingen en status updates worden elke 5 seconden automatisch ververst |

---

## Kopie voor Excel (tab-gescheiden)

```
TestID	Testscenario	Teststappen	Verwachte resultaat
8	Chauffeur markeren	1. Log in als chauffeur 2. Ga naar Dashboard of Mijn Leveringen 3. Selecteer een levering 4. Klik op "Markeer Onderweg" of "Markeer Afgeleverd"	Status van de levering wordt bijgewerkt en tabel wordt ververst
9	Chauffeur tabs navigatie	1. Log in als chauffeur 2. Klik op tab "Mijn Leveringen" 3. Klik op tab "Route" 4. Klik op tab "Dashboard"	Gebruiker kan schakelen tussen alle 3 tabs zonder errors
10	Chauffeur leveringen bekijken	1. Log in als chauffeur 2. Ga naar tab "Mijn Leveringen"	Tabel toont alle toegewezen leveringen met volgorde, ID, klant, adres, ETA en status
11	Chauffeur route bekijken	1. Log in als chauffeur 2. Ga naar tab "Route"	Route overzicht toont aantal stops en geschatte duur
12	Chauffeur levering status update	1. Log in als chauffeur 2. Ga naar "Mijn Leveringen" 3. Selecteer levering 4. Klik "Markeer Onderweg"	Levering status verandert naar "Onderweg"
13	Chauffeur levering afleveren	1. Log in als chauffeur 2. Selecteer levering met status "Onderweg" 3. Klik "Markeer Afgeleverd"	Levering status verandert naar "Afgeleverd"
14	Manager tabs navigatie	1. Log in als manager 2. Klik op alle tabs: Dashboard, Prestaties, Gebruikers, Rapporten	Gebruiker kan schakelen tussen alle 4 tabs zonder errors
15	Manager prestaties bekijken	1. Log in als manager 2. Ga naar tab "Prestaties"	Tabel toont chauffeur prestaties met totaal, afgeleverd, onderweg, gepland en gem. levertijd
16	Manager gebruiker aanmaken	1. Log in als manager 2. Ga naar tab "Gebruikers" 3. Vul email, wachtwoord en rol in 4. Klik "Account Aanmaken"	Nieuw account wordt aangemaakt en verschijnt in de tabel
17	Manager gebruiker verwijderen	1. Log in als manager 2. Ga naar "Gebruikers" 3. Selecteer een gebruiker 4. Klik "Verwijder Geselecteerde" 5. Bevestig	Gebruiker wordt verwijderd uit de tabel
18	Manager CSV export prestaties	1. Log in als manager 2. Ga naar tab "Rapporten" 3. Klik "Export Chauffeur Prestaties (CSV)" 4. Kies locatie	CSV bestand wordt opgeslagen met chauffeur prestatie data
19	Manager CSV export bestellingen	1. Log in als manager 2. Ga naar "Rapporten" 3. Klik "Export Alle Bestellingen (CSV)" 4. Kies locatie	CSV bestand wordt opgeslagen met alle bestellingen
20	Manager statistieken bekijken	1. Log in als manager 2. Ga naar tab "Rapporten"	Samenvatting toont totaal, afgeleverd, onderweg, gepland, geannuleerd en succes ratio
21	Klant tabs navigatie	1. Log in als klant 2. Klik op alle tabs: Dashboard, Bestellingen, Tracking	Gebruiker kan schakelen tussen alle 3 tabs zonder errors
22	Klant bestellingen bekijken	1. Log in als klant 2. Ga naar tab "Bestellingen"	Tabel toont alle bestellingen met ID, klant, afleveradres, status en ETA
23	Klant bestellingen zoeken	1. Log in als klant 2. Ga naar "Bestellingen" 3. Typ zoekterm in zoekveld	Tabel filtert bestellingen op basis van zoekterm
24	Klant tracking bekijken	1. Log in als klant 2. Ga naar tab "Tracking"	Huidige status wordt getoond met recente status updates
25	Klant auto-refresh	1. Log in als klant 2. Ga naar Dashboard 3. Vink "Auto-refresh (5 sec)" aan	Bestellingen en status updates worden elke 5 seconden automatisch ververst
```

---

## Test Accounts
| Rol | Email | Wachtwoord |
|-----|-------|------------|
| Planner | planner@gmail.com | wachtwoord |
| Chauffeur | chaffeur@gmail.com | wachtwoord |
| Klant | klant@gmail.com | wachtwoord |
| Manager | manager@gmail.com | wachtwoord |
