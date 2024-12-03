import os
import json
from bs4 import BeautifulSoup
import re
from statistics import mean, median
from collections import Counter


def extract_price(price_text):
    # Извлекаем числовое значение цены
    return int(re.sub(r"[^\d]", "", price_text))


def parse_product(product_div):
    # Парсинг данных отдельного продукта
    product = {}

    # ID продукта
    favorite_link = product_div.find("a", class_="add-to-favorite")
    if favorite_link and "data-id" in favorite_link.attrs:
        product["id"] = favorite_link["data-id"]

    # Название и характеристики из названия
    name_span = product_div.find("span")
    if name_span:
        name = name_span.text.strip()
        display_match = re.search(r'([\d.]+)"', name)
        if display_match:
            product["display"] = display_match.group(1)

        name_parts = name.split()
        if len(name_parts) > 1:
            product["brand"] = name_parts[1]

        storage_match = re.search(r"(\d+)GB", name)
        if storage_match:
            product["storage"] = storage_match.group(1)

    # Цена
    price_elem = product_div.find("price")
    if price_elem:
        product["price"] = extract_price(price_elem.text)

    # Характеристики из списка
    specs_ul = product_div.find("ul")
    if specs_ul:
        specs = specs_ul.find_all("li")
        for spec in specs:
            if "type" in spec.attrs:
                spec_type = spec["type"]
                spec_value = spec.text.strip()
                product[spec_type] = spec_value

    return product


def process_files(directory):
    products = []

    # Обход всех файлов в директории
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file.read(), "html.parser")
                product_divs = soup.find_all("div", class_="product-item")

                for product_div in product_divs:
                    product = parse_product(product_div)
                    if product:
                        products.append(product)

    return products


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    directory = r"D:\data_lab3\data_tasks\2"
    products = process_files(directory)

    if not products:
        print("Не удалось получить данные о продуктах")
        return

    # Сохранение всех данных
    save_json(products, "products.json")

    # Сортировка по цене
    sorted_products = sorted(products, key=lambda x: x.get("price", 0))
    save_json(sorted_products, "sorted_products.json")

    # Фильтрация по бренду
    filtered_products = [p for p in products if p.get("brand") == "Apple"]
    save_json(filtered_products, "filtered_products.json")

    # Статистика по цене
    prices = [p["price"] for p in products if "price" in p]
    if prices:
        price_stats = {
            "min": min(prices),
            "max": max(prices),
            "average": round(mean(prices), 2),
            "median": median(prices),
            "total": sum(prices),
        }
        save_json(price_stats, "price_stats.json")

        print("\nСтатистика по ценам:")
        for stat, value in price_stats.items():
            print(f"{stat}: {value}")

    # Частота брендов
    brands = [p["brand"] for p in products if "brand" in p]
    if brands:
        brand_frequency = Counter(brands)
        save_json(dict(brand_frequency), "brand_frequency.json")

        print("\nЧастота брендов:")
        for brand, count in brand_frequency.items():
            print(f"{brand}: {count}")


if __name__ == "__main__":
    main()
