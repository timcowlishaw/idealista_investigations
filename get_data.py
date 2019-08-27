import bs4
import seleniumrequests
import csv
import time
import random
import json
from urllib.parse import urljoin
from selenium import webdriver
import keyboard
from pathlib import Path
browser = webdriver.Chrome()


with open("data/leaf_locations.json") as f:
    districts = json.load(f)

district_urls = {
    "raval": "https://www.idealista.com/alquiler-viviendas/barcelona/ciutat-vella/el-raval/",
    "gracia": "https://www.idealista.com/alquiler-viviendas/barcelona/gracia/",
    "sants": "https://www.idealista.com/alquiler-viviendas/barcelona/sants-montjuic/"
}

def time_limited_request(url):
    browser.get(url)
    time.sleep(3 + random.random()  * 3)
    if "Vaya! parece que estamos recibiendo muchas peticiones tuyas en poco" in browser.page_source:
        print("Solve the CAPTCHA then press space to continue.")
        keyboard.wait('space')
        browser.get(url)
        time.sleep(3 + random.random()  * 3)
    html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    return html

def get_listings(url, writer):
    print("X")
    response = time_limited_request(url)
    soup = bs4.BeautifulSoup(response)
    items = soup.find_all("article", class_="item")
    for item in items:
        title_elem = item.find(class_="item-link")
        title = title_elem.text
        href = title_elem["href"]
        price = item.find(class_="item-price").text
        details = ",".join([d.text for d in item.find_all(class_="item-detail")])
        description = item.find(class_="item-description").text
        print(".")
        writer.writerow([title, href, price, details, description])
    nxt = soup.find("li", class_="next")
    if nxt:
        link = nxt.find("a")
        get_listings(urljoin(url,link["href"]), writer)

for (district, url) in district_urls.items():
    #url = "https://idealista.com/%s" % data["href"]
    path = Path("data/%s.csv" % district)
    if not path.is_file():
        with open("data/%s.csv" % district, "w") as file:
            print(district)
            writer = csv.writer(file)
            get_listings(url, writer) 
