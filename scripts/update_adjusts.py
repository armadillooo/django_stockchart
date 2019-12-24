from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
from datetime import datetime
from stocks.models import Company, Adjust
import re


#株価併合、分割のデータの取得
def run():
    #株価分割
    url = urlopen('https://www.rakuten-sec.co.jp/ITS/Companyfile/stock_split_20064.html')
    soup = BeautifulSoup(url, features='lxml')
    a_tags = soup.findAll('a', {'href':re.compile('stock.')})[::-1]

    #2015年以降のデータを取得
    href_list = [a['href'] for a in a_tags if int(re.search('20..', a['href']).group()) >= 2015]

    for href in href_list:
        html = urlopen('https://www.rakuten-sec.co.jp/ITS/Companyfile/{}'.format(href))
        bsObj = BeautifulSoup(html, features='lxml')
        data = bsObj.find('table', {'class':'ta1'}).findAll('tr')[1:]

        time.sleep(0.5)
        for tr in data:
            td_list = tr.findAll('td')
            
            date = datetime.strptime(td_list[0].text.replace('\n', ''), '%Y/%m/%d')
            
            code = int(td_list[2].text)
            
            div = td_list[4].text.split(':')
            constant = float(div[0]) / float(div[1])
            try:
                if Company.objects.filter(code=code):
                    adjust = Adjust.objects.create(
                        prime=str(date) + ':' + str(code) + ':' + str(constant),
                        date=date,
                        code=Company.objects.get(code=code),
                        constant=constant,
                    )
            except:
                break
        else:
            continue
        break
    #株価併合
    url = urlopen('https://www.rakuten-sec.co.jp/ITS/Companyfile/reverse_stock_split_20064.html')
    soup = BeautifulSoup(url, features='lxml')
    a_tags = soup.findAll('a', {'href':re.compile('reverse.')})[::-1]

    #2015年以降のデータを取得
    href_list = [a['href'] for a in a_tags if int(re.search('20..', a['href']).group()) >= 2015]

    for href in href_list:
        html = urlopen('https://www.rakuten-sec.co.jp/ITS/Companyfile/{}'.format(href))
        bsObj = BeautifulSoup(html, features='lxml')
        data = bsObj.find('table', {'class':'ta1'}).findAll('tr')[1:]
        
        time.sleep(0.5)
        for tr in data:
            td_list = tr.findAll('td')
            
            mul = re.findall('[0-9]{1,3}', td_list[3].text)
            constant = float(mul[0]) / float(mul[1])
        
            date_str = re.findall('[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}', td_list[4].text)[0]
            date = datetime.strptime(date_str, '%Y/%m/%d')
            
            code = int(td_list[1].text)
            try:
                if Company.objects.filter(code=code):
                    adjust = Adjust.objects.create(
                        prime=str(date) + ':' + str(code) + ':' + str(constant),
                        date=date,
                        code=Company.objects.get(code=code),
                        constant=constant,
                    )
            except:
                break  
        else:
            continue
        break