from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
from stocks.models import Company


#銘柄一覧を取得
def run():
    url = urlopen('https://kabuoji3.com/stock/')
    bs = BeautifulSoup(url, features='lxml')
    page_list = [li.text for li in bs.find('ul', {'class': 'pager'}).findAll('li')]
    for page in page_list:
        url =  urlopen('https://kabuoji3.com/stock/?page={}'.format(page))    
        bs = BeautifulSoup(url, features='lxml')
        data = bs.findAll('tr')[1:]

        time.sleep(0.5)
        for tr in data:
            td_list = list(tr.findAll('td'))
            names = td_list[0].text.split()

            code = int(names[0])
            name = ''.join(names[1:])
            market = td_list[1].text
            try:
                company = Company.objects.create(
                    code=code,
                    name=name,
                    market=market,
                )
            except:
                pass