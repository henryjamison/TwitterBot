import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import random
import requests
import tweepy
# import config

# Authenticate with Twitter API
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def getImage():
    # Start the web driver
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)

        # Load the webpage
        patent_number = random.randint(1000000, 9999999)
        url = f"https://patents.google.com/patent/US{patent_number}/en?oq={patent_number}"
        driver.get(url)

        time.sleep(0.5)

        titleXpath = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/h1'
        title = driver.find_element(By.XPATH, titleXpath)
        time.sleep(0.5)

        ownerXpath = '//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd[2]'
        owner = driver.find_element(By.XPATH, ownerXpath)
        time.sleep(0.5)

        divXpath = '//*[@id="figures"]/div/img[1]'
        driver.find_element(By.XPATH, divXpath).click()
        time.sleep(0.5)

        img_Xpath = '//*[@id="image"]'
        image_element = driver.find_element(By.XPATH, img_Xpath)

        # Get the image URL
        image_url = image_element.get_attribute("src")

        # Download the image
        response = requests.get(image_url)

        body = title.text + "\n Owned By: " + owner.text + "\n" + "Patent Number: " + str(patent_number) + "\n" + url

        # Check if the request was successful
        if response.status_code == 200:
            # Save the image to a file
            filename = f"{patent_number}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
        sendTweet(body,filename)
        driver.quit()
    except NoSuchElementException:
        driver.quit()

def sendTweet(body,filename):
    api.update_status_with_media(body,filename)
    os.remove(filename)
    print("tweeted!")

getImage()

