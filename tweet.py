import os
import random
import requests
import tweepy
from bs4 import BeautifulSoup
import urllib.request



# Authenticate with Twitter API
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
BEARER_TOKEN = os.environ["BEARER_TOKEN"]

auth_v1 = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth_v1)

auth_v2 = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

def start():
    patent_number = random.randint(1000000, 9999999)
    url = f"https://patents.google.com/patent/US{patent_number}/en?oq={patent_number}"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features='lxml')
    meta = soup.find_all('meta',itemprop='full')
    ####### start()[0], runner()[1], etc..
    return patent_number, url, req, soup, meta


def get_body(soup, num, url):
    title = soup.title.text
    parsed_title = title.split(' - ')[1].strip()
    owner = soup.find('meta',scheme='assignee')['content']
    if (owner == 'Individual'):
        owner = soup.find('meta',scheme='inventor')['content']
        body = parsed_title + "\nInvented By: " + owner + "\n" + "Patent Number: US" + str(num) + "\n" + url
    else:
        body = parsed_title + "\nOwned By: " + owner + "\n" + "Patent Number: US" + str(num) + "\n" + url
    return body
    

def trim_url_list(meta):
    img_list = []
    for img in meta:    
        i = img['content']
        img_list.append(i)
    if img_list == []:
        print("no pics found")
        runner()
        return
    return img_list[:4]

def download_imgs(img_list):
    index = 0
    file_list = []
    for img in img_list:
        filename = f"{index}.jpg"
        urllib.request.urlretrieve(img, filename)
        file_list.append(filename)
        index+=1
    return file_list

def split_abstract(abstract, limit=280):
    tweet_parts = []
    current_part = ""
    words = abstract.split()
    for word in words:
        if len(current_part) + len(word) + 1 <= limit:
            current_part += word + " "
        else:
            tweet_parts.append(current_part.strip())
            current_part = word + " "

    if current_part:
        tweet_parts.append(current_part.strip())

    return tweet_parts

def get_abstract(soup):
    try:
        abstract = soup.find('div',class_='abstract').text
        if len(abstract) < 840:
            return split_abstract(abstract,280)
        else:
            print('Abstract too long for now')
            return 1
    except(AttributeError):
           print('Abstract Doesnt exist')
           return 1

def runner():
    start_info = start()
    patent_number = start_info[0]
    url = start_info[1]
    soup = start_info[3]
    meta = start_info[4]
    i_list = trim_url_list(meta)
    file_list = download_imgs(i_list)
    body = get_body(soup,patent_number,url)
    abstract = get_abstract(soup)
    sendTweet(body,file_list,abstract)

def sendTweet(body,file_list,abstract,):
    media_ids = [api.media_upload(i).media_id_string for i in file_list] 
    print(media_ids)
    tweet = auth_v2.create_tweet(text=body, media_ids=media_ids)
    tweet_id = tweet.data['id']
    if abstract != 1:
        for ab in abstract:
            reply = auth_v2.create_tweet(in_reply_to_tweet_id=tweet_id,text=ab)
            reply_id = reply.data['id']
            tweet_id = reply_id
    for file in file_list:
        os.remove(file)
    print("tweeted!")


runner()

