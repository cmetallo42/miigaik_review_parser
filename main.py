import os
import re
import urllib.request

try:
    from termcolor import colored
except ImportError:
    print("Trying to Install required module: termcolor\n")
    os.system("python -m pip install termcolor")
from termcolor import colored

try:
    import html2text
except ImportError:
    print("Trying to Install required module: html2text\n")
    os.system("python -m pip install html2text")
import html2text

tabiturient = "https://tabiturient.ru/vuzu/miigaik"
tabiturient_about = "https://tabiturient.ru/vuzu/miigaik/about"
studika = "https://studika.ru/moskva/miigaik/otzyvi"

marks = "\n"
ratings = []
good_reviews = []
bad_reviews = []
neutral_reviews = []
s_start_stars = 0

marks_str = [
    ["Состояние и оснащение корпусов вуза: "],
    ["Удобство расположения корпусов вуза: "],
    ["Качество образования: "],
    ["Качество работы административного аппарата: "],
    ["Дополнительные активности в вузе: "],
    ["Качество общепита: "],
]
start_of_rating_str = '<table class="circustext" cellpadding="0" cellspacing="0">'
end_of_rating_str = "</td>"
good_request_str = '<div class="p20 request1">'
bad_request_str = '<div class="p20 request2">'
neutral_request_str = '<div class="p20 request3">'
start_of_review = '<div style="text-align:justify;" class="font2">'
s_start_stars_str = '<div class="review-stars"'
s_start_review_str = '<div class="text-read mt-2" itemprop="reviewBody">'
end_div = "</div>"
pagination_str = '<li class="page-item" data-page'


# Получение страниц
def get_page(url):
    hdr = {}
    hdr[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    req = urllib.request.Request(url, headers=hdr)
    page = urllib.request.urlopen(req).read().decode("utf8")
    return page


print("Getting reviews...wait a few seconds...")
tabiturient_page = get_page(tabiturient)
tabiturient_about_page = get_page(tabiturient_about)
studika_page = get_page(studika)

# Смотрим сколько страниц на сайте
pages_count = studika_page.count(pagination_str)
if pages_count > 1:
    i = 2
    while i <= pages_count:
        studika_page += get_page(studika + "?page=" + str(i))
        i += 1


# Ищем положительные, отрицательные и нейтральные отзывы на studika.ru
def s_page_parser(s_page, s_end_review=0):
    while True:
        s_start_stars = s_page.find(s_start_stars_str, s_end_review)
        if s_start_stars == -1:
            break
        s_end_stars = s_page.find(end_div, s_start_stars)
        stars_count = s_page[s_start_stars:s_end_stars].count("fill")
        s_start_review = s_page.find(s_start_review_str, s_end_stars)
        s_end_review = s_page.find(end_div, s_start_review)
        h = html2text.HTML2Text()
        h.ignore_links = True
        if stars_count < 3:
            bad_reviews.append(h.handle(s_page[s_start_review:s_end_review]))
        elif stars_count > 3:
            good_reviews.append(h.handle(s_page[s_start_review:s_end_review]))
        else:
            neutral_reviews.append(h.handle(s_page[s_start_review:s_end_review]))


# Ищем отзывы на tabiturient.ru
def page_parser(page, request_str, start_request=0, end=0):
    while start_request != -1:
        start_request = page.find(request_str, end)
        if start_request == -1:
            break
        start = page.find(start_of_review, start_request)
        end = page.find(end_div, start)
        review = page[start:end]
        h = html2text.HTML2Text()
        h.ignore_links = True
        if request_str.find("request1") != -1:
            good_reviews.append(h.handle(review))
        if request_str.find("request2") != -1:
            bad_reviews.append(h.handle(review))
        if request_str.find("request3") != -1:
            neutral_reviews.append(h.handle(review))


# Парсим страницу about
def page_about_parser(page_about, start=0, i=0):
    while start != -1:
        start = page_about.find(start_of_rating_str, i)
        if start == -1:
            break
        end = page_about.find(end_of_rating_str, start)
        i = end
        rating = page_about[start:end]
        h = html2text.HTML2Text()
        h.ignore_links = True
        ratings.append(re.findall(r"\d*\.\d+|\d+", h.handle(rating)))
    ratings.pop(4)
    ratings.pop(4)


# Принт статистики
def print_stats():
    print("Статистика:\n", marks)
    print(colored("Good reviews:", "green"), colored(len(good_reviews), "green"))
    print(colored("Bad reviews:", "red"), colored(len(bad_reviews), "red"))
    print(
        colored("Neutral reviews:", "yellow"), colored(len(neutral_reviews), "yellow")
    )
    print("---------------")
    total_reviews = len(good_reviews) + len(bad_reviews) + len(neutral_reviews)
    print(colored("Total reviews:", "red"), colored(total_reviews, "red"))


# Вызов парсеров
page_parser(tabiturient_page, good_request_str)
page_parser(tabiturient_page, bad_request_str)
page_parser(tabiturient_page, neutral_request_str)
page_about_parser(tabiturient_about_page)
s_page_parser(studika_page)


# Складываем строки с оценками для удобства
k = 0
for j in marks_str:
    marks += marks.join(j) + marks.join(ratings[k]) + "/10" + "\n"
    k += 1

os.system("clear")
value = 0

# Цикл для консольного меню
while True:
    value = input(
        "\nХорошие отзывы: 1\nПлохие отзывы: 2\nНейтральные отзывы: 3\nСтатистика: 4\nВыйти: 5\n"
    )
    os.system("clear")
    try:
        value = int(value)
    except ValueError:
        os.system("clear")
        print("Введите число от 1 до 5")
        continue
    if value == 1:
        print("Хорошие отзывы:\n", *good_reviews, sep="\n")
    if value == 2:
        print("Плохие отзывы:\n", *bad_reviews, sep="\n")
    if value == 3:
        print("Нейтральные отзывы:\n", *neutral_reviews, sep="\n")
    if value == 4:
        print_stats()
    if value == 5:
        exit()
