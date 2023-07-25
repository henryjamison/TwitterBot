import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import random
import requests
import tweepy

# Authenticate with Twitter API
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)
# client = tweepy.Client(consumer_key=CONSUMER_KEY,consumer_secret=CONSUMER_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_TOKEN_SECRET)

def getImage():
    # Start the web driver
    try:
        # chrome_service = webdriver.ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("detach", True)
        # version = '114.0.5735.90'
        version = '114.0.5735.16'
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version=version).install()), options=options)
        # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=version).install()), options=options)
        # driver = webdriver.ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())


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

        body = title.text + "\nOwned By: " + owner.text + "\n" + "Patent Number: " + str(patent_number) + "\n" + url

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
        print("No picture found, searching again.")
        getImage()

def sendTweet(body,filename):
    # api.media_upload(filename=filename)
    # media = api.update_status_with_media(status='media upload', filename=filename)
    # client.create_tweet(text=body, media_ids=media)
    api.update_status_with_media(body,filename)
    os.remove(filename)
    print("tweeted!")
    

getImage()

