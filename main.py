"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Přemysl Ježek
email: j.prema@seznam.cz

"""

import sys
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # převod relativních odkazů na absolutní

# Base URL pro doplnění relativních odkazů
ZAKLAD_URL = "https://www.volby.cz/pls/ps2017nss/"

def stahnout_html(adresa: str) -> str:
    """Stáhne HTML a vrátí text; vyhodí výjimku při HTTP chybě."""
    r = requests.get(adresa, timeout=20)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text

def cti_cislo(text: str, default: int = 0) -> int:
    """Převede '1 234' / '1\xa0234' / '1 234' na int; nečíselné → default."""
    s = str(text or "")
    for sep in (" ", "\xa0", "\u202f", ","):
        s = s.replace(sep, "")
    if s == "":
        return default
    sign = s[0] if s and s[0] in "+-" else ""
    body = s[1:] if sign else s
    return int(sign + body) if body.isdigit() else default

def najdi_obce(html_stranka: str):
    """Z ps32 stránky vrátí seznam (kod_obce, nazev_obce, url_detail)."""
    doc = BeautifulSoup(html_stranka, "html.parser")
    tabulky = [t for t in doc.find_all("table") if str(t.get("id", "")).startswith("ps311_t")]
    if not tabulky:  # záložní detekce podle hlaviček
        for t in doc.find_all("table"):
            head = " ".join(h.get_text(strip=True).lower() for h in t.find_all("th"))
            if ("číslo" in head or "cislo" in head) and ("název" in head or "nazev" in head):
                tabulky.append(t)

    seznam, videne = [], set()
    for t in tabulky:
        for tr in t.find_all("tr")[1:]:
            td = tr.find_all("td")
            if len(td) < 2:
                continue
            kod = td[0].get_text(strip=True).replace("\xa0", " ")
            nazev = td[1].get_text(strip=True)
            a = td[0].find("a") or td[-1].find("a")
            if not a or not a.get("href"):
                continue
            url = urljoin(ZAKLAD_URL, a["href"])
            if "ps311" not in url and "xvyber" not in url:
                continue
            if kod not in videne:
                videne.add(kod)
                seznam.append((kod, nazev, url))
    return seznam

def precti_obec(html_stranka: str):
    """Z ps311 stránky vrátí (registrovani, obalky, platne, hlasy_dict, poradi_stran)."""
    doc = BeautifulSoup(html_stranka, "html.parser")

    registrovani = obalky = platne = 0
    prvni = doc.find("table")
    if prvni:
        for tr in prvni.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cells) >= 7 and cells[0].isdigit():
                registrovani = cti_cislo(cells[3])
                obalky       = cti_cislo(cells[4])
                platne       = cti_cislo(cells[6])
                break

    hlasy, poradi = {}, []
    for t in doc.find_all("table"):
        head = " ".join(h.get_text(strip=True).lower() for h in t.find_all("th"))
        if "strana" in head and ("platné" in head or "platne" in head):
            for tr in t.find_all("tr"):
                td = tr.find_all("td")
                if len(td) < 3:
                    continue
                cislo = td[0].get_text(strip=True)
                nazev = td[1].get_text(strip=True)
                pocet = td[2].get_text(strip=True).replace("\xa0", "").replace(" ", "")
                if cislo.isdigit() and any(ch.isalpha() for ch in nazev) and pocet.isdigit():
                    if nazev not in poradi:
                        poradi.append(nazev)
                    hlasy[nazev] = int(pocet)
    return registrovani, obalky, platne, hlasy, poradi

def main():
    if len(sys.argv) != 3:
        print('Použití: python main.py "<URL ps32>" "vysledky.csv"')
        sys.exit(1)

    url_ps32, cesta_vystup = sys.argv[1], sys.argv[2]

    print("Start: stahuji data…")
    try:
        html_seznam = stahnout_html(url_ps32)
    except Exception as e:
        print("Chyba při stahování seznamu obcí:", e)
        sys.exit(2)

    obce = najdi_obce(html_seznam)
    if not obce:
        print("Na stránce nebyly nalezeny obce (je to opravdu ps32 stránka?).")
        sys.exit(3)

    radky, poradi_stran = [], []
    for i, (kod, nazev, url) in enumerate(obce):
        try:
            html_detail = stahnout_html(url)
        except Exception:
            continue
        reg, ob, pl, hlasy, poradi = precti_obec(html_detail)
        if i == 0:
            poradi_stran = poradi[:]
        else:
            for s in poradi:
                if s not in poradi_stran:
                    poradi_stran.append(s)
        radky.append({
            "kod": kod, "obec": nazev,
            "registrovani": reg, "obalky": ob, "platne": pl,
            "hlasy": hlasy
        })

    hlavicka = ["kod_obce", "obec", "registrovani_volici", "vydane_obalky", "platne_hlasy"] + poradi_stran
    # CSV pro český Excel – UTF-8 s BOM (poradil kolega v práci)
    with open(cesta_vystup, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(hlavicka)
        for r in radky:
            row = [r["kod"], r["obec"], r["registrovani"], r["obalky"], r["platne"]]
            row += [int(r["hlasy"].get(s, 0)) for s in poradi_stran]
            w.writerow(row)

    print(f"Hotovo. Načteno obcí: {len(radky)}. Uloženo do: {cesta_vystup}")

if __name__ == "__main__":
    main()
