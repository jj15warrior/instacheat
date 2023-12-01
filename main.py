import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
s = {}

def update_slavs(to_translate, translation):
    global s
    if to_translate in s:
        if translation not in s[to_translate]:
            s[to_translate].append(translation)
    else:
        s[to_translate] = [translation]

def slavnik(winp):
    global s
    try:
        return s[winp]
    except KeyError:
        return ""

expected_execution_time = 2*60 # 5s to avoid detection
pairs_pre = open("users.csv").read().split("\n")
pairs = []
for i in range(len(pairs_pre)):
    tmp = pairs_pre[i].split(":")
    if tmp[0] != ['']:
        pairs.append((tmp[0], tmp[1]))

fo = webdriver.firefox.options.Options()
fo.add_argument("--disable-extensions")
fo.add_argument("--disable-gpu")
fo.add_argument("--headless")
driver = webdriver.Firefox(fo)


for (username,password) in pairs:
    try:
        driver.get("https://instaling.pl/teacher.php?page=login")
    except:
        driver.quit()
        driver = webdriver.Firefox(fo)
        driver.get("https://instaling.pl/teacher.php?page=login")
    driver.find_element(By.ID, "log_email").send_keys(username)
    driver.find_element(By.ID, "log_password").send_keys(password)
    driver.find_element(By.ID, "log_password").send_keys(Keys.ENTER)
    student_id = driver.current_url.split("=")[-1]
    while student_id == "login":
        driver.implicitly_wait(100)
        student_id = driver.current_url.split("=")[-1]
    print(student_id)
    print(username)
    driver.get("https://instaling.pl/ling2/html_app/app.php?child_id=" + student_id)
    try:
        driver.find_element(By.ID, "start_session_button").click()
    except Exception as e:
        print("continuing an already started session")
        driver.find_element(By.ID, "continue_session_button").click()
    driver.implicitly_wait(expected_execution_time*1000)
    while True:
        to_translate = driver.find_element(By.CLASS_NAME, "translations").text
        try:
            driver.find_element(By.ID, "answer").send_keys(slavnik(to_translate))
        except selenium.common.exceptions.ElementNotInteractableException:
            print("finished")
            try:
                driver.find_element(By.ID, "return_mainpage").click()
            except:
                driver.implicitly_wait(10000)
            driver.get("https://instaling.pl/teacher2/logout.php")
            break
        driver.find_element(By.ID, "check").click()
        driver.implicitly_wait(200)
        translation = ""
        retry = True
        while retry:
            try:
                translation = driver.find_element(By.ID, "word").text
                retry = False
            except selenium.common.exceptions.ElementNotInteractableException:
                driver.implicitly_wait(200)
        update_slavs(to_translate, translation)
        print(translation, slavnik(to_translate))
        retry = True
        while retry:
            try:
                driver.find_element(By.ID, "next_word").click()
                retry = False
            except selenium.common.exceptions.ElementNotInteractableException:
                driver.implicitly_wait(200)
print("done4all")
