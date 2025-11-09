import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import get_book_data, scrape_books
book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'

def test_get_book_data_returns_dict():
    """Тест: функция возвращает словарь"""
    result = get_book_data(book_url)
    assert isinstance(result, dict), "Функция get_book_data возвращает не словарь"

def test_get_book_data_contains_required_keys():
    """Тест: словарь содержит обязательные ключи"""
    result = get_book_data(book_url)
    required_keys = ['Title', 'Rating', 'Description', 'UPC', 'Availability']
    for key in required_keys:
        assert key in result, "Возвращаемый словарь из get_book_data не содержит обязательные ключи"

def test_get_book_data_has_correct_title():
    """Тест: название книги корректно"""
    result = get_book_data(book_url)
    assert result['Title'] == 'A Light in the Attic', "Функция get_book_data возвращает некорректное название"

def test_availability_is_integer():
    """Тест: количество в наличии является целым числом"""
    result = get_book_data(book_url)
    assert isinstance(result['Availability'], int), "Функция get_book_data возвращает количество книг в наличии, которое не является целым числом"

def test_scrape_books_returns_list():
    """Тест: функция scrape_books возвращает список"""
    result = scrape_books(is_save=False)
    assert isinstance(result, list), "Функция scrape_books возвращает не список"
