---
name: scrape-wiki-cities
description: Extrae los datos de ciudades de las wikis de American Truck Simulator y Euro Truck Simulator 2 (trucksimulator.wiki.gg), incluyendo nombre, país/estado, número de compañías y todas las features (garaje, gasolinera, concesionario, etc.).
---

Usa los scripts ``scrape_ets2.py`` y ``scrape_ats.py`` para obtener los datos de ciudades de las wikis en formato JSON.

## Scraper de ETS2

Obtiene todas las ciudades de Euro Truck Simulator 2:

```bash
python3 scrape_ets2.py
```

### Filtrar por país

```bash
python3 scrape_ets2.py --country España
```

### Filtrar por ciudad

```bash
python3 scrape_ets2.py --city "A Coruña"
```

## Scraper de ATS

Obtiene todas las ciudades de American Truck Simulator:

```bash
python3 scrape_ats.py
```

### Filtrar por estado

```bash
python3 scrape_ats.py --state California
```

### Filtrar por ciudad

```bash
python3 scrape_ats.py --city "Aberdeen"
```

## Formato de salida

### ETS2

```json
{
  "countries": [
    {
      "name": "Spain",
      "flag": "https://trucksimulator.wiki.gg/images/Flag_of_Spain.png?a5e556",
      "cities": [
        {
          "name": "A Coruña",
          "companies": 10,
          "features": {
            "garage": true,
            "gasStation": false,
            "serviceShop": true,
            "recruitmentAgency": false,
            "hotel": false,
            "restStop": true,
            "dealer": "No",
            "airport": false,
            "seaport": false,
            "ferry": false,
            "tollGates": true,
            "weighStation": false,
            "borderCrossing": false,
            "viewpoint": false,
            "photoTrophy": false
          }
        }
      ]
    }
  ]
}
```

### ATS

```json
{
  "states": [
    {
      "name": "California",
      "flag": "https://trucksimulator.wiki.gg/images/Flag_of_California.png?cd1a74",
      "cities": [
        {
          "name": "Bakersfield",
          "companies": 11,
          "features": {
            "garage": true,
            "gasStation": true,
            "serviceShop": true,
            "recruitmentAgency": true,
            "hotel": false,
            "restStop": true,
            "dealer": "Kenworth",
            "airport": false,
            "seaport": false,
            "ferry": false,
            "tollGates": false,
            "weighStation": true,
            "borderCrossing": false,
            "agriculturalStation": false,
            "viewpoint": false,
            "photoTrophy": false
          }
        }
      ]
    }
  ]
}
```
