from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('codes/<int:code_id>/', code),
    path('calculations/<int:calculation_id>/', calculation),
]