from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from stocks.models import Company, Price, Adjust

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

    latest = Price.objects.filter(code=code).last().date
    name = Company.objects.get(pk=code).name
    return render(request, 'index.html', {'code':code, 'name':name, 'terms':terms, 'term':term, "latest":latest})


#グラフの表示
def plot_chart(request, code, term, terms):
    ohlc_dict =  {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }
    freq, window, period, width = terms[term]
    end = Price.objects.filter(code=code).last().date
    if term == '3month' or term == '6month':
        start = end - delta(months=period)
    else:
        start = end - delta(years=period)

    query = Price.objects.filter(code=code).order_by('date')

    array = np.array([[r.date, r.open, r.high, r.low, r.close] for r in query.filter(date__range=(start, end))])

    df = pd.DataFrame(array, columns=['date', 'open', 'high', 'low', 'close']).set_index('date')
    #株式調整
    for row in Adjust.objects.filter(code=code):
        if row.date <= end:
            df.loc[df.index <= row.date] *= row.constant
    df.index = pd.to_datetime(df.index)
    
    ohlc_df = df.resample(freq).aggregate(ohlc_dict)
    ohlc_df.index = mdates.date2num(ohlc_df.index)
    ohlc_array = ohlc_df.reset_index().values
    #移動平均線
    series = pd.Series({r.date: r.adjust for r in query}).rolling(window).mean()
    series = series[series.index >= start]
    
    fig, ax = plt.subplots()

    mpl_finance.candlestick_ohlc(ax, ohlc_array, width=width)
    series.plot(ax=ax)

    ax.grid()

    x_label = pd.date_range(start, end)
    steps = int(len(x_label) / 4)
    ax.set_xticks(x_label[0::steps])

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
