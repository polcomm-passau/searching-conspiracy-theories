# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 17:15:19 2020

@author: Daria Kravets
"""

import requests
#from bs4 import BeautifulSoup
import re
import random
import time
from selenium import webdriver
import os
import sys

#Import own modules
import corona_youtube
import corona_google
import corona_yandex


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

proxy_dic = {"com": "US",
          "de": "DE",
          "ee": "EE",
          "by": "BY",
          "com.ua": "UA",
          "ru": "RU"
        } 

#READ country list
try:
    with open("country_list.txt") as f:
        country_list = f.read().splitlines()
except FileNotFoundError:
    with open("scraping/country_list.txt") as f:
        country_list = f.read().splitlines()


#Random order of countries
random.shuffle(country_list)

print(country_list)


done_countries = []


i=random.randint(10, 80)
print("Randon number chosen: ", i)

#Scraped text
scraped_text = {}

for country in country_list:
    proxy_country = proxy_dic.get(country)
    keyword_list =  corona_youtube.get_keyword_list(country)
    random.shuffle(keyword_list)

    #For our proxies we used the services of the company ProxyRack - https://www.proxyrack.com/
    #Additionally, for Belarus for Yandex we bought proxies via Proxy-Seller - https://proxy-seller.com/ 

    #Scraping Google    
    print("Starting scraping Google")
    PROXY = "http://login-country-{}:password@209.205.216.221:100{}".format(proxy_country, str(i)) #ProxyRack

    try:
        scraped_text = corona_google.google(PROXY, keyword_list, country, scraped_text)
        i=i+2
    except Exception as e: #Catchin unexpected errors - Never happens
        print(e)
        print("Something is wrong with Google - restarting myself")
        for c in done_countries:
            country_list.remove(c)
        with open('country_list.txt', 'w') as f:  
            for country in country_list:
                f.write(country+'\n')
        #Restart
        os.execv(sys.executable, ['python3'] + sys.argv)

    # Scraping Youtube
    PROXY_youtube = PROXY.split("@")[1]
    print("Starting scraping Youtube")
    erfolg2 = 0
    while (erfolg2 ==0):
        try:
            corona_youtube.youtube(PROXY_youtube, keyword_list, country)
            erfolg2 +=1
            #driver.quit()
        except Exception as e:
            print (e)
            print("Proxy did not work. Going back to finding a proxy")
            time.sleep(2)
            if country == "by":
                PROXY_youtube = "..." #Insert your dic with proxies here and pick one
            else:
                #Activate another proxy
                print("Activated another proxy")
                PROXY_youtube = "http://login-country-{}:password@209.205.216.221:100{}".format(proxy_country, str(i+2))


    #Scraping Yandex
    print("Starting scraping Yandex")
    if country not in ["com.ua"]:
        if country == "by": 
            PROXY_yandex = "..." #Insert your dic with proxies here and pick one
        else: 
            PROXY_yandex = "http://login-country-{}:password@209.205.216.221:9000".format(proxy_country)
    
            try:
                scraped_text = corona_yandex.yandex(PROXY_yandex, keyword_list, country, scraped_text)
            except Exception as e:
               print(str(e))
               print("Something is wrong with Yandex - restarting myself")
               for c in done_countries:
                   country_list.remove(c)
               with open('country_list.txt', 'w') as f:  # Use file to refer to the file object
                   for country in country_list:
                       f.write(country+'\n')
               os.execv(sys.executable, ['python3'] + sys.argv)


    #Wait before choose another country
    time.sleep(5)
    
    #Add country to done
    done_countries.append(country)


#Saving full country list
country_list = ["de", "com.ua", "ru", "by", "com"]
try:
    with open('country_list.txt', 'w') as f:  # Use f to refer to the file object
        for country in country_list:
            f.write(country+'\n')
except FileNotFoundError:
    with open('scraping/country_list.txt', 'w') as f:  
        for country in country_list:
            f.write(country+'\n')


