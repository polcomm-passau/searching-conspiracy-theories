# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 16:30:51 2020

@author: kravet01
"""

#AIzaSyAlHLWduCCLpEmkA2npnso9TaJHsjVXGi4


import urllib.request as request
import urllib.parse as parse
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
import datetime
import time
import os
import requests

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys




def get_keyword_list (country):
    country = country.lower()
    english_keywords = ["covid 19", "covid 19 origin", "covid 19 biological weapon",  "covid 19 truth", "covid 19 conspiracy theories", "covid 19 conspiracy"] #Origins?
    #english_keywords = ["covid 19"]
    russian_keywords = ["коронавирус", "коронавирус происхождение", "коронавирус биологическое оружие", "коронавирус правда", "коронавирус теории заговора", "коронавирус заговор"] #proishozhdenie

    keyword_dic = {"com": ["covid 19", "covid 19 origin", "covid 19 biological weapon", "covid 19 truth", "covid 19 conspiracy theories", "covid 19 conspiracy"],
                    "de": ["corona", "corona herkunft", "corona biologische waffe", "corona wahrheit", "corona verschwörungstheorien", "corona verschwörung" ], #Ursprung?
                    "ee": ["koroonaviirus", "koroonaviiruse päritolu","koroonaviirus bioloogiline relv", "koroonaviirus tõde", "koroonaviirus vandenõuteooriad", "koroonaviirus vandenõu"],
                    "by": ["каронавірус", "каронавірус паходжанне", "каронавірус біялагічная зброя", "каронавірус праўда", "каронавірус тэорыі змовы", "каронавірус змова"],
                    "com.ua": ["коронавірус", "коронавірус походження", "коронавірус біологічна зброя","коронавірус правда", "коронавірус теорії змови", "коронавірус змова"],
                    "ru": ["коронавирус", "коронавирус происхождение", "коронавирус биологическое оружие","коронавирус правда", "коронавирус теории заговора", "коронавирус заговор"],
                    
                   }


    keyword_list= keyword_dic.get(country)
    if country != "ru":
        #Country word will be added to all Russian laguage terms
        keyword_list.extend(russian_keywords)
        #Search first for Russian terms
        #keyword_list.reverse()
    if country != "com":
        keyword_list.extend(english_keywords)

    return keyword_list



def youtube(PROXY, keyword_list, country):
    try:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }


        titles = []
        links = []
        descriptions = []
        sources_name = []
        sources_link = []
        rank = []
        results_country =[]
        results_keyword=[]
        dates_list =[]
        age_list = []

        country_list = ["com", "de", "ee", "by", "com.ua", "ru"]
        print(keyword_list)


        print (PROXY)

        #Headless mode IMPORTANT
        # =============================================================================
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.headless = True

        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

# =============================================================================
        if country == "by":
             PROXY = "...." # Add Bel proxies

        firefox_capabilities['proxy'] = {
            "proxyType": "MANUAL",
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
        }




        # =============================================================================
        #     THis is Selenium without Proxies with Chrome.
        #     chrome_driver = r"C:/Users/kravet01/Documents/chromedriver"
        #     os.environ["webdriver.chrome.driver"] = chrome_driver
        #     driver = webdriver.Chrome(chrome_driver)
        # =============================================================================
        hl_dic = {"com": "en",
                  "de": "de",
                  "ee": "et",
                  "by": "be",
                  "com.ua": "uk",
                  "ru": "ru",

                }


        gl_dic = {"com": "us",
                  "de": "de",
                  "ee": "ee",
                  "by": "by",
                  "com.ua": "ua",
                  "ru": "ru",

                }

        timestamp = str(datetime.datetime.now()).split('.')[0]
        day = timestamp.split(" ")[0]
        hour = timestamp.split(" ")[1].split(":")[0]
        day = str(day) #+ str(hour)
        gl_wert =gl_dic.get(country).upper()
        print(gl_wert)


        print(country)


        for keyword in keyword_list:

            if country == "de":
                driver = webdriver.Firefox(options=options)
            else:
                driver = webdriver.Firefox(capabilities=firefox_capabilities, options=options)
            print ("Driver initialized")
            print (keyword)
            keyword = keyword.replace(' ', '+')
            url = f"https://www.youtube.{country}/results?search_query={keyword}&gl={gl_wert}&hl={hl_wert}"
            print (url)
            start = time.time()

            driver.get(url)
            print("Initialization took: {0} sec".format((time.time() - start)))



            count = len(driver.find_elements_by_xpath('//*[@id="video-title"]'))
            tries = 1
            #Wartet bis 50 Videos laden
            while (count < 50):
                if (tries < 10):
                    time.sleep(2)
                    body = driver.find_element_by_css_selector('body')
                    body.send_keys(Keys.END)
                    driver.implicitly_wait(3)
                    count = len(driver.find_elements_by_xpath('//*[@id="video-title"]'))
                    print (count)
                    tries += 1
                else:
                    break

            print ("raus")



            video_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
            video_description = driver.find_elements_by_xpath( '//*[@id="description-text"]')
            video_sources = driver.find_elements_by_xpath('//*[@id="channel-info"]/a')


            n=1
            for i, x, source in zip(video_data,video_description, video_sources):
                links.append(i.get_attribute('href'))
                titles.append(i.get_attribute('title'))  # //*[@id="video-title"]/yt-formatted-string
                descriptions.append(x.text)
                sources_link.append(source.get_attribute('href'))
                #sources_name.append(source.text)
                rank.append(n)
                results_country.append(country)
                results_keyword.append(keyword)
                dates_list.append(day)
                n+=1


            driver.quit()







        df = pd.DataFrame(list(zip(results_country, results_keyword,titles, links, descriptions, sources_link, rank, dates_list)), columns =["Country", "Keyword", "Title", "Link", "Description", "Source_link",  "Rank", "Date"])
        print (df)


        #Connecting to the MySQL Database

        try:
            engine = create_engine('mysql+mysqlconnector://root:password@xxx.cz5mu6sb6zby.eu-central-1.rds.amazonaws.com:3306/corona',  echo=False)
            df.to_sql(name='Youtube_table', con=engine, if_exists = 'append', index=False)

            #ToDO: EMail me if data is not being collected properly!
        except IOError as e:
            #s.sendmail(MY_ADDRESS, MY_ADDRESS, "Subject: MISTAKE occurred\n\nSomething is wrong with the database")
            print("Something is wrong with your database")
            print (e)
        #except:
        #    s.sendmail(MY_ADDRESS, MY_ADDRESS, "Subject: MISTAKE occurred\n\nSomething is wrong with the database")
        #

        #s.close()

    except Exception as e:
        print (e)
        raise Exception

#    finally:
#        print ("Closing Firefox driver")
#        driver.quit()
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here

   youtube()
   get_keyword_list()
