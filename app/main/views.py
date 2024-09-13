from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Customer,
    Supplier,
    Warehouse,
    Product,
    CustomerProductPrice,
    Recipe,
    RecipeProducts,
    OrderList,
    Workshop,
)

from .forms import (
    CustomerForm,
    SupplierForm,
    WarehouseForm,
    ProductForm,
    CustomerProductPriceForm,
    RecipeForm,
    RecipeProductsForm,
    OrderListForm,
    WorkshopForm,
)

def index(request):    
    recipes_list = []
    recipes = Recipe.objects.all()
    for recipe in recipes:
        recipes_list.append({'recipe':recipe, 'recipe_products':RecipeProducts.objects.filter(recipe = recipe)})


    context = {'customers': Customer.objects.all(),
               'suppliers': Supplier.objects.all(),
               'warehouses': Warehouse.objects.all(),
               'products': Product.objects.all(),
               'customer_product_prices': CustomerProductPrice.objects.all(),
               'recipes': recipes_list,
               'order_list': OrderList.objects.all(),
               'workshops': Workshop.objects.all(),
               }    

    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def success(request):
    return render(request, 'success.html')

def handle_form(request, form_class, instance=None, action='Create'):
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('main:success')
    else:
        form = form_class(instance=instance)
    
    return render(request, 'form.html', {'form': form, 'action': action})

def create_customer(request):
    return handle_form(request, CustomerForm, action='Создать клиента')

def update_customer(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    return handle_form(request, CustomerForm, instance=customer, action='Обновить клиента')

def create_supplier(request):
    return handle_form(request, SupplierForm, action='Создать поставщика')

def update_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
    return handle_form(request, SupplierForm, instance=supplier, action='Обновить поставщика')

def create_warehouse(request):
    return handle_form(request, WarehouseForm, action='Создать склад')

def update_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
    return handle_form(request, WarehouseForm, instance=warehouse, action='Обновить склад')

def create_product(request):
    return handle_form(request, ProductForm, action='Создать продукт')

def update_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    return handle_form(request, ProductForm, instance=product, action='Обновить продукт')

def create_customer_product_price(request):
    return handle_form(request, CustomerProductPriceForm, action='Создать цену продукта для клиента')

def update_customer_product_price(request, customer_product_price_id):
    customer_product_price = get_object_or_404(CustomerProductPrice, customer_product_price_id=customer_product_price_id)
    return handle_form(request, CustomerProductPriceForm, instance=customer_product_price, action='Обновить цену продукта для клиента')

def delete_customer_product_price(request, customer_product_price_id):
    price_instance = get_object_or_404(CustomerProductPrice, pk=customer_product_price_id)

    if request.method == 'POST':
        price_instance.delete()
        return redirect('main:success')

    return render(request, 'form_del.html', )

def create_recipe(request):
    return handle_form(request, RecipeForm, action='Создать рецепт')

def update_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    return handle_form(request, RecipeForm, instance=recipe, action='Обновить рецепт')

def delete_recipe(request, recipe_id):
    price_instance = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == 'POST':
        price_instance.delete()
        return redirect('main:success')
    return render(request, 'form_del.html', )

def create_recipe_products(request):
    return handle_form(request, RecipeProductsForm, action='Создать продукты рецепта')

def update_recipe_products(request, recipe_products_id):
    recipe_products = get_object_or_404(RecipeProducts, recipe_products_id=recipe_products_id)
    return handle_form(request, RecipeProductsForm, instance=recipe_products, action='Обновить продукты рецепта')

def create_order_list(request):
    return handle_form(request, OrderListForm, action='Создать список заказов')

def update_order_list(request, order_list_id):
    order_list = get_object_or_404(OrderList, order_list_id=order_list_id)
    return handle_form(request, OrderListForm, instance=order_list, action='Обновить список заказов')

def delete_order_list(request, order_list_id):
    price_instance = get_object_or_404(OrderList, pk=order_list_id)
    if request.method == 'POST':
        price_instance.delete()
        return redirect('main:success')
    return render(request, 'form_del.html', )

def create_workshop(request):
    return handle_form(request, WorkshopForm, action='Создать мастерскую')

def update_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
    return handle_form(request, WorkshopForm, instance=workshop, action='Обновить мастерскую')

def delete_workshop(request, workshop_id):
    price_instance = get_object_or_404(Workshop, pk=workshop_id)
    if request.method == 'POST':
        price_instance.delete()
        return redirect('main:success')
    return render(request, 'form_del.html', )
