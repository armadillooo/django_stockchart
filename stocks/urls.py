from django.urls import path
from . import views


#term: [freq, window, period, width]
terms = {
    '3month': ['D', 25, 3, 0.6],
    '6month': ['2D', 25, 6, 1.0],
    '1year': ['W', 75, 1, 4.0],
    '2year': ['W', 75, 2, 4.0],
    '4year': ['M', 200, 4, 10.0],
    }

markets = [
    'マザーズ',
    '名古屋セ',
    '名証1部',
    '名証2部',
    '名証ETF',
    '札幌ア',
    '札証',
    '東証',
    '東証1部',
    '東証1部外国',
    '東証2部',
    '東証2部外国',
    '東証ETF',
    '東証JQG',
    '東証JQS',
    '福岡Q',
    '福証',
 ]

coderanges = [str(i) for i in range(1000, 10000, 1000)]

urlpatterns = [
    path('', views.index, {'terms':terms}, name='index'),
    
    path('plot/<int:code>/<term>.png/', views.plot_chart, {'terms':terms}, name='plot'),

    path('search/', views.show_company, {'markets':markets, 'coderanges':coderanges}, name='search'),
]