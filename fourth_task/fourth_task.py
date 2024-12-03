import xml.etree.ElementTree as ET
import json
import os
from typing import List, Dict, Any
import statistics


def parse_xml_file(file_path: str) -> List[Dict[str, Any]]:
    """Парсинг отдельного XML файла"""
    tree = ET.parse(file_path)
    root = tree.getroot()

    items = []
    for item in root.findall(".//clothing"):
        clothing_dict = {}
        for child in item:
            # Очистка от лишних пробелов и перевода строк
            text = child.text.strip() if child.text else None

            # Преобразование типов данных
            if child.tag in ["id", "reviews", "price"]:
                clothing_dict[child.tag] = int(text) if text else None
            elif child.tag == "rating":
                clothing_dict[child.tag] = float(text) if text else None
            else:
                clothing_dict[child.tag] = text
        items.append(clothing_dict)
    return items


def process_data(directory_path: str) -> Dict[str, Any]:
    """Обработка всех XML файлов в директории"""
    all_items: List[Dict[str, Any]] = []

    # Сбор данных из всех XML файлов
    for filename in os.listdir(directory_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(directory_path, filename)
            items = parse_xml_file(file_path)
            all_items.extend(items)

    # Сохранение всех данных в JSON
    with open("all_clothing.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    # Сортировка по цене
    sorted_by_price = sorted(
        all_items,
        key=lambda x: (
            x.get("price", float("-inf"))
            if x.get("price") is not None
            else float("-inf")
        ),
    )
    with open("sorted_by_price.json", "w", encoding="utf-8") as f:
        json.dump(sorted_by_price, f, ensure_ascii=False, indent=2)

    # Фильтрация: только эксклюзивные товары
    exclusive_items = [item for item in all_items if item.get("exclusive") == "yes"]
    with open("exclusive_items.json", "w", encoding="utf-8") as f:
        json.dump(exclusive_items, f, ensure_ascii=False, indent=2)

    # Статистика по цене
    prices = [item["price"] for item in all_items if item.get("price") is not None]
    price_stats: Dict[str, Any] = {}
    if prices:
        price_stats = {
            "min": min(prices),
            "max": max(prices),
            "mean": statistics.mean(prices),
            "median": statistics.median(prices),
            "sum": sum(prices),
        }
    with open("price_stats.json", "w", encoding="utf-8") as f:
        json.dump(price_stats, f, ensure_ascii=False, indent=2)

    # Частота категорий
    category_frequency: Dict[str, int] = {}
    for item in all_items:
        category = item.get("category")
        if category:
            category_frequency[category] = category_frequency.get(category, 0) + 1

    with open("category_frequency.json", "w", encoding="utf-8") as f:
        json.dump(category_frequency, f, ensure_ascii=False, indent=2)

    return {
        "total_items": len(all_items),
        "price_stats": price_stats,
        "category_frequency": category_frequency,
    }


if __name__ == "__main__":
    directory_path = r"D:\data_lab3\data_tasks\4"
    try:
        results = process_data(directory_path)
        print("Обработка завершена успешно!")
        print(f"Всего обработано товаров: {results['total_items']}")
        print("\nСтатистика по ценам:")
        for key, value in results["price_stats"].items():
            print(f"{key}: {value}")
        print("\nЧастота категорий:")
        for category, count in results["category_frequency"].items():
            print(f"{category}: {count}")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
