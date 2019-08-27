import bs4
import seleniumrequests
import csv
import time
import random
import json
from urllib.parse import urljoin
from selenium import webdriver
from pathlib import Path
from datetime import datetime
browser = webdriver.Chrome()

LOGIN_URL="https://www.idealista.com/login"
SEARCH_URL="https://www.idealista.com/usuario/tus-alertas"
EMAIL="tim@timcowlishaw.co.uk"
PASSWORD="9Xw6pk1C9Z2uc7sFh8rY"

def time_limited_request(url):
    browser.get(url)
    time.sleep(3 + random.random()  * 3)
    if "Vaya! parece que estamos recibiendo muchas peticiones tuyas en poco" in browser.page_source:
        input("Solve the CAPTCHA then press any key to continue.")
        browser.get(url)
        time.sleep(3 + random.random()  * 3)
    html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    return html

def login():
    browser.get(LOGIN_URL)
    email_field = browser.find_element_by_id("email")
    password_field = browser.find_element_by_class_name("js-password-field")
    email_field.send_keys(EMAIL)
    password_field.send_keys(PASSWORD)
    time.sleep(3 + random.random()  * 3)
    browser.find_element_by_id("doLogin").click()
    time.sleep(3 + random.random() * 3)
    


def get_searches():
    response = time_limited_request(SEARCH_URL)
    soup = bs4.BeautifulSoup(response, features='html.parser')
    search_elems = soup.select("#searches tbody tr")
    searches = {}
    for elem in search_elems:
        searches[elem["data-searchname"]] = urljoin(SEARCH_URL, elem["data-searchurl"])
    return searches



def get_listings(url, writer):
    print("X",end="")
    response = time_limited_request(url)
    soup = bs4.BeautifulSoup(response, features='html.parser')
    items = soup.find_all("article", class_="item")
    for item in items:
        title_elem = item.find(class_="item-link")
        title = title_elem.text
        href = title_elem["href"]
        price = item.find(class_="item-price").text
        details = ",".join([d.text for d in item.find_all(class_="item-detail")])
        description = item.find(class_="item-description").text
        print(".",end="")
        writer.writerow([title, href, price, details, description])
    print("")
    nxt = soup.find("li", class_="next")
    if nxt:
        link = nxt.find("a")
        get_listings(urljoin(url,link["href"]), writer)

login()
searches = get_searches()
with open("data/searches.json", "w") as f:
    json.dump(searches, f)

date = datetime.now().strftime("%Y-%m-%d")

for (search, url) in searches.items():
    Path("data/searches/%s" % search).mkdir(parents=True, exist_ok=True)
    path = Path("data/searches/%s/%s.csv" % (search, date))
    if not path.is_file():
        with open("data/searches/%s/%s.csv" % (search, date), "w") as file:
            print(search)
            writer = csv.writer(file)
            get_listings(url, writer) 
