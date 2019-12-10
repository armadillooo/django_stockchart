from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.core.paginator import Paginator
from stocks.models import Company, Price, Adjust

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

from datetime import datetime
import time
from dateutil.relativedelta import relativedelta as delta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpl_finance
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io

#グラフの表示
def index(request, terms):
    year = datetime.now().year
    code = request.GET.get('code', 1400)
    term = request.GET.get('term', '1year')
    
    #対応する銘柄があるかどうか
    if not code:
        return render(request, 'index.html', {'code':'non value', 'invaild':True})
    if not Company.objects.filter(code=code):
        return render(request, 'index.html', {'code':code, 'invaild':True})

    name = Company.objects.get(pk=code).name
    return render(request, 'index.html', {'code':code, 'name':name, 'terms':terms, 'term':term})


#全株価を取得
def get_price(reqest):
    year = datetime.now().year
    code_list = Company.objects.values_list('code', flat=True)

    for code in code_list:
        for each in range(year, 2015, -1):
            html = urlopen('https://kabuoji3.com/stock/{}/{}/'.format(code, each))
            bsObj = BeautifulSoup(html, features='lxml')
            data = bsObj.findAll('tr')[:0:-1]

            for tr in data:
                try:
                    td_list = [td.text for td in tr.findAll('td')]
                    date_str = td_list[0]
                    prime = str(code) + ':' + str(date_str)

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
        time.sleep(0.5)
    return redirect(to='../')


#銘柄一覧を取得
def get_company(request):
    for page in range(1, 100):
        url =  urlopen('https://kabuoji3.com/stock/?page={}'.format(page))    
        bs = BeautifulSoup(url, features='lxml')
        
        data = bs.findAll('tr')[1:]
        for tr in data:
            try:
                td_list = list(tr.findAll('td'))
                names = td_list[0].text.split()

                code = int(names[0])
                name = ''.join(names[1:])
                market = td_list[1].text
        
                company = Company.objects.create(
                    code=code,
                    name=name,
                    market=market,
                )
            except:
                pass
        time.sleep(0.2)
    return redirect(to='../')


#グラフの表示
def plot_chart(request, code, term, terms):
    ohlc_dict =  {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }
    '''
    freq = 'W'
    period = 1
    window = 75
    width = 4.0
    '''
    #データの集計(月,年で場合分け)
    freq, window, period, width = terms[term]

    end = Price.objects.filter(code=code).last().date
    if term == '3month' or term == '6month':
        start = end - delta(months=period)
    else:
        start = end - delta(years=period)

    query = Price.objects.filter(code=code).filter(date__range=(start,end)).order_by('date')

    x_list = [q.date for q in query]

    array = np.array([[r.date, r.open, r.high, r.low, r.close] for r in query])

    df = pd.DataFrame(array, columns=['date', 'open', 'high', 'low', 'close'])
    df = df.set_index('date')
    #株式調整
    for row in Adjust.objects.filter(code=code):
        if row.date <= end:
            df.loc[df.index <= row.date] *= row.constant
    df.index = pd.to_datetime(df.index)
    
    ohlc_df = df.resample(freq).aggregate(ohlc_dict)
    ohlc_df.index = mdates.date2num(ohlc_df.index)
    ohlc_array = ohlc_df.reset_index().values

    average_list = [[r.date, r.adjust] for r in Price.objects.filter(code=code).order_by('date')]
    average_df = pd.DataFrame(average_list, columns=['date', 'adjust'])
    average_df = average_df.set_index('date').rolling(window).mean()
    average_df = average_df[average_df.index >= start]
    
    fig, ax = plt.subplots()

    mpl_finance.candlestick_ohlc(ax, ohlc_array, width=width)
    average_df.plot(ax=ax)

    ax.grid()

    steps = int(len(x_list) / 4)
    ax.set_xticks(x_list[0::steps])

    canvas = FigureCanvasAgg(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    plt.close(fig)
    return HttpResponse(output.getvalue(), content_type='image/png')


#企業一覧の表示
def show_company(request, markets, coderanges):
    word = request.GET.get('word', '')
    market = request.GET.get('market', '')
    coderange = request.GET.get('coderange', '')
    page = request.GET.get('page')

    result = Company.objects.order_by('code')
    if word:
        result = result.filter(name__icontains=word)
    if market:
        result = result.filter(market=market)
    if coderange:
        coderange = int(coderange)
        result = result.filter(code__range=(coderange, coderange+1000))

    paginator = Paginator(result, 50)
    content = paginator.get_page(page)
    return render(request, 'search.html', {'content':content, 'word':word, 'markets':markets, 'market':market, 'coderanges':coderanges, 'coderange':str(coderange)})


#株価併合、分割のデータの取得
def get_adjust(request):
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

        for tr in data:
            try:
                td_list = tr.findAll('td')
                
                date = datetime.strptime(td_list[0].text.replace('\n', ''), '%Y/%m/%d')
                
                code = int(td_list[2].text)
                
                div = td_list[4].text.split(':')
                constant = float(div[0]) / float(div[1])

                if Company.objects.filter(code=code):
                    adjust = Adjust.objects.create(
                        prime=str(date) + ':' + str(code) + ':' + str(constant),
                        date=date,
                        code=Company.objects.get(code=code),
                        constant=constant,
                    )
            except:
                pass
            time.sleep(0.5)

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
        
        for tr in data:
            try:
                td_list = tr.findAll('td')
                
                mul = re.findall('[0-9]{1,3}', td_list[3].text)
                constant = float(mul[0]) / float(mul[1])
            
                date_str = re.findall('[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}', td_list[4].text)[0]
                date = datetime.strptime(date_str, '%Y/%m/%d')
                
                code = int(td_list[1].text)

                if Company.objects.filter(code=code):
                    adjust = Adjust.objects.create(
                        prime=str(date) + ':' + str(code) + ':' + str(constant),
                        date=date,
                        code=Company.objects.get(code=code),
                        constant=constant,
                    )
            except:
                pass    
            time.sleep(0.5)
    return redirect(to='../')