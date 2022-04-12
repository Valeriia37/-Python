#  Написать программу, которая собирает товары «В тренде» с сайта техники mvideo и складывает
#  данные в БД. Сайт можно выбрать и свой. Главный критерий выбора: динамически загружаемые товары
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pprint import pprint


def write_to_database(product):
    '''
    Записывает словарь о товарах в базу данных
    :param product: словарь
    '''
    client = MongoClient('127.0.0.1', 27017)
    db = client['product_db']
    product_data = db.product
    if product_data.find_one({'link': product['link']}):
        print(f'Duplicated product {product["link"]}')
    else:
        product_data.insert_one(product)
        print(f'Success insert the link {product["link"]}')


s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

driver.get('https://www.mvideo.ru/')
driver.execute_script("window.scrollTo(0, 1700)")

wait = WebDriverWait(driver, 15)
button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='mvid-carousel-inner']/button[2]")))
button.click()
elems = driver.find_elements(By.XPATH, "//mvid-product-cards-group/*")

product_list = []
product_data = {}
for elem in elems:
    if elem.get_attribute('class') == 'product-mini-card__name ng-star-inserted':
        product_data['product_name'] = elem.find_element(By.XPATH, './div/a/div').text
        product_data['link'] = elem.find_element(By.XPATH, './/a').get_attribute('href')
    if elem.get_attribute('class') == 'product-mini-card__price ng-star-inserted':
        price = elem.find_element(By.XPATH, ".//span[@class='price__main-value']").text
        price = float(price[:-1].replace(' ', ''))
        product_data['price'] = price
    if elem.get_attribute('class') == 'product-mini-card__bonus-rubles ng-star-inserted':
        bonus = elem.find_element(By.XPATH, './/span[@class="mbonus-block__value"]').text
        if len(bonus.split()) == 2:
            product_data['bonus_rubles'] = int(bonus.split()[1])
        else:
            product_data['bonus_rubles'] = int(bonus.rstrip('+'))
    if elem.get_attribute('class') == 'product-mini-card__controls buttons ng-star-inserted':
        write_to_database(product_data)
        product_list.append(product_data)
        product_data = {}

pprint(product_list)
print(len(product_list))