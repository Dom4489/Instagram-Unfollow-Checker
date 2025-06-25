from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time 
import os
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
import json

load_dotenv()
username = os.getenv('user')
password = os.getenv('pass')
count = 0
maxScroll = int(input("how many followers do you have? \n"))
maxScroll /= 20
maxScroll *= 4 

def login(browser):
    WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.NAME, "username")))
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password) 
    browser.find_element(By.NAME, "password").send_keys(u'\ue007')

def clickButtonWithCSS(browser, css_selector):
    element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
    )
    element.click()

def navigateToFollowers(driver):
    linkCSS = "[href*=\"" + username + "\"]"
    clickButtonWithCSS(driver, linkCSS)

def scrollDown(browser):
    time.sleep(2)
    fBody  = browser.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]")
    scroll = 0
    while scroll < maxScroll: # change and make this an input
        browser.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
        time.sleep(1)
        scroll += 1
    return

def getUsers(browser):
    listXPath1 = "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]"
    WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.XPATH, listXPath1)))
    scrollDown(browser)
    time.sleep(1)
    username_elements = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, ".//span[contains(@class, '_aaco') and contains(@class, '_aad7') and contains(@class, '_ap3a') and contains(@class, '_aacw') and contains(@class, '_aacx') and contains(@class, '_aade')]")
        )
    )
    usernames = [el.text.strip() for el in username_elements if el.text.strip()]
    return usernames 

def findDoNotFollow(followers, following):
    followers.sort()
    following.sort()
    notFollowing = []
    for i in range(len(following)):
        try:
            followers.index(following[i])
        except ValueError:
            notFollowing += [following[i]]
    return notFollowing

def findDoNotFollowBack(followers, following):
    followers.sort()
    following.sort()
    notFollowingBack = []
    for i in range(len(followers)):
        try:
            following.index(followers[i])
        except ValueError:
            notFollowingBack += [followers[i]]
    return notFollowingBack

def findRemoved(saved, followers):
    saved.sort()
    followers.sort()
    removed = []
    for i in range(len(saved)):
        try:
            followers.index(saved[i])
        except ValueError:
            removed += [saved[i]]
    return removed

def loadListFromFile(filename='saved_list.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No saved list found at {filename}")
        return None

def saveListToFile(data, filename='saved_list.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)
    print(f"List saved to {filename}")

def deleteListFromFile(filename='saved_list.json'):
    if os.path.exists(filename):
        os.remove(filename)
        print(f"List deleted from {filename}")
    else:
        print(f"No saved list found at {filename}")
    

def main():
    browser = webdriver.Chrome()
    browser.get('https://www.instagram.com/?flo=true')
    time.sleep(1)
    login(browser)
    navigateToFollowers(browser)
    print("Hello")
    time.sleep(1)
    followersCSS = "[href*=\"" + username + "/followers/\"]"
    cssSelectClose = '[aria-label="Close"]'
    followingCSS = "[href*=\"" + username + "/following/\"]"
    clickButtonWithCSS(browser, followersCSS)
    followersList = getUsers(browser)
    clickButtonWithCSS(browser, cssSelectClose)
    time.sleep(1)
    clickButtonWithCSS(browser, followingCSS)
    followingList = getUsers(browser)
    savedList = loadListFromFile()
    if (savedList is None):
        print("no previous list was found could not check for users who have removed you or deactivated their account")
    elif savedList == followersList:
        print("no users have removed you or deactivated their account")
    else:
        removedList = findRemoved(savedList, followersList)
        if removedList:
            print("These users have removed you or have deactivated their account \n")
            for i in range(len(removedList)):
                print(removedList[i] + "\n")
    doNotFollowList = findDoNotFollow(followersList, followingList)
    print("These users do not follow you back \n")
    for i in range(len(doNotFollowList)):
        print(doNotFollowList[i] + "\n")
    doNotFollowBackList = findDoNotFollowBack(followersList, followingList)
    print("You do not follow these users back: \n")
    for i in range(len(doNotFollowBackList)):
        print(doNotFollowBackList[i] + "\n")
    deleteListFromFile()
    saveListToFile(followersList)
    browser.quit()

if __name__ == "__main__":
    main()