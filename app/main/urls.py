"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('',views.index, name='index'),
    path('about/',views.about, name='about'),
    path('success/', views.success, name='success'),

    path('userdj_update/', views.update_userdj, name='update_userdj'),
    path('warehouse_products_create/', views.create_warehouse_products, name='create_warehouse_products'),
    
    path('customers_create/', views.create_customer, name='create_customer'),
    path('customers_update/<int:customer_id>/', views.update_customer, name='update_customer'),
    
    path('suppliers_create/', views.create_supplier, name='create_supplier'),
    path('suppliers_update/<int:supplier_id>/', views.update_supplier, name='update_supplier'),
    
    path('warehouses_create/', views.create_warehouse, name='create_warehouse'),
    path('warehouses_update/<int:warehouse_id>/', views.update_warehouse, name='update_warehouse'),
    
    path('products_create/', views.create_product, name='create_product'),
    path('products_update/<int:product_id>/', views.update_product, name='update_product'),
    
    path('create_supplier_product_price/', views.create_supplier_product_price, name='create_supplier_product_price'),
    path('update_supplier_product_price/<int:supplier_product_price_id>/', views.update_supplier_product_price, name='update_supplier_product_price'),
    path('delete_supplier_product_price/<int:supplier_product_price_id>/', views.delete_supplier_product_price, name='delete_supplier_product_price'),
    
    path('create_recipe/', views.create_recipe, name='create_recipe'),
    path('update_recipe/<int:recipe_id>/', views.update_recipe, name='update_recipe'),
    path('delete_recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    
    path('create_recipe_products/', views.create_recipe_products, name='create_recipe_products'),
    path('update_recipe_products/<int:recipe_products_id>/', views.update_recipe_products, name='update_recipe_products'),
    path('delete_recipe_products/<int:recipe_products_id>/', views.delete_recipe_products, name='delete_recipe_products'),

    path('create_order_list/', views.create_order_list, name='create_order_list'),
    path('update_order_list/<int:order_list_id>/', views.update_order_list, name='update_order_list'),
    path('delete_order_list/<int:order_list_id>/', views.delete_order_list, name='delete_order_list'),

    path('create_workshop/', views.create_workshop, name='create_workshop'),
    path('update_workshop/<int:workshop_id>/', views.update_workshop, name='update_workshop'),
    path('delete_workshop/<int:workshop_id>/', views.delete_workshop, name='delete_workshop'),

    path('debiting-list/', views.debiting_list_view, name='debiting_list'),  
    path('cheque-list/', views.cheque_list_view, name='cheque_list'),  
    
]
