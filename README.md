Einfache Django-Anwendung zur Verwaltung von elektronischen Rechnungen (XRechnung 3.0+).

Funktionen:

* Firmenliste
* Kundenliste
* Adressliste
* Rechnungen (mit Anlagen)
* Export XRechnung
* Import XRechnung (mit eingebetteten Anlagen)
* PDF-Export (mit Firmenlogo)
* Import/Export von Positionen in Form von CSV-Dateien

 Einfach unter Deboan 11 ausprobieren ;-) 

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