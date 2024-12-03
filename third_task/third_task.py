import xml.etree.ElementTree as ET
import json
import os
import statistics
from collections import Counter


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    star_data = {}
    for child in root:
        # Проверяем, что значение не None
        if child.text is not None:
            # Удаляем лишние пробелы из текста
            value = child.text.strip()
            # Преобразуем числовые значения
            if child.tag == "radius":
                value = int(value)
            elif child.tag == "distance":
                value = float(value.split()[0])
            elif child.tag == "age":
                value = float(value.split()[0])
            star_data[child.tag] = value

    return star_data


def process_data(directory_path):
    stars_data = []

    # Собираем данные из всех XML файлов
    for filename in os.listdir(directory_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(directory_path, filename)
            star_data = parse_xml_file(file_path)
            stars_data.append(star_data)

    # Сохраняем в JSON
    with open("stars.json", "w", encoding="utf-8") as f:
        json.dump(stars_data, f, ensure_ascii=False, indent=2)

    # Сортировка по радиусу
    sorted_by_radius = sorted(stars_data, key=lambda x: x["radius"])
    with open("stars_sorted_by_radius.json", "w", encoding="utf-8") as f:
        json.dump(sorted_by_radius, f, ensure_ascii=False, indent=2)

    # Фильтрация по созвездию "Лев"
    leo_stars = [star for star in stars_data if star["constellation"].strip() == "Лев"]
    with open("leo_stars.json", "w", encoding="utf-8") as f:
        json.dump(leo_stars, f, ensure_ascii=False, indent=2)

    # Статистика по радиусу
    radii = [star["radius"] for star in stars_data]
    radius_stats = {
        "min": min(radii),
        "max": max(radii),
        "mean": statistics.mean(radii),
        "median": statistics.median(radii),
        "sum": sum(radii),
    }
    with open("radius_stats.json", "w", encoding="utf-8") as f:
        json.dump(radius_stats, f, ensure_ascii=False, indent=2)

    # Частота созвездий
    constellation_freq = Counter(star["constellation"] for star in stars_data)
    with open("constellation_frequency.json", "w", encoding="utf-8") as f:
        json.dump(dict(constellation_freq), f, ensure_ascii=False, indent=2)

    return {
        "all_data": stars_data,
        "sorted_data": sorted_by_radius,
        "filtered_data": leo_stars,
        "radius_stats": radius_stats,
        "constellation_freq": dict(constellation_freq),
    }


# Путь к директории с XML файлами
directory_path = r"D:\data_lab3\data_tasks\3"
results = process_data(directory_path)

# Вывод результатов
print("Статистика по радиусу:")
print(json.dumps(results["radius_stats"], indent=2))
print("\nЧастота созвездий:")
print(json.dumps(results["constellation_freq"], indent=2))
