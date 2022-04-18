# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 15:53:27 2020

@author: kravet01
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import time
import random
import sys
import text_extractor

from sqlalchemy import create_engine

user_agent_list = [
   #Chrome
   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
   "Mozilla/5.0 (X11; Fedora;Linux x86; rv:60.0) Gecko/20100101 Firefox/60.0"

]


def yandex(PROXY, keyword_list, country, scraped_text):
    headers = {
            'User-Agent': '{}'.format(random.choice(user_agent_list))
    }


    location_dic = {"de": "177",
                    "ru": "213",
                    "com": "87",
                    "by": "157",
                    "ee": "11481",
                    "com.ua": "143"

                    }

    version_dic = {"com": "com",
              "de": "com",
              "ee": "com",
              "by": "by",
              "com.ua": "ua",
              "ru": "ru",

            }

    proxy_dic = {"com": "US",
          "de": "DE",
          "ee": "RU",
          "by": "RU",
          "com.ua": "UA",
          "ru": "RU"

        }

    data_titles  = []
    data_links = []
    data_snippets = []
    rank = []
    date_list = []
    keywords = []
    results_country =[]
    fulltext = []

    timestamp = str(datetime.datetime.now()).split('.')[0]
    day = timestamp.split(" ")[0]
    hour = timestamp.split(" ")[1].split(":")[0]
    day = str(day) 


    location = location_dic.get(country)
    version = version_dic.get(country)

    proxy = PROXY
    time.sleep(2)
    i = 10

    if country == "by":
        proxy = "..." #Insert your dic with proxies here and pick one


    for keyword in keyword_list:
        count_exceptions = 0
        time.sleep(5)
        keyword = keyword.replace(' ', '+')
        URL_TO_SCRAPE = 'https://yandex.{}/search/?lr={}&text={}&numdoc=21'.format(version, location, keyword)
        status=0
        print(URL_TO_SCRAPE)

        while (status == 0):
            try:

                r = requests.get(URL_TO_SCRAPE,proxies={"http": proxy, "https": proxy}, timeout=10, headers=headers)
                time.sleep(5)
                print (r.status_code)
                content = BeautifulSoup(r.content, "html.parser")

                #Search results
                results = content.find_all("li", class_ = "serp-item")
                print (len(results))
                status = len(results)
                if status == 0:
                    raise Exception

            except AttributeError:
                continue
            except Exception as e:
                #Try again 
                count_exceptions = count_exceptions+1
                print("So many exceptions before: ", count_exceptions)
                if count_exceptions == 50:
                    print("Mistake occured too many times. Start new")
                    raise Exception
                print (e)
                time.sleep(2)
            else:
                n=1
                for result in results:
                    data_titles.append(result.find("div", class_="text-container").getText())
                    link = result.find("a", href=True).get('href')
                    data_links.append(str(link))
                    data_snippets.append(result.find("div", class_="organic__url-text").getText())
                    rank.append(n)
                    date_list.append(day)
                    keywords.append(keyword)
                    results_country.append(country)
                    n+=1
                    #Full Text
                    not_wished = ["//yandex.com/images/search", "//yandex.com/video/search",
                          "//yandex.ru/images/search?", "//yandex.ru/video/search?",
                          "//yandex.by/images/search?", "//yandex.by/video/search?",
                          "//yandex.ua/images/search?", "//yandex.ua/video/search?",
                          "youtube.by", "youtube.com", "youtube.de"
                          ] #Not organic search results or search results where text does not need to be scraped 
                    if str(link) in scraped_text:
                        fulltext.append(scraped_text.get(link))
                    elif any(x in link for x in not_wished):
                        fulltext.append("Not Wished")
                        scraped_text.update({"{}".format(link):"Not Wished"})
                    else:
                        try:
                            text = text_extractor.get_text(link)
                            fulltext.append(text)
                            scraped_text.update({"{}".format(link):"{}".format(text)})
                        except requests.exceptions.MissingSchema:
                            fulltext.append("URL-Mistake")
                            scraped_text.update({"{}".format(link):"URL-Mistake"})
                            continue
                        except:
                            fulltext.append("Unknown-Mistake")
                            scraped_text.update({"{}".format(link):"Unknown-Mistake"})
                            continue
                        finally:
                            time.sleep(1)
                time.sleep(15)



    df = pd.DataFrame(list(zip(results_country, keywords, date_list, data_titles, data_links, data_snippets, rank, fulltext)), columns =["Country", "Keyword", "Date", "Snippet", "Link", "Title", "Rank", "Fulltext"])

#Saving the data in the AWS RDS MySQL database 
    try:
        engine = create_engine('mysql+mysqlconnector://root:login@password.eu-central-1.rds.amazonaws.com:3306/corona',  echo=False)
        df.to_sql(name='Yandex_table', con=engine, if_exists = 'append', index=False)

    except IOError as e:
        print (e)
        #Sent an E-Mail with an error to us.

    return scraped_text

if __name__ == "__main__":

   yandex()
