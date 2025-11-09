import time
import requests
import schedule
from bs4 import BeautifulSoup
import re
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_book_data(book_url: str) -> dict:
    """
    Парсит данные о книге с указанной страницы.
    
    Args:
        book_url: URL страницы книги
        
    Returns:
        Словарь с информацией о книге (название, рейтинг, описание, цена и т.д.)
    """
    
    response = requests.get(book_url)     
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    else:
        raise Exception(f"Request failed with status code: {response.status_code}")
    book_data = {}
    book_data["Title"] = soup.find("h1").text
    
    rating_dic = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    rating_tag = soup.find("p", class_="star-rating")
    book_data["Rating"] = rating_dic[rating_tag["class"][1]]
    
    description_tag = soup.find("div", id="product_description")
    book_data["Description"] = description_tag.find_next_sibling("p").text.strip() if description_tag else "No description"
    
    book_table = soup.find("table", class_ = "table table-striped")
    for position in book_table.find_all("tr"):
        key = position.find("th").text
        value = position.find("td").text
        book_data[key] = value
        if key == "Availability":
            numbers = re.findall(r'\d+', value)
            book_data["Availability"] = int(numbers[0]) if numbers else 0
        if  key == "Number of reviews":
            book_data["Number of reviews"] = int(value) 
        if key == "Price (excl. tax)":
            book_data["Price (excl. tax)"] = float(value[1:])
        if key == "Price (incl. tax)":
            book_data["Price (incl. tax)"] = float(value[1:])
        if key == "Tax":
            book_data["Tax"] = float(value[1:])
            book_data["Currency"] = value[0]
    return book_data

def scrape_books(is_save = False) -> list:
    """
    Собирает данные обо всех книгах с сайта books.toscrape.com.
    
    Args:
        is_save: Если True, сохраняет результаты в books_data.txt в папку artifacts
        
    Returns:
        Список словарей с данными книг
    """

    base_url = "http://books.toscrape.com/catalogue/"
    all_books_data = []
    page_number = 1
    max_retries = 3
    
    while True:
        page_url = f"{base_url}page-{page_number}.html"
        response = requests.get(page_url)
        if response.status_code != 200:
            break
            
        soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
        books = soup.find_all("article", class_="product_pod")
            
        for book in books:
            book_link = book.find("h3").find("a")["href"]
            full_book_url = f"{base_url}{book_link}"
            retry_delay = 2
            for attempt in range(max_retries + 1):
                try:
                    book_data = get_book_data(full_book_url)
                    all_books_data.append(book_data)
                    break
                except Exception as e:
                    if attempt < max_retries:
                        delay = retry_delay * (2 ** attempt)
                        time.sleep(delay)
            time.sleep(0.5)
            
        next_button = soup.find("li", class_="next")
        if not next_button:
            break  
            
        page_number += 1
        time.sleep(1)
    if is_save and all_books_data:
        with open("artifacts/books_data.txt", "w", encoding="utf-8") as f:
            json.dump(all_books_data, f, ensure_ascii=False, indent=2)
    
    return all_books_data

if __name__ == "__main__":
    def scheduled_parsing():
        """
        Запускает парсинг по расписанию в 19:00 с сохранением результатов.
        Используется планировщиком schedule.
        """
        print(f"[{time.strftime('%H:%M:%S')}] Запуск парсинга по расписанию")
        scrape_books(is_save=True)

    schedule.clear()
    schedule.every().day.at("19:00").do(scheduled_parsing)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Планировщик остановлен")