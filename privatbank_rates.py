from datetime import datetime, timedelta
from aiofile import async_open
from aiopath import AsyncPath
from colorama import Fore
import asyncio
import aiohttp
import platform
import time
import sys


# run code in terminal: python privatbank_rates.py 2   or   python privatbank_rates.py 2 USD EUR PLN

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?date="


# кастомне виключення для обробки помилок HTTP
class HttpError(Exception):
    pass


# cервіс для запитів до API Приватбанку.
class PrivatbankAPI:
    def __init__(self):
        self.session = aiohttp.ClientSession()  # створюємо асинхронну сесію для запитів

    # асинхронний метод для закриття сесії
    async def close(self):
        await self.session.close()

    # асинхронний метод для отримання курсів валют на дату
    async def get_rates(self, date_str: str):
        url = API_URL + date_str  # формуємо URL запиту
        async with self.session.get(url) as resp:  # асинхронний запит до API
            if resp.status == 200:  # перевіряємо статус відповіді
                data = await resp.json()  # отримуємо JSON-дані з відповіді
                return data
            else:
                raise HttpError(f"Error status: {resp.status} for {url}")


# базова логіка отримання курсів за N днів.
async def fetch_currency_rates(days: int, currencies: list[str]):
    if days < 1 or days > 10:  # перевіряємо, що дні в межах 1-10
        raise ValueError("You can only request rates for the last 1–10 days.")

    # створюємо екземпляр API
    api = PrivatbankAPI()
    result = []

    # обробляємо запити і збираємо дані
    try:
        for i in range(days):
            date = datetime.now() - timedelta(days=i)  # отримуємо дату N днів тому
            date_str = date.strftime("%d.%m.%Y")  # формат дати для API

            data = await api.get_rates(date_str)  # запит до API
            rates = data.get("exchangeRate", [])  # отримуємо список курсів

            # фільтруємо тільки потрібні валюти і формуємо результат
            day_rates = {}
            for rate in rates:
                # перевіряємо, чи валюта в списку запитуваних
                if rate.get("currency") in currencies:
                    day_rates[rate["currency"]] = {  # формуємо словник з курсами
                        "sale": rate.get("saleRate"),
                        "purchase": rate.get("purchaseRate"),
                    }

            result.append({date_str: day_rates})

    except HttpError as err:
        print("HTTP error:", err)
    finally:
        await api.close()  # закриваємо сесію

    return result


# функція для логування запитів
async def log_command(
    days: int, currencies: list[str], elapsed: float, data: list[dict]
):

    log_path = AsyncPath("logs.txt")  # шлях до файлу логу
    # поточний час у форматі YYYY-MM-DD HH:MM:SS
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    currencies_str = ", ".join(currencies)  # конвертуємо список валют у рядок
    line = (
        f"{now} - Requested: {days} days, Currencies: {currencies_str} - "  # формуємо рядок для логу
        f"Execution time: {elapsed:.2f} sec\n"
    )

    body = ""  # тіло логу, де будуть курси валют
    for day in data:
        for date_str, rates in day.items():  # перебираємо дні і курси
            body += f"{date_str}:\n"  
            if not rates:
                body += "  No data.\n" 
            else:
                # перебираємо валюти і їх значення
                for currency, values in rates.items():
                    sale = values.get("sale") 
                    purchase = values.get("purchase")   
                    body += f"  {currency}: Purchase = {purchase}, Sale = {sale}\n" 
            body += "\n"

    # асинхронно відкриваємо файл і записуємо рядок
    async with async_open(log_path, mode="a") as afp:
        await afp.write(line + body)  


async def main():

    start_time = time.perf_counter()

    # перевіряємо, чи передані аргументи
    if len(sys.argv) < 2:
        print("Usage: python main.py <days> [currency1 currency2 ...]")
        return

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("The days parameter must be a number.")
        return

    # валюти беремо з аргументів, якщо вони є, інакше за умовчанням ["USD", "EUR"]
    if len(sys.argv) > 2:
        currencies = [
            arg.upper() for arg in sys.argv[2:]
        ]  # конвертуємо валюти в верхній регістр, (з 3 аргументу)
    else:
        currencies = ["USD", "EUR"]

    try:
        # асинхронно отримуємо курси валют
        data = await fetch_currency_rates(days, currencies)
        print(data)

        # виводимо результати
        for day in data:
            for date_str, rates in day.items():
                print(f"\n {Fore.BLUE} Date: {date_str}{Fore.RESET}")
                if not rates:
                    print("There is no data for the selected currencies.")
                else:
                    for currency, values in rates.items():
                        sale = values.get("sale")
                        purchase = values.get("purchase")
                        print(f"{Fore.YELLOW}  {currency}:{Fore.RESET}")
                        print(f"    Purchase: {purchase}")
                        print(f"    Sale: {sale}")

    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    elapsed = time.perf_counter() - start_time  # обчислюємо час виконання

    # асинхронно логуємо запит з часом виконання
    await log_command(days, currencies, elapsed, data)
    
    print(f"\nExecution time: {elapsed:.2f} sec")


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
