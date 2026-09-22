from logging import exception
from warnings import catch_warnings
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import selenium.webdriver.common.keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.common.exceptions import TimeoutException
import string



def find_element_with_retry(driver, by, value, retries=3):
    for attempt in range(retries):
        try:
            return WebDriverWait(driver, 60).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            print(f"Не удалось найти элемент {value}, попытка {attempt+1}")
            driver.refresh()
    raise TimeoutException(f"Элемент {value} не найден после {retries} попыток")

def find_elements_with_retry(driver, by, value, retries=3):
    for attempt in range(retries):
        try:
            return WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            print(f"Не удалось найти элемент {value}, попытка {attempt+1}")
            driver.refresh()
    raise TimeoutException(f"Элемент {value} не найден после {retries} попыток")

def is_limit_exceeded(driver):
    try:
        print("Обработка превышения лимита")
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".button.is-danger"))
        )
        driver.execute_script("arguments[0].click();", button)
        return True
    except TimeoutException:
        print("Не нашел")
        return False

def is_logged_out(driver):
    page_ready = driver.execute_script("return document.readyState") == "complete"
    try:
        print("Обработка вылета")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="user_email_field"]'))
        )
        return True
    except TimeoutException:
        print("Не нашел")
        return False

def target_page(driver, repeat):
    i=0
    while i < repeat:
        button = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/section/div[2]/div/div[5]/div[2]/nav/a[2]')
        button.click()
        i = i + 1
    return i-1
def login(driver, phone_number):
    driver.get("https://idmc.shop.kaspi.kz/api/p/login")
    try:
        phone_tab = find_element_with_retry(driver, By.XPATH, '//*[@id="phone_tab"]')
    except TimeoutException:
        print("Не найдена кнопка телефона")
    driver.execute_script("arguments[0].click();", phone_tab)

    # 4️⃣ Вводим номер телефона (замени на свой селектор)
    try:
        phone_input = find_element_with_retry(driver, By.ID, "user_phone_field")
    except TimeoutException:
        print("Ошибка при вводе телефона")
    phone_input.send_keys(phone_number)  # Ввести номер
    try:
        continue_button = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/main/div/div/div/div[2]/section/section/div/button')
    except TimeoutException:
        print("Ошибка при нажатии кнопки 1")
    driver.execute_script("arguments[0].click();", continue_button)
    # 5 Вводим код
    time.sleep(2)
    try:
        code_input = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/main/div/div/div/div[2]/section/section/div/section/input')
    except TimeoutException:
        print("Не найден текстбокс с кодом")

    otp_code = input("Enter OTP Code: ")
    code_input.send_keys(otp_code)
    try:
        continue_button = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/main/div/div/div/div[2]/section/section/div/button')
    except TimeoutException:
        print("Не найдена кнопка логина")

    driver.execute_script("arguments[0].click();", continue_button)
    old_url = driver.current_url
    try:
        WebDriverWait(driver, 60).until(
            lambda driver: driver.current_url != old_url
        )
    except TimeoutException:
        driver.refresh()
        WebDriverWait(driver, 60).until(
            lambda driver: driver.current_url != old_url
        )


# 1️⃣ Настраиваем браузер
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Открыть на весь экран

# 2️⃣ Запускаем браузер
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

phone_number="7750564581"
login(driver, phone_number)



