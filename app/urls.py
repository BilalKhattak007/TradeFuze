from django.urls import path
from . import views
from .views import user_login

urlpatterns = [
    path("",user_login,name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('home', views.home, name='home'),
    path('addTrade',views.addTrade,name='addTrade'),
    path("trades",views.trades,name="trades"),
    path("monthlycal",views.monthlyCal,name="monthlyCal"),
    path("rules",views.rules,name="rules"),
    path("wallet",views.wallet,name="wallet"),
]
