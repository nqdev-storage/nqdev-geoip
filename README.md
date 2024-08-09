# nqdev-geoip

Free updated GeoIP legacy databases

## libs

### env

-   `pip install virtualenv`
-   `virtualenv env -p E:\sys\services\Python\Python311\python.exe`
-   `.\env\Scripts\activate`
-   `python -m pip freeze > requirements.txt` -> backup package
-   `pip install -r requirements.txt` -> restorage package
-   `python manage.py makemigrations`
-   `python manage.py migrate` -> tạo database, nếu chưa có sẵn database
-   `python manage.py runserver 0.0.0.0:8000` -> start for all ip

## docs

-   https://mailfud.org/geoip-legacy/
    -   You can use my [geoip_update.sh](https://mailfud.org/geoip-legacy/geoip_update.sh) script if needed, instructions found within. Always carefully audit any downloaded scripts!

## curl test

### GeoIP.dat

```bash
curl --location 'http://localhost:5000/geoip?ip=185.213.82.249'
```

### GeoIPCity.dat

```bash
curl --location 'http://localhost:5000/geoipcity?ip=185.213.82.249'
```
