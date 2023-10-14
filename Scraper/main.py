import os
from functools import partial

from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import json
import csv

def mainScraper():
    urls = []
    for item in range(1, 801):
        url = f"https://lifehacker.ru/topics/technology/?page={item}"
        urls.append(url)
    amount = 0
    partial_getData = partial(getData, amount=amount)
    with Pool(10) as p:
        p.map(partial_getData, urls)



def getData(url, amount):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    mainURL = url
    req = requests.get(url, headers)
    src = req.text

    # with open("index.html", "w") as file:
    #     file.write(src)
    # with open("index.html") as file:
    #     src = file.read()

    soup = BeautifulSoup(src, "lxml")
    allArticles = soup.find_all("div", class_="article-card__small-wrapper")

    articlesURL = [] # urls of articles
    articleMainArray = []  # main array of the saved articles
    count = 1

    for article in allArticles:
        currentArticleURL = article.find("a", class_="lh-small-article-card__link").get("href")
        articleURL = "https://lifehacker.ru" + currentArticleURL
        articlesURL.append(articleURL)

    for url in articlesURL:
        print(f"Progress: {amount} of 800")
        #print(f"the article #{count} has been scrapped")
        req = requests.get(url, headers)
        src = req.text
        soup = BeautifulSoup(src, "lxml")

        # Get article's title
        try:
            articleTitle = soup.find("h1", class_="article-card__title").text
        except Exception:
            articleTitle = None

        # Get article's description
        try:
            articleDescription = soup.find("div", class_="article-card__subtitle").text
        except Exception:
            articleDescription = None

        # Get article's author
        try:
            articleAuthor = soup.find("a", class_="author__name").text
        except Exception:
            articleAuthor = None

        # Get article's date
        try:
            articleDate = soup.find("span", class_="article-card-header__elem article-card-header__elem--date")\
                .text.strip()
        except Exception:
            articleDate = None

        # Get article's topic
        try:
            articleTopic = soup.find("a", class_="article-card-header__elem article-card-header__elem--link")\
                .text.strip()
        except Exception:
            articleTopic = None

        # Get article's text
        articleMain = soup.\
            find("div", class_="single-article__post-content single-article__content-container").find_all("p")


        articleTextArray = ""
        for x in articleMain:
            articleTextArray += f"{x.text} "

        # Add all info of the article to the array
        articleMainArray.append(
            {
                "Title": articleTitle,
                "Description": articleDescription,
                "Author": articleAuthor,
                "Date": articleDate,
                "Topic": articleTopic,
                "Text": articleTextArray
            }
        )
        count += 1
        amount += 1
    projectName = mainURL.split("/")[-1].split("=")[-1]
    with open(f"data/page_{projectName}.json", "a", encoding="utf-8") as file:
        json.dump(articleMainArray, file, indent=4, ensure_ascii=False)



def merge():
    folder_path = 'data'

    data_list = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                data_list.extend(data)

    output_json_path = 'main.json'
    with open(output_json_path, 'w', encoding='utf-8') as output_file:
        json.dump(data_list, output_file, ensure_ascii=False, indent=4)

    print(f'Данные объединены и сохранены в файл {output_json_path}')


def main():
    #merge()
    mainScraper()

if __name__ == "__main__":
    main()
