from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Customer,
    Supplier,
    Warehouse,
    Product,
    SupplierProductPrice,
    Recipe,
    RecipeProducts,
    OrderList,
    Workshop,
    Userdj,
    DebitingList,
    Cheque,
    ChequeProduct,
    WarehouseProducts,
)

from .forms import (
    CustomerForm,
    SupplierForm,
    WarehouseForm,
    ProductForm,
    SupplierProductPriceForm,
    RecipeForm,
    RecipeProductsForm,
    OrderListForm,
    WorkshopForm,
    UserdjForm,
    WarehouseProductsForm,
)

def index(request):    
    recipes_list = []
    recipes = Recipe.objects.all()
    for recipe in recipes:
        recipes_list.append({'recipe':recipe, 'recipe_products':RecipeProducts.objects.filter(recipe = recipe)})

    cheque_list = []
    cheques = Cheque.objects.all()
    for cheque in cheques:
        cheque_list.append({'cheque':cheque, 'cheque_product':ChequeProduct.objects.filter(cheque = cheque)})



    context = {'customers': Customer.objects.all(),
               'suppliers': Supplier.objects.all(),
               'warehouses': Warehouse.objects.all(),
               'warehouse_products': WarehouseProducts.objects.all(),
               'products': Product.objects.all(),
               'supplier_product_prices': SupplierProductPrice.objects.all(),
               'recipes': recipes_list,
               'order_list': OrderList.objects.all(),
               'workshops': Workshop.objects.all(),
               'userdj': Userdj.objects.first(),
               'debiting_list': DebitingList.objects.all(),
               'cheque_list': cheque_list,
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

def update_userdj(request):
    userdj = get_object_or_404(Userdj, user_id=1)
    return handle_form(request, UserdjForm, instance=userdj, action='Обновить дату')


def create_warehouse_products(request):
    return handle_form(request, WarehouseProductsForm, action='Купить продукт')


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

def create_supplier_product_price(request):
    return handle_form(request, SupplierProductPriceForm, action='Создать цену продукта для клиента')

def update_supplier_product_price(request, supplier_product_price_id):
    supplier_product_price = get_object_or_404(SupplierProductPrice, supplier_product_price_id=supplier_product_price_id)
    return handle_form(request, SupplierProductPriceForm, instance=supplier_product_price, action='Обновить цену продукта для клиента')

def delete_supplier_product_price(request, supplier_product_price_id):
    price_instance = get_object_or_404(SupplierProductPrice, pk=supplier_product_price_id)

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

def delete_recipe_products(request, recipe_products_id):
    recipe_products_instance = get_object_or_404(Recipe, pk=recipe_products_id)
    if request.method == 'POST':
        recipe_products_instance.delete()
        return redirect('main:success')
    return render(request, 'form_del.html', )

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

def debiting_list_view(request):
    debiting_list1 = []
    debiting_list2 = []
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            debiting_list1 = DebitingList.objects.filter(date_of_debiting__range=[start_date, end_date], fresh=True)
            debiting_list2 = DebitingList.objects.filter(date_of_debiting__range=[start_date, end_date], fresh=False)

    return render(request, 'debiting_list.html', {'debiting_list1': debiting_list1, 'debiting_list2': debiting_list2})


def cheque_list_view(request):
    cheque_list_customer = []
    cheque_list_supplier = []
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        warehouse = int(request.GET.get('warehouse') or 0)

        if start_date and end_date and warehouse:
            suppliers = Supplier.objects.all()
            for supplier in suppliers:
                cheque_supplier = []
                cheques = Cheque.objects.filter(date__range=[start_date, end_date], supplier=supplier)
                for cheque in cheques:
                    if warehouse == -1:
                        cheque_product = ChequeProduct.objects.filter(cheque = cheque)
                    else:
                        cheque_product = ChequeProduct.objects.filter(cheque = cheque, product__warehouse = warehouse)
                    if cheque_product:
                        cheque_supplier.append({'cheque':cheque, 'cheque_product':cheque_product})
                cheque_list_supplier.append({'supplier': supplier, 'cheque_supplier': cheque_supplier})
            
            customers = Customer.objects.all()
            for customer in customers:
                cheque_customer = []
                cheques = Cheque.objects.filter(date__range=[start_date, end_date], customer=customer)
                for cheque in cheques:
                    if warehouse == -1:
                        cheque_product = ChequeProduct.objects.filter(cheque = cheque)
                    else:
                        cheque_product = ChequeProduct.objects.filter(cheque = cheque, product__warehouse = warehouse)
                    
                    if cheque_product:
                        cheque_customer.append({'cheque':cheque, 'cheque_product':cheque_product})
                cheque_list_customer.append({'customer': customer, 'cheque_customer': cheque_customer})

    return render(request, 'cheque_list.html', {'cheque_list_supplier': cheque_list_supplier,
                                                'cheque_list_customer': cheque_list_customer,
                                                'warehouses': Warehouse.objects.all()})
