# Python API Client für die Deutsche Bahn

## Beschreibung

Dieses Python-Skript dient als Schnittstelle zur Deutschen Bahn API, um Fahrplan- und Echtzeitdaten für einen bestimmten Bahnhof abzurufen. Es kapselt die Logik für die Authentifizierung, das Abrufen von Daten und die Verarbeitung der Antworten.

## Kernfunktionalität

Das Skript stellt eine `Station`-Klasse bereit, die die Interaktion mit der Deutschen Bahn API vereinfacht. Die Klasse kapselt Methoden zum Abrufen von Bahnhofsdaten, Fahrplaninformationen und Verspätungsinformationen.

### Klasse: `Station`

Die Klasse `Station` bietet Methoden für den Zugriff auf verschiedene Endpunkte der Deutschen Bahn API.

#### Konstruktor: `__init__(self, name, db_client_id, db_api_key)`

* **Parameter:**
  * `name` (str): Der Name des Bahnhofs.
  * `db_client_id` (str): Die Client-ID für die Deutsche Bahn API.
  * `db_api_key` (str): Der API-Schlüssel für die Deutsche Bahn API.
* **Funktionalität:**
  * Initialisiert eine Instanz der Klasse `Station`.
  * Speichert den Bahnhofsnamen.
  * Ruft die EVA-Nummer des Bahnhofs anhand des Namens ab.
  * Definiert die Header für API-Anfragen unter Verwendung der bereitgestellten `db_client_id` und `db_api_key`.

#### Methoden:

* `get_evano_from_name(self, name)`
  * **Parameter:**
    * `name` (str): Der Name des Bahnhofs.
  * **Rückgabewert:**
    * (str): Die EVA-Nummer des Bahnhofs oder `None`, falls nicht gefunden.
  * **Funktionalität:**
    * Liest die Datei `Bahnhoefe.csv`, um die EVA-Nummer des Bahnhofs anhand seines Namens zu finden.
    * Führt einen case-insensitive Vergleich durch.

* `__str__(self)`
  * **Rückgabewert:**
    * (str): Eine JSON-String-Repräsentation der Stationsdaten.
  * **Funktionalität:**
    * Gibt die Stationsdaten als String zurück.

* `get_evano(self)`
  * **Rückgabewert:**
    * (str): Die EVA-Nummer des Bahnhofs.
  * **Funktionalität:**
    * Gibt die EVA-Nummer des Bahnhofs zurück.

* `send_request_planned(self, date, hour)`
  * **Parameter:**
    * `date` (str): Das Datum im Format "JJMMTT".
    * `hour` (str): Die Stunde im Format "HH".
  * **Rückgabewert:**
    * (dict): Die Antwort der API im Dictionary-Format, oder `None` bei einem Fehler.
  * **Funktionalität:**
    * Sendet eine Anfrage an die Deutsche Bahn API, um die geplanten Ankunfts- und Abfahrtszeiten für den Bahnhof zu einer bestimmten Zeit abzurufen.
    * Verarbeitet die XML-Antwort und konvertiert sie in ein Dictionary.
    * Gibt den Fehlercode aus, falls die Anfrage fehlschlägt.

* `send_request_planned_many(self, date, hour, num_hours=1)`
  * **Parameter:**
    * `date` (str): Das Datum im Format "JJMMTT".
    * `hour` (str): Die Stunde im Format "HH".
    * `num_hours` (int, optional): Die Anzahl der Stunden, für die Daten abgerufen werden sollen. Standardwert ist 1.
  * **Rückgabewert:**
    * (dict): Die zusammengeführte Antwort der API im Dictionary-Format, oder `None`, falls keine Daten vorhanden sind.
  * **Funktionalität:**
    * Sendet Anfragen an die Deutsche Bahn API für einen Bereich von Stunden.
    * Verarbeitet die XML-Antwort und konvertiert sie in ein Dictionary.
    * Führt die Antworten für jede Stunde zu einer einzigen Antwort zusammen.
    * Gibt den Fehlercode aus, falls eine Anfrage fehlschlägt.

* `send_request_delay(self)`
  * **Rückgabewert:**
    * (dict): Die Antwort der API im Dictionary-Format, oder `None` bei einem Fehler.
  * **Funktionalität:**
    * Sendet eine Anfrage an die Deutsche Bahn API, um die aktuellen Verspätungen für den Bahnhof abzurufen.
    * Verarbeitet die XML-Antwort und konvertiert sie in ein Dictionary.
    * Gibt den Fehlercode aus, falls die Anfrage fehlschlägt.

* `get_train_data(self, date=datetime.now().strftime("%y%m%d"), hour=datetime.now().strftime("%H"))`
  * **Parameter:**
    * `date` (str, optional): Das Datum im Format "JJMMTT". Standardwert ist das aktuelle Datum.
    * `hour` (str, optional): Die Stunde im Format "HH". Standardwert ist die aktuelle Stunde.
  * **Rückgabewert:**
    * (list): Eine Liste von `Train`-Objekten, die die Fahrplandaten und Verspätungsinformationen enthalten.
  * **Funktionalität:**
    * Ruft die geplanten Abfahrtszeiten und Verspätungsinformationen ab.
    * Erstellt eine Liste von `Train`-Objekten, die die relevanten Daten enthalten.
    * Verarbeitet die API-Antworten und extrahiert die Zugdaten.

