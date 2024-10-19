# Import z knihoven.
import requests
from bs4 import BeautifulSoup
import csv


def process_response_server(url: str) -> BeautifulSoup:
    """Zpracuje zadané url."""
    response = requests.get(url)
    if str(response) == "<Response [404]>":
        print(f"Zadaná stránka neexistuje. Zkontrolujte URL!\nUKONČUJI PROGRAM!")
        quit()
    elif str(response) == "<Response [500]>":
        print(f"Chyba serveru. Vyzkoušejte později.\nUKONČUJI PROGRAM!")
        quit()
    elif str(response) == "<Response [200]>":
        return BeautifulSoup(response.text, "html.parser")


def get_specific_data(soup: BeautifulSoup, tag1: str, tag2: str, class_name, keyword: str) -> list:
    """Seznam vybraných dat dle argumentů."""
    html_data = soup.find_all(tag1)
    specific_data = list()
    for tag1 in html_data:
        raw_data = tag1.find(tag2, class_=class_name)
        if raw_data is not None:
            column = {keyword: raw_data.get_text()}
            specific_data.append(column)
    return specific_data


def get_town_urls(soup: BeautifulSoup, tag1: str, tag2: str) -> list:
    """Vytvoří seznam url pro města daného kraje."""
    html_data = soup.find_all(tag1)
    town_urls = list()
    for tag1 in html_data:
        raw_data = tag1.find(tag2)
        if raw_data is not None:
            complete_url_town = f"https://www.volby.cz/pls/ps2017nss/" + raw_data.get("href")
            town_urls.append(complete_url_town)
    return town_urls


def merge_data(list_a: list, list_b: list, length: int) -> list:
    """Sloučí data vybraných slovníků."""
    for position in range(0, length):
        list_a[position].update(list_b[position])
    return list_a


def save_csv_report(file_name: str, data: list):
    """Zapíše a uloží výstupní soubor."""
    with open(file_name, mode="w", newline="") as csvfile:
        keys = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=keys, delimiter=";")

        writer.writeheader()
        for line_data in data:
            writer.writerow(line_data)


url_district = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
soup_url_district = process_response_server(url_district)

column_code = get_specific_data(soup_url_district, "tr", "td", "cislo", "code")
column_location = get_specific_data(soup_url_district, "tr", "td", "overflow_name", "location")

full_data = merge_data(column_code, column_location, len(column_code))

data_part_two = list()
data_party_votes = dict()
data_part_three = list()
data_part_four = dict()

municipality_urls = get_town_urls(soup_url_district, "tr", "a")
for url_town in municipality_urls:
    details_towns = process_response_server(url_town)
    all_tables = details_towns.find_all("table")
    tr_tag_table_one = all_tables[0].find_all("tr")
    td_tag_tables = tr_tag_table_one[2].find_all("td")
    columns = {
        "registered": td_tag_tables[3].get_text(),
        "envelopes": td_tag_tables[4].get_text(),
        "valid": td_tag_tables[7].get_text()
    }
    # pokud tyto data nedám do seznamu ale nechám ve slovníků, na který napojím data níže, tak vše funguje.
    data_part_two.append(columns)

    # Zpracování druhé části dat

    tr_tag_table_two = all_tables[1].find_all("tr")

    for tr_two in tr_tag_table_two[2::]:
        td_tag = tr_two.find_all("td")
        party = td_tag[1].get_text()
        votes = td_tag[2].get_text()
        # column_parties = {party: votes}
        data_party_votes.update({party: votes})
        # # Pokud dám tisk přímo ve smyčce - tak mi to vyhazuje správná data
        # print(data_party_votes)
    # Zde už to ukládá chybná data - respektive je přepisuje, nejspíše klíč i hodnotu, ale nevím z jakého důvodu.
    data_part_three.append(data_party_votes)

# Tisk počtu slovníků - který odpovídá délce řádků/počtu obcí (97)
print(len(data_part_three))
# Tisk jednotlivých politických stran a počet hlasů - počet hlasů nesedí, čísla odpovídají počtu hlasů z poslední obce.
print(data_part_three)

# # Stačí odkomentovat pro uložení do souboru:
# full_data = merge_data(full_data, data_part_two, len(full_data))
# full_data = merge_data(full_data, data_part_three, len(full_data))
# print(full_data)

# nazev = "testy.csv"
# save_csv_report(nazev, full_data)