# 7️⃣ Открываем защищённую страницу
def process(repeat, repeat_global, closed):
    pages = find_elements_with_retry(driver, By.XPATH, '//a[contains(@class, "pagination-link")]')
    last_page=int(pages[4].get_attribute("textContent").strip())
    target_page(driver, repeat[0])
    while repeat[0] < last_page:
        j = 0
        products = find_elements_with_retry(driver, By.XPATH, '//p[contains(@class, "is-5")]/a[@target="blank"]')
        print(len(products))
        while j!=len(products):
            #находим товар
            products = find_elements_with_retry(driver, By.XPATH, '//p[contains(@class, "is-5")]/a[@target="blank"]')
            print(f"{products[j].get_attribute("textContent").strip()}:")
            #находим артикул
            art_block = find_elements_with_retry(driver, By.XPATH, '//p[contains(@class, "is-6")]')
            text_list = art_block[j].text.split("\n")
            for h in range(0, len(art_block)):
                print(f"{h}: {art_block[h].text.split()}\n")
            print(f"Тест: {text_list}\n")
            art=text_list[1]
            print("Артикул: " + art)

            #переходим к товару
            driver.execute_script("arguments[0].click();", products[j])

            #находим нашу цену
            our_price_block = find_element_with_retry(driver,By.XPATH, '//*[@id="app"]/section/div[2]/div/div[1]/div[2]/div[2]/div/div/div[1]/div[2]/div')
            raw_price = our_price_block.get_attribute("textContent").strip()
            our_price = int(raw_price.replace("\xa0", "").replace("₸", "").strip())
            print(f"Наша цена: {our_price}")
            #переходим к товару на каспи
            button = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/section/div[2]/div/div[1]/div[3]/div[2]/div/div[1]/div[2]/div[2]/a')
            driver.execute_script("arguments[0].click();", button)
            tabs = driver.window_handles
            driver.switch_to.window(tabs[-1])

            #Закрываем окно с городом
            if closed[0]==False:
                button = find_element_with_retry(driver, By.XPATH, '//i[contains(@class, "icon icon_close")]')
                driver.execute_script("arguments[0].click();", button)
                closed[0] = True

            #Ищем минимальную цену конкурента
            sellers = find_elements_with_retry(driver, By.XPATH, '//td[contains(@class, "sellers-table__cell")]/a')
            prices = find_elements_with_retry(driver, By.XPATH, '//td[contains(@class, "sellers-table__cell")]/div[contains(@class, "sellers-table__price-cell-text")]')
            i=0
            target_price = 0
            for seller in sellers:
                if(seller.text.strip()!='ТОО "QAZ ЭЛЕКТРО ЭКСПРЕСС"'):
                    raw_price=prices[i].get_attribute("textContent").strip()
                    target_price = int(raw_price.replace("\xa0", "").replace("₸", "").strip())
                    print(f"Конкурент цена: {target_price}")
                    break
                i=i+2;
            print(f"Минимальная цена конкурента: {target_price}")
            #Переходим в кабинет
            driver.close()
            driver.switch_to.window(tabs[0])

            #находим минимальную цен
            index = next((i for i, d in enumerate(dict_list) if d.get("A") == int(art)), -1)
            print(dict_list[index]["B"])
            min_price=int(dict_list[index]["D"])
            print(f"Минимальная цена: {min_price}")

            if(target_price==0):
                min_price=int(min_price*1.08)
                target_price=min_price
                print("Мы единственные в карточке товара")
            elif(target_price<min_price):
                target_price=min_price
                print(f"Цена конкурента ниже чем наша минимальная цена")

            #изменяем цену
            print(f"Итоговая цена: {target_price-1}")
            print(f"Повтор номер: {repeat_global[0]}")
            if(target_price-1!=our_price):
                print(f"Цена изменена")
                button = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/section/div[2]/div/div[1]/div[2]/div[2]/div/button')
                button.click()
                price_input = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/section/div[2]/div/div[3]/div/div[2]/div/section/div[1]/div/div[1]/input')
                price_input.clear()
                price_input.send_keys(target_price-1)
                button = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/section/div[2]/div/div[3]/div/div[2]/div/section/div[1]/div/div[3]/button')
                button.click()
            driver.back()
            j=j+1
            print(f"\nТовар номер {repeat[0]}{j}")
        repeat[0] = repeat[0] + 1
        if(repeat[0]==last_page):
            repeat[0] = 0
            repeat_global[0]=repeat_global[0]+1
            driver.get("https://kaspi.kz/mc/#/products/active/1")
            continue
        button = find_element_with_retry(driver, By.XPATH, '//*[@id="app"]/section/div[2]/div/div[5]/div[2]/nav/a[2]')
        button.click()

repeat=[0]
repeat_global=[1]
closed=[False]
driver.get("https://kaspi.kz/mc/#/products/active/1")
while(True):
    try:
        process(repeat, repeat_global, closed)
    except Exception as e:
        print(f"⚠️ Произошла ошибка: {e}")
        driver.get("https://kaspi.kz/mc/#/products/active/1")
        if is_limit_exceeded(driver):
            time.sleep(300)
        if is_logged_out(driver):
            login(driver, phone_number)

