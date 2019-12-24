from django.urls import path
from . import views
 

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('favorite/', views.favorite, name='favorite'),
    path('my_page/', views.my_page, name='my_page'),
]