import time
from random import random

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import base64

try:
    str_to_decode = base64.decodebytes(open("db.json", "rb").read()).decode("utf-8")
    # print(str_to_decode)
    provisory_db = json.loads(str_to_decode)

except FileNotFoundError:
    provisory_db = {}
    open("db.json", "wb").write(base64.encodebytes(json.dumps(provisory_db).encode("utf-8")))


def get_from_db(word):
    # call mysql here
    print(word)
    if word not in provisory_db:
        return ""
    else:
        return provisory_db[word]


def update_db(word, completion):
    # call mysql here
    print(word, completion)
    provisory_db[word] = completion


options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(executable_path=r'/usr/bin/geckodriver', options=options)
driver.profile = webdriver.FirefoxProfile()
driver.profile.set_preference("media.volume_scale", "0.0")
users = open("users.csv", "r").read().splitlines()

for u in users:
    login, password = u.split(":")
    driver.delete_all_cookies()
    driver.get("https://instaling.pl/teacher.php?page=login")
    driver.find_element(By.ID, "log_email").send_keys(login)
    driver.find_element(By.ID, "log_password").send_keys(password)
    print("logging in as", login, "...")
    driver.find_element(By.ID, "log_password").send_keys(Keys.ENTER)
    time.sleep(3)
    try:
        if driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/h4").text == "Dzisiejsza sesja wykonana":
            print("skipping", login, " -> already done today")
            continue
    except Exception as e:
        pass
    driver.get("https://instaling.pl/ling2/html_app/app.php?child_id=" + driver.current_url.split("?student_id=")[1])
    time.sleep(2)
    try:
        # start_session_button
        driver.find_element(By.ID, "start_session_button").click()
    except exceptions.NoSuchElementException and exceptions.ElementNotInteractableException:
        driver.find_element(By.ID, "continue_session_button").click()

    done = driver.find_element(By.ID, "return_mainpage").text == "Powrót na stronę główną"

    while not done:
        word = driver.find_element(By.XPATH, "/html/body/div[1]/div[8]/div[1]/div[2]/div[2]").text
        completion = get_from_db(word)
        driver.find_element(By.ID, "answer").send_keys(completion + Keys.ENTER)
        time.sleep(random() * 2)  # anti susbeing bypass
        status = driver.find_element(By.XPATH, "/html/body/div[1]/div[9]/div[2]/h4/div").text
        completion = driver.find_element(By.ID, "word").text
        if status == "Niepoprawnie":
            update_db(word, completion)
        time.sleep(random() * 2)  # anti susbeing bypass
        driver.find_element(By.ID, "next_word").click()
        done = driver.find_element(By.ID, "return_mainpage").text == "Powrót na stronę główną"

        # while this is not the most optimal solution, it is the most reliable one
        open("db.json", "wb").write(base64.encodebytes(json.dumps(provisory_db).encode("utf-8")))

    print("done, that's all for today folks!")
    # ascii logo
    print("   _         __           __           __")
    print("(____  ___/ /____ _____/ / ___ ___ _/ /_ ")
    print("/ / _ \(_-/ __/ _ `/ __/ _ / -_/ _ `/ __/")
    print("/_/_//_/___\__/\_,_/\__/_//_\__/\_,_/\__/")

driver.close()