* `get_sorted_departure_list(self, delay=True, date=datetime.now().strftime("%y%m%d"), hour=datetime.now().strftime("%H"), time_flag=int(datetime.now().strftime("%y%m%d%H%M")))`
  * **Parameter:**
    * `delay` (bool, optional): Gibt an, ob die Züge nach der tatsächlichen Abfahrtszeit (mit Verspätung) oder der geplanten Abfahrtszeit sortiert werden sollen. Standardwert ist `True`.
    * `date` (str, optional): Das Datum im Format "JJMMTT". Standardwert ist das aktuelle Datum.
    * `hour` (str, optional): Die Stunde im Format "HH". Standardwert ist die aktuelle Stunde.
    * `time_flag` (int, optional): Die Zeit im Format JJMMTTHHMM. Züge, die vor dieser Zeit abfahren, werden nicht zurückgegeben. Standardwert ist die aktuelle Zeit.
  * **Rückgabewert:**
    * (list): Eine sortierte Liste von `Train`-Objekten, die die Abfahrtszeiten enthalten, gefiltert nach der `time_flag`.
  * **Funktionalität:**
    * Ruft die Zugdaten ab und sortiert sie nach der geplanten oder tatsächlichen Abfahrtszeit.
    * Filtert die Züge, die vor der angegebenen `time_flag` abfahren.
    * Gibt die sortierte und gefilterte Liste von Zügen zurück.

### Klasse: `Train`

Die Klasse `Train` wird verwendet, um die Daten für einen einzelnen Zug zu speichern. Sie wird von der Klasse `Station` intern verwendet.

#### Konstruktor: `__init__(self, station_name, arrival_planned, arrival_actual, departure_planned, departure_actual, platform_planned, platform_actual, canceled, train_number, train_type, train_category, train_id, past_destinations, future_destinations)`

* **Parameter:**
  * `station_name` (str): Der Name des Bahnhofs.
  * `arrival_planned` (str): Die geplante Ankunftszeit.
  * `arrival_actual` (str): Die tatsächliche Ankunftszeit.
  * `departure_planned` (str): Die geplante Abfahrtszeit.
  * `departure_actual` (str): Die tatsächliche Abfahrtszeit.
  * `platform_planned` (str): Das geplante Gleis.
  * `platform_actual` (str): Das tatsächliche Gleis.
  * `canceled` (bool): Gibt an, ob der Zug ausfällt.
  * `train_number` (str): Die Zugnummer.
  * `train_type` (str): Der Zugtyp.
  * `train_category` (str): Die Zugkategorie.
  * `train_id` (str): Die Zug-ID.
  * `past_destinations` (str): Die vergangenen Ziele.
  * `future_destinations` (str): Die zukünftigen Ziele.
* **Funktionalität:**
  * Initialisiert eine Instanz der Klasse `Train`.
  * Speichert die Zugdaten.
  * Berechnet, ob sich das Gleis geändert hat (`platform_change`).
  * Ermittelt das Endziel (`final_destination`) und die Startstation (`start_station`).

### Methoden:

* `print_train(self)`
  * **Funktionalität:**
    * Gibt die Zuginformationen auf der Konsole aus.

## Verwendete Module:

* `requests`: Für das Senden von HTTP-Anfragen an die Deutsche Bahn API.
* `json`: Für die Verarbeitung von JSON-Daten.
* `datetime`: Für die Arbeit mit Datums- und Zeitangaben.
* `xmltodict`: Für die Konvertierung von XML-Daten in Python-Dictionaries.
* `csv`: Für das Lesen der Datei `Bahnhoefe.csv`.
* `Train`: Eine benutzerdefinierte Klasse zur Darstellung von Zugdaten.

## Voraussetzungen:

* Python 3.x
* Die Datei `Bahnhoefe.csv` im Verzeichnis `db_api`.
* Die externen Module `requests` und `xmltodict`. Diese können mit pip installiert werden:

pip install requests xmltodict
## Verwendung:

1.  Importiere die erforderlichen Module und Klassen.

```python
import requests
import json
import datetime
import xmltodict
import csv
from Train import Train
from datetime import datetime, timedelta
Erstelle eine Instanz der Klasse Station, um auf Bahnhofsdaten zuzugreifen.  Stelle sicher, dass du deine DB-Client-Id und deinen DB-Api-Key angibst.bahnhof = Station("Dein Bahnhofsname", "DEIN_DB_CLIENT_ID", "DEIN_DB_API_KEY")
Verwende die Methoden der Klasse Station, um die gewünschten Daten abzurufen.zuege = bahnhof.get_train_data()
abfahrten = bahnhof.get_sorted_departure_list()
