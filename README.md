# Třetí projekt – Engeto Python Akademie

## Popis projektu

Skript stahuje výsledky voleb do Poslanecké sněmovny 2017 z webu **volby.cz**. Ze stránky typu **ps32** (seznam obcí vybraného okresu) 
automaticky vyhledává odkazy na detail každé obce (**ps311**), z nich načítá souhrnná čísla i počty hlasů pro všechny strany a vše 
ukládá do **CSV** se středníkem `;`.

Poznámka: CSV je v kódování **UTF-8 s BOM** (kvůli správné diakritice v českém Excelu).

---

## Instalace knihoven (pomocí `requirements.txt`)

Je doporučeno použít **virtuální prostředí** a instalovat z **příkazového řádku/terminálu**.

### Vytvoření a aktivace virtuálního prostředí

> Název adresáře může být libovolný (často `.venv` nebo `venv`).

**Windows – PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows – CMD**

```bat
py -m venv .venv
.\.venv\Scripts\activate.bat
```

**macOS / Linux (bash/zsh)**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Instalace závislostí z `requirements.txt`

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ověření instalace

```bash
python -c "import requests, bs4; print('requests:', requests.__version__, '| bs4:', bs4.__version__)"
```

---

## Spuštění projektu

Skript se spouští se **dvěma argumenty**:

1. URL stránky **ps32** (v uvozovkách, obsahuje `&`),
2. název/cesta k výstupnímu **CSV**.

**Syntaxe:**

```bash
python main.py "<URL_ps32>" "<vystupni_soubor.csv>"
```

**Příklad (okres Benešov):**

```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" "vysledky_benesov.csv"
```

---

## Ukázka výstupu v terminálu

```
Start: stahuji data…
Hotovo. Načteno obcí: 114. Uloženo do: vysledky_benesov.csv
```

---

## Minimální `requirements.txt`

```txt
requests==2.32.4
beautifulsoup4==4.13.4
```
