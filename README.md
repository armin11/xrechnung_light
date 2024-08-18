# XRechnung light

## Beschreibung

Einfache Django-Anwendung zur Verwaltung von elektronischen Rechnungen (XRechnung 3.0+). Das Projekt ist als "Proof of Concept" gedacht und läßt sich gut für ein Django Tutorial nutzen.

## Funktionen

* Firmenliste
* Kundenliste
* Adressliste
* Rechnungen (mit Anlagen)
* Export XRechnung
* Import XRechnung (mit eingebetteten Anlagen)
* PDF-Export (mit Firmenlogo)
* Import/Export von Positionen in Form von CSV-Dateien

 ## Demo
 
https://www.armin11.de

## Installation
 
 Einfach unter Debian 11 ausprobieren ;-) 

 ```console
git clone https://github.com/armin11/xrechnung_light.git
cd xrechnung_light
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser
python3 manage.py runserver
```