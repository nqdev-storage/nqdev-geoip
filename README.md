[![CodeQL](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/github-code-scanning/codeql)
[![Python App Flask CI](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/python-app-testing.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/python-app-testing.yml)
[![Update GeoIP Databases](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/geoip_update.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/geoip_update.yml)

# nqdev-geoip

Free updated GeoIP legacy databases

## libs

### env

-   `pip install virtualenv`
-   `virtualenv env -p E:\sys\services\Python\Python311\python.exe`
-   `.\env\Scripts\activate`
-   `deactivate`
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

### Other

```bash
curl --location 'http://localhost:5000/instagram/getinfo?username=bngoc.winwin'
```

---

# GeoLite.mmdb

[MaxMind's GeoLite2](https://dev.maxmind.com/geoip/geoip2/geolite2/) Country, City, and ASN databases

## Download

### URL1

-   [GeoLite2-ASN.mmdb](https://git.io/GeoLite2-ASN.mmdb)
-   [GeoLite2-City.mmdb](https://git.io/GeoLite2-City.mmdb)
-   [GeoLite2-Country.mmdb](https://git.io/GeoLite2-Country.mmdb)

### URL2

-   [GeoLite2-ASN.mmdb](https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-ASN.mmdb)
-   [GeoLite2-City.mmdb](https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb)
-   [GeoLite2-Country.mmdb](https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb)

## License

-   Database and Contents Copyright (c) [MaxMind](https://www.maxmind.com/), Inc.
-   [GeoLite2 End User License Agreement](https://www.maxmind.com/en/geolite2/eula)
-   [Creative Commons Corporation Attribution-ShareAlike 4.0 International License (the "Creative Commons License")](https://creativecommons.org/licenses/by-sa/4.0/)

---
