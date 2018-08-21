import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, pytz, datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

br = webdriver.Chrome(chrome_options=options, executable_path='/usr/bin/chromedriver')

# grabbed from https://xivwb.gitee.io/#eure-1
br.get("https://xivwb.gitee.io/#eure-1")
br.implicitly_wait(10)
# print("***** %s" % br.page_source)

lines = br.find_elements_by_xpath("//div[@class='match']/table/tbody/tr")
for li in lines[:3]:
    items = li.find_elements_by_xpath("td")
    timestr = items[0].text.split(" ")[1]
    ts = time.mktime(time.strptime(timestr, "%H:%M:%S"))
    dt = datetime.datetime.fromtimestamp(ts, pytz.timezone("utc")).astimezone(pytz.timezone("Asia/Shanghai"))
    dt = dt - datetime.timedelta(minutes=6)
    print(dt)
    tzstr = dt.strftime("%H:%M:%S")
    print(u"【强风】 %s 持续 %s" % (tzstr, items[2].text))
   #  print(u"【强风】 %s 持续 %s" % (timestr, items[2].text))

br.close()
