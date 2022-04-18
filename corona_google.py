# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 19:33:47 2020

@author: Daria Kravets
"""

import urllib.request as request
import urllib.parse as parse
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
import datetime
import requests
import time
import logging
import text_extractor
import random



user_agent_list = [
   #Chrome
   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
   "Mozilla/5.0 (X11; Fedora;Linux x86; rv:60.0) Gecko/20100101 Firefox/60.0",
   "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
   "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"

]



def google(PROXY, keyword_list, country, scraped_text): #keyword_list are the queries you want to search for; PROXY, scraped_text ignore
    headers = {
            'User-Agent': '{}'.format(random.choice(user_agent_list))
    }


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

    proxy_dic = {"com": "US",
          "de": "DE",
          "ee": "EE",
          "by": "BY",
          "com.ua": "UA",
          "ru": "RU"

        }
    timestamp = str(datetime.datetime.now()).split('.')[0]
    day = timestamp.split(" ")[0]
    hour = timestamp.split(" ")[1].split(":")[0]
    day = str(day) 
    found_results = []

    hl_wert =  hl_dic.get(country)
    gl_wert =gl_dic.get(country).upper()
    
    proxy = PROXY

    for keyword in keyword_list:
        count_exceptions = 0
        keyword = keyword.replace(' ', '+')
        url = f"https://www.google.{country}/search?num=22&q={keyword}&gl={gl_wert}&hl={hl_wert}"
        status = "0"
        while (status != "200"):
            try:
                if country == "by": #Add proxies for Belarus instead of "..."
                    response = requests.get(url,proxies={"http": "...", "https": "..."}, timeout=10, headers=headers)
                else:
                    response = requests.get(url,proxies={"http": proxy, "https": proxy}, timeout=10, headers=headers)
                response.encoding = 'utf-8'

                content = BeautifulSoup(response.content, "html.parser")
                status = str(response.status_code)
                if status == "429":
                    raise Exception

                def parse_results(soup, keyword, scraped_text):
                    rank = 1
                    result_block = soup.find_all('div', attrs={'class': 'g'})
                    print(len(result_block))
                    for result in result_block:

                        link = result.find('a', href=True)
                        title = result.find('h3')
                        description = result.find('div', attrs={'class':'IsZvec'})
                        if link and title:

                            link = link['href']
                            title = title.get_text()
                            if description:
                                description = description.get_text()
                            if link != '#':

                                if link in scraped_text:
                                    fulltext=(scraped_text.get(link))
                                elif "youtube" in link:
                                    scraped_text.update({"{}".format(link):"Youtube"})
                                    fulltext = "Youtube"
                                else:
                                    try:
                                        fulltext = text_extractor.get_text(link)
                                        scraped_text.update({"{}".format(link):"{}".format(fulltext)})
                                    except requests.exceptions.MissingSchema:
                                        fulltext = "URL-Mistake"
                                        scraped_text.update({"{}".format(link):"URL-Mistake"})
                                    except:
                                        print("oops")
                                        fulltext = "Unknown-Mistake"
                                        scraped_text.update({"{}".format(link):"Unknown-Mistake"})
                                        #continue
                                    finally:
                                        time.sleep(1)
                                found_results.append({"date": str(day), "country": country, 'keyword': keyword, 'rank': rank, 'title': title, 'description': description, "link": link, "fulltext": fulltext})
                                rank += 1

                    return found_results, scraped_text
                parse_results(content, keyword, scraped_text)
                time.sleep(10)

            except Exception as e: #Never happens
                proxy = "http://login-country-{}:password@209.205.216.221:9000".format(proxy_dic.get(country))
                count_exceptions = count_exceptions+1
                headers = {
                        'User-Agent': '{}'.format(random.choice(user_agent_list))
                }
                time.sleep(5)


    found_results = pd.DataFrame(found_results)


    #Connecting to the AWS RDS MySQL Database -> Just save a .csv file
    try:
        engine = create_engine('mysql+mysqlconnector://root:password@xxx.cz5mu6sb6zby.eu-central-1.rds.amazonaws.com:3306/xxx',  echo=False)
        found_results.to_sql(name='Google_table', con=engine, if_exists = 'append', index=False)

    except IOError as e:
        #s.sendmail(MY_ADDRESS, MY_ADDRESS, "Subject: MISTAKE occurred\n\nSomething is wrong with the database")
        print (e)

    return scraped_text

if __name__ == "__main__":

   google()
