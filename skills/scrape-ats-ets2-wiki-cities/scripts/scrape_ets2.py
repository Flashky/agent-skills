#!/usr/bin/env python3
"""
Scraper de la wiki de Euro Truck Simulator 2 para extraer datos de ciudades.
Fuente: https://trucksimulator.wiki.gg/wiki/Cities/Euro_Truck_Simulator_2

Uso:
  python3 scrape_ets2.py                          # Todas las ciudades
  python3 scrape_ets2.py --country "España"       # Filtrar por país
  python3 scrape_ets2.py --city "A Coruña"        # Filtrar por ciudad
"""

import argparse
import json
import sys
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

WIKI_BASE = "https://trucksimulator.wiki.gg"
URL = f"{WIKI_BASE}/wiki/Cities/Euro_Truck_Simulator_2"

# Mapeo de alt text de iconos a nombres de features (camelCase)
ICON_MAP = {
    "Garage": "garage",
    "Gas": "gasStation",
    "Service Shop": "serviceShop",
    "Recruitment Agency": "recruitmentAgency",
    "Hotel": "hotel",
    "Rest Stop": "restStop",
    "Airports": "airport",
    "Seaport": "seaport",
    "Ferry": "ferry",
    "Toll Gates": "tollGates",
    "Weigh Station": "weighStation",
    "Border Crossing": "borderCrossing",
    "Viewpoint": "viewpoint",
    "Photo Trophy": "photoTrophy",
}


def parse_features(features_td):
    """Parsea la celda de features y devuelve un dict con las features presentes."""
    features = {
        "garage": False,
        "gasStation": False,
        "serviceShop": False,
        "recruitmentAgency": False,
        "hotel": False,
        "restStop": False,
        "dealer": "No",
        "airport": False,
        "seaport": False,
        "ferry": False,
        "tollGates": False,
        "weighStation": False,
        "borderCrossing": False,
        "viewpoint": False,
        "photoTrophy": False,
    }

    if not features_td:
        return features

    for a_tag in features_td.find_all("a"):
        img = a_tag.find("img")
        if not img:
            continue

        alt = img.get("alt", "")

        if alt == "Dealer ico.png":
            # El nombre del concesionario está en el title o texto del <a>
            dealer_name = a_tag.get("title") or a_tag.get_text(strip=True)
            if dealer_name:
                features["dealer"] = dealer_name
        elif alt in ICON_MAP:
            features[ICON_MAP[alt]] = True

    return features


def fetch_and_parse():
    """Descarga y parsea la página de ciudades de ETS2."""
    print(f"Descargando {URL} ...", file=sys.stderr)
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar el panel "Accessible" dentro del tabber
    accessible_panel = soup.find("article", id="Accessible-0")
    if not accessible_panel:
        print("ERROR: No se encontró el panel 'Accessible' en la página.", file=sys.stderr)
        sys.exit(1)

    table = accessible_panel.find("table", class_="wikitable")
    if not table:
        print("ERROR: No se encontró la tabla de ciudades.", file=sys.stderr)
        sys.exit(1)

    rows = table.find_all("tr")
    # Saltar la fila de encabezados (primera fila)
    data_rows = rows[1:] if len(rows) > 1 else []

    # Agrupar ciudades por país
    countries_dict = defaultdict(list)
    country_flags = {}  # country_name -> URL de la bandera

    for row in data_rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        # Columna 1: Nombre de la ciudad
        name_td = cols[0]
        city_link = name_td.find("a")
        city_name = city_link.get_text(strip=True) if city_link else name_td.get_text(strip=True)

        # Columna 2: País
        # La celda contiene: <a href="/wiki/Spain"><img alt="Flag..." /></a> <a href="/wiki/Spain">Spain</a>
        # El nombre del país está en el segundo <a> (el que tiene texto), o en el texto directo
        country_td = cols[1]
        country_links = country_td.find_all("a")
        if len(country_links) >= 2:
            country_name = country_links[1].get_text(strip=True)
        elif len(country_links) == 1:
            country_name = country_links[0].get_text(strip=True)
        else:
            country_name = country_td.get_text(strip=True)

        # Extraer la URL de la bandera del primer <a> (el que contiene el <img>)
        if country_name not in country_flags and len(country_links) >= 1:
            flag_img = country_links[0].find("img")
            if flag_img and flag_img.get("src"):
                flag_url = flag_img["src"]
                # Convertir a absoluta si es relativa
                if flag_url.startswith("/"):
                    flag_url = WIKI_BASE + flag_url
                country_flags[country_name] = flag_url

        # Columna 3: Compañías
        companies_text = cols[2].get_text(strip=True)
        try:
            companies = int(companies_text)
        except ValueError:
            companies = 0

        # Columna 4: Features
        features = parse_features(cols[3])

        city_data = {
            "name": city_name,
            "companies": companies,
            "features": features,
        }

        countries_dict[country_name].append(city_data)

    # Convertir a lista ordenada por nombre de país
    countries = [
        {
            "name": country,
            "flag": country_flags.get(country, ""),
            "cities": cities,
        }
        for country, cities in sorted(countries_dict.items())
    ]

    return {"countries": countries}


def filter_country(data, country_name):
    """Filtra los resultados por nombre de país (case-insensitive partial match)."""
    country_name_lower = country_name.lower()
    filtered_countries = [
        c for c in data["countries"]
        if country_name_lower in c["name"].lower()
    ]
    return {"countries": filtered_countries}


def filter_city(data, city_name):
    """Filtra los resultados por nombre de ciudad (case-insensitive partial match)."""
    city_name_lower = city_name.lower()
    countries = []
    for country in data["countries"]:
        filtered_cities = [
            c for c in country["cities"]
            if city_name_lower in c["name"].lower()
        ]
        if filtered_cities:
            countries.append({"name": country["name"], "cities": filtered_cities})
    return {"countries": countries}


def main():
    parser = argparse.ArgumentParser(
        description="Extrae datos de ciudades de ETS2 desde la wiki."
    )
    parser.add_argument(
        "--country",
        type=str,
        help="Filtrar por país (ej. 'España', 'France', 'Germany')",
    )
    parser.add_argument(
        "--city",
        type=str,
        help="Filtrar por ciudad (ej. 'A Coruña', 'Berlin')",
    )
    args = parser.parse_args()

    data = fetch_and_parse()

    if args.country:
        data = filter_country(data, args.country)

    if args.city:
        data = filter_city(data, args.city)

    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
