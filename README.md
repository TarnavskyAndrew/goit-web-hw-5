# PrivatBankRates

**PrivatBankRates** is an asynchronous command-line utility written in Python for retrieving and displaying currency exchange rates from PrivatBank over a specified number of days.  
The tool allows you to select specific currencies and logs all requests for further reference.

---

## Features

- Fetches exchange rates for up to 10 previous days
- Supports custom currency selection (e.g., USD, EUR, PLN)
- Asynchronous HTTP requests via `aiohttp`
- Request logging to `logs.txt` using `aiofile` and `aiopath`
- Colored console output

---

## Requirements

- Python >=3.8, <3.13
- Poetry (recommended) or pip

Dependencies:

- `aiohttp`
- `aiofile`
- `aiopath`
- `colorama`

---

## Installation

Using Poetry:

```bash
poetry install
```
--- 


## Usage

Run the script with:

```bash
python privatbank_rates.py <days> [currency1 currency2 ...]
```
Arguments:

`<days>`  — number of days to retrieve (1–10)
<br />
`[currency1 currency2 ...]`  — optional list of currencies to display (default: USD, EUR)

--- 

## API Documentation

This project uses the public PrivatBank API:

[PrivatBank Exchange Rates API Documentation](https://api.privatbank.ua/#p24/exchange)

---

