from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('codes/<int:code_id>/', code_details, name="code_details"),
    path('codes/<int:code_id>/add_to_calculation/', add_code_to_draft_calculation, name="add_code_to_draft_calculation"),
    path('calculations/<int:calculation_id>/delete/', delete_calculation, name="delete_calculation"),
    path('calculations/<int:calculation_id>/', calculation)
]
