import time
from random import random

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import base64

try:
    provisory_db = json.loads(str(base64.decodebytes(bytes(open("db.json", "r").read().encode("unicode_escape")).base64decode())))
except Exception:
    provisory_db = {}
    open("db.json", "w").write(str(base64.encodebytes(bytes(json.dumps(provisory_db).encode("unicode_escape")))))


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


driver = webdriver.Firefox(executable_path=r'/usr/bin/geckodriver')
users = open("users.csv", "r").read().splitlines()

for u in users:
    login, password = u.split(":")
    driver.delete_all_cookies()
    driver.get("https://instaling.pl/teacher.php?page=login")
    driver.find_element(By.ID, "log_email").send_keys(login)
    driver.find_element(By.ID, "log_password").send_keys(password)
    driver.find_element(By.ID, "log_password").send_keys(Keys.ENTER)
    time.sleep(3)
    driver.get("https://instaling.pl/ling2/html_app/app.php?child_id=" + driver.current_url.split("?student_id=")[1])
    driver.implicitly_wait(1)
    try:
        # start_session_button
        driver.find_element(By.ID, "start_session_button").click()
    except exceptions.NoSuchElementException and exceptions.ElementNotInteractableException:
        driver.find_element(By.ID, "continue_session_button").click()
    done = driver.find_element(By.ID, "return_mainpage").text == "Powrót na stronę główną"
    while done == False:
        word = driver.find_element(By.XPATH, "/html/body/div[1]/div[8]/div[1]/div[2]/div[2]").text
        completion = get_from_db(word)
        driver.find_element(By.ID, "answer").send_keys(completion)
        driver.find_element(By.ID, "answer").send_keys(Keys.ENTER)
        time.sleep(random()*2)  # anti susbeing bypass
        status = driver.find_element(By.XPATH, "/html/body/div[1]/div[9]/div[2]/h4/div").text
        completion = driver.find_element(By.ID, "word").text
        if status == "Niepoprawnie":
            update_db(word, completion)
        time.sleep(random()*2)  # anti susbeing bypass
        driver.find_element(By.ID, "next_word").click()
        done = driver.find_element(By.ID, "return_mainpage").text == "Powrót na stronę główną"

        # while this is not the most optimal solution, it is the most reliable one
        open("db.json", "w").write(str(base64.encodebytes(bytes(json.dumps(provisory_db).encode("unicode_escape")))))

    print("done")
driver.close()
