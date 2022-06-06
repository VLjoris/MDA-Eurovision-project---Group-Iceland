from django.contrib import admin
from django.urls import path,include
from home.views import *
urlpatterns = [
    path('',go_index,name="index"),
    path('country/<str:_code>', go_country, name="go_country"),
    path('graph/', go_graph , name="go_graph"),
    path('predictions/',go_predictions, name="go_predictions")
]
