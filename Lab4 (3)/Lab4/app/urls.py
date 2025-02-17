from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/codes/', search_codes),  # GET
    path('api/codes/<int:code_id>/', get_code_by_id),  # GET
    path('api/codes/<int:code_id>/update/', update_code),  # PUT
    path('api/codes/<int:code_id>/update_image/', update_code_image),  # POST
    path('api/codes/<int:code_id>/delete/', delete_code),  # DELETE
    path('api/codes/create/', create_code),  # POST
    path('api/codes/<int:code_id>/add_to_calculation/', add_code_to_calculation),  # POST

    # Набор методов для заявок
    path('api/calculations/', search_calculations),  # GET
    path('api/calculations/<int:calculation_id>/', get_calculation_by_id),  # GET
    path('api/calculations/<int:calculation_id>/update/', update_calculation),  # PUT
    path('api/calculations/<int:calculation_id>/update_status_user/', update_status_user),  # PUT
    path('api/calculations/<int:calculation_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/calculations/<int:calculation_id>/delete/', delete_calculation),  # DELETE

    # Набор методов для м-м
    path('api/calculations/<int:calculation_id>/update_code/<int:code_id>/', update_code_in_calculation),  # PUT
    path('api/calculations/<int:calculation_id>/delete_code/<int:code_id>/', delete_code_from_calculation),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
