import requests
import pandas as pd
from lxml import etree
import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from time import sleep
import threading
import DAO
from pyecharts import options as opts
from pyecharts.charts import Map ,Timeline,Bar,Line,Pie,EffectScatter
# import pyecharts.options as opts
from pyecharts.charts import WordCloud
from pyecharts import options as opts
import configparser
# 基础header

config = configparser.RawConfigParser()
config.read("/home/ly/Item/flask/config/config.ini")

Cookie = config.get("reptile","Cookie")
UA = config.get("reptile","UA")
proxy = config.get("reptile","proxy")
driverUrl = config.get("reptile","driverUrl")

up_url = "https://www.pixiv.net"
headers = {
            "Cookie":Cookie, "User-Agent":UA
          }
mainurl = "https://www.pixiv.net/ranking.php"

# data = [时间、作家、点赞、收藏、浏览、类型[],评分]
data_list = []


# 获取动态页面数据
def getDataFromWeb(url, nowTime):
    browser_options = Options()
    browser_options.add_argument('--headless')
    browser_options.add_argument('--disable-gpu')
    browser_options.add_argument("--proxy-server="+proxy)

    #browser_options.add_argument("--proxy-server=http://10.112.78.231:7890")
    service = Service(driverUrl)
    browser = webdriver.Edge(service=service,options=browser_options)
    print(url)
    browser.get(url)
    time.sleep(10)

    taget = [a.text for a in browser.find_elements(By.CLASS_NAME,'gtm-new-work-tag-event-click')]

    temp = [b.text for b in [a.find_element(By.TAG_NAME,'dd') for a in
                             browser.find_element(By.CLASS_NAME,'dpDffd').find_elements(By.TAG_NAME,'li')]]

    writer = browser.find_element(By.CLASS_NAME,'ipIUhW').find_element(By.TAG_NAME,'div').text
    browser.close()
    browser.quit()

    return [nowTime, writer, temp[0], temp[1], temp[2], taget]

# 线程任务—获取数据
def thread_getData(url_list,nowTime):
    for url in url_list:
        print('--'+url)
        data_list.append(getDataFromWeb(url,nowTime))
        time.sleep(0.5)

# 获取下一页的数据
def get_NewPage(url):
    if url == "":
        url = "https://www.pixiv.net/ranking.php"
    print(url)
    context = requests.get(url = url,headers=headers,proxies={'http':'http://10.112.78.231:7890','https':'http://10.112.78.231:7890','socks':'socks5://10.112.78.231:7890'}).text
    html = etree.HTML(context)
    print('finished get')
    nowtime = html.xpath('//*[@id="wrapper"]/div[1]/div/div[2]/div/nav[2]/ul/li[2]/a/text()')[0] # 获取当前排名的日期----nowtime
    print(nowtime.encode("utf-8").decode("latin1"))
    o = html.xpath('/html/body/div[3]/div[1]/div/div[3]/div[1]/section/div[2]/a[1]/@href')
    o = [up_url+x for x in o if "user" not in x] # 各个图片的网页
    return o,nowtime,html

if __name__ == "__main__":
    # 进入各个网页，收集他们的标签等信息

    start = time.time()
    threads = []
    next_url = ""
    ok = False
    for j in range(1):
        o, nowtime, html = get_NewPage(next_url)
        l = 0
        r = len(o) // 5
        print(2)
        thread_getData(o[0:2],nowtime)
        #for i in range(10):
        #    thread1 = threading.Thread(target=thread_getData, args=(o[l:r], nowtime))
        #    l += len(o) // 5
        #    r += len(o) // 5
        #    threads.append(thread1)
        #for i in threads:
        #    i.start()
        #for t in threads:
        #    t.join()

        print("ok!", end=" ")
        #print(nowtime)
        print(len(data_list))

        print("\n")
        # for t in threads:
        #     del (t)
        # threads.clear()
        if ok == False:
            next_url = \
            [mainurl + i for i in html.xpath('//*[@id="wrapper"]/div[1]/div/div[2]/div/nav[2]/ul/li[3]/a/@href')][0]
            ok = True
        else:
            next_url = \
            [mainurl + i for i in html.xpath('//*[@id="wrapper"]/div[1]/div/div[2]/div/nav[2]/ul/li[4]/a/@href')][0]
    end = time.time()
    print(end - start)

    data = pd.DataFrame(data_list)
    #print(data)

    data.columns = ['日期', '作者', '点赞', '收藏', '浏览', '类型']
    data['点赞'] = data['点赞'].str.replace(',', '')
    data[['点赞']] = data[['点赞']].astype('int')
    data['收藏'] = data['收藏'].str.replace(',', '')
    data[['收藏']] = data[['收藏']].astype('int')
    data['浏览'] = data['浏览'].str.replace(',', '')
    data[['浏览']] = data[['浏览']].astype('int')
    data['日期'] = data['日期'].astype('string')
    data['作者'] = data['作者'].astype('string')
    data['类型'] = data['类型'].astype('string')
    data['评分'] = data.点赞 * 0.3 + data.收藏 * 0.5 + data.浏览 * 0.2

    DAO.insert(data)

