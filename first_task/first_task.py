import os
import json
from bs4 import BeautifulSoup
import statistics
from collections import Counter


def clean_text(text):
    """Очищает текст от лишних пробелов и переносов строк"""
    return " ".join(text.split())


def parse_html_files(directory):
    data = []

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    print(f"Обработка файла: {filename}")
                    soup = BeautifulSoup(file.read(), "html.parser")

                    item = {}

                    # Парсим тип
                    type_span = soup.select_one('div > span:contains("Тип:")')
                    if type_span:
                        item["Тип"] = clean_text(type_span.text.replace("Тип:", ""))

                    # Парсим название турнира
                    title = soup.select_one("h1.title")
                    if title:
                        tournament_name = clean_text(title.text.replace("Турнир:", ""))
                        item["Турнир"] = tournament_name

                    # Парсим город и дату начала
                    address = soup.select_one("p.address-p")
                    if address:
                        address_text = clean_text(address.text)
                        if "Город:" in address_text and "Начало:" in address_text:
                            city = address_text.split("Город:")[1].split("Начало:")[0]
                            date = address_text.split("Начало:")[1]
                            item["Город"] = clean_text(city)
                            item["Дата начала"] = clean_text(date)

                    # Парсим информацию о турах и контроле времени
                    count_span = soup.select_one("span.count")
                    if count_span:
                        tours = count_span.text.replace("Количество туров:", "")
                        item["Количество туров"] = int(clean_text(tours))

                    time_span = soup.select_one("span.year")
                    if time_span:
                        time = time_span.text.replace("Контроль времени:", "").replace(
                            "мин", ""
                        )
                        item["Контроль времени"] = int(clean_text(time))

                    # Парсим минимальный рейтинг
                    min_rating_span = soup.select_one(
                        'span:contains("Минимальный рейтинг")'
                    )
                    if min_rating_span:
                        rating = min_rating_span.text.replace(
                            "Минимальный рейтинг для участия:", ""
                        )
                        item["Минимальный рейтинг"] = int(clean_text(rating))

                    # Парсим рейтинг и просмотры
                    for span in soup.select("div:last-child span"):
                        text = span.text
                        if "Рейтинг:" in text:
                            rating = text.replace("Рейтинг:", "")
                            item["Рейтинг"] = float(clean_text(rating))
                        elif "Просмотры:" in text:
                            views = text.replace("Просмотры:", "")
                            item["Просмотры"] = int(clean_text(views))

                    if item:
                        data.append(item)
                        print(f"Успешно обработан файл: {filename}")

            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {str(e)}")

    return data


def process_data(data):
    if not data:
        print("Нет данных для обработки")
        return

    # Записываем исходные данные
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Исходные данные сохранены в output.json")

    # Сортировка по количеству просмотров
    sorted_data = sorted(data, key=lambda x: x.get("Просмотры", 0), reverse=True)
    with open("sorted_by_views.json", "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    print("Отсортированные по просмотрам данные сохранены в sorted_by_views.json")

    # Фильтрация турниров с рейтингом выше 3.0
    filtered_data = [item for item in data if item.get("Рейтинг", 0) > 3.0]
    with open("filtered_by_rating.json", "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    print("Отфильтрованные по рейтингу данные сохранены в filtered_by_rating.json")

    # Статистика по числовым полям
    numeric_stats = {}
    for field in [
        "Количество туров",
        "Контроль времени",
        "Минимальный рейтинг",
        "Рейтинг",
        "Просмотры",
    ]:
        values = [item[field] for item in data if field in item]
        if values:
            numeric_stats[field] = {
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
            }

    # Частота городов
    cities = Counter(item["Город"] for item in data if "Город" in item)

    stats = {
        "numeric_stats": numeric_stats,
        "city_frequency": dict(cities.most_common()),
    }

    with open("statistics.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print("Статистика сохранена в statistics.json")


def main():
    data_dir = r"D:\data_lab3\data_tasks\1"

    if not os.path.exists(data_dir):
        print(f"Директория не найдена: {data_dir}")
        return

    data = parse_html_files(data_dir)
    if data:
        process_data(data)
        print("\nОбработка данных завершена успешно.")
    else:
        print("Данные не найдены или произошла ошибка при парсинге.")


if __name__ == "__main__":
    main()
