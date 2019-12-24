from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
from stocks.models import Price, Company

def run():
    year = datetime.now().year
    code_list = [row.code for row in Company.objects.all()]
    for code in code_list:
        print(code)
        for each in range(year, 2016, -1):
            html = urlopen('https://kabuoji3.com/stock/{}/{}/'.format(code, each))
            bsObj = BeautifulSoup(html, features='lxml')
            data = bsObj.findAll('tr')[:0:-1]

            time.sleep(0.5)
            for tr in data:
                td_list = [td.text for td in tr.findAll('td')]
                date_str = td_list[0]
                prime = str(code) + ':' + str(date_str)
                print(date_str)
                try:
                    price = Price.objects.create(
                        prime=prime,
                        date=datetime.strptime(date_str, '%Y-%m-%d'),
                        code=Company.objects.get(code=code),
                        open=float(td_list[1]),
                        high=float(td_list[2]),
                        low=float(td_list[3]),
                        close=float(td_list[4]),
                        volume=float(td_list[5]),
                        adjust=float(td_list[6]),
                    )              
                except:
                    break
            else:
                continue
            break