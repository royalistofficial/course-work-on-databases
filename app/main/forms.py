from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Customer, 
    Supplier, 
    Warehouse, 
    Product, 
    SupplierProductPrice, 
    Recipe, 
    RecipeProducts, 
    OrderList, 
    Userdj,
    Workshop,
    WarehouseProducts,
    DebitingList
)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']
        labels = {
            'name': 'Имя клиента',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Введите имя клиента',
                'class': 'form-control',
                'maxlength': 100,
            }),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']
        labels = {
            'name': 'Имя поставщика',
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Введите имя поставщика',
                'class': 'form-control',
                'maxlength': 100,
            }),
        }

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['max_warehouse_capacity']
        labels = {
            'category': 'Категория',
            'max_warehouse_capacity': 'Максимальная вместимость склада',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'max_warehouse_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'warehouse', 'expiry_date', 'mass']
        labels = {
            'name': 'Название продукта',
            'warehouse': 'Склад',
            'expiry_date': 'Срок годности',
            'mass': 'Масса (кг)',
        }

        widgets = {
            'mass': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'expiry_date': forms.NumberInput(attrs={'step': '1', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_mass(self):
        mass = self.cleaned_data.get('mass')
        if mass is not None and mass < 0:
            raise forms.ValidationError('Mass cannot be negative.')
        return mass

class SupplierProductPriceForm(forms.ModelForm):
    class Meta:
        model = SupplierProductPrice
        fields = ['supplier', 'product', 'price']
        labels = {
            'supplier': 'Поставщик',
            'product': 'Продукт',
            'price': 'Цена',
        }

        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price
    

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'finish_product']
        labels = {
            'name': 'Название рецепта',
            'finish_product': 'Готовый продукт',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'finish_product': forms.Select(attrs={'class': 'form-control'}),
        }

class RecipeProductsForm(forms.ModelForm):
    class Meta:
        model = RecipeProducts
        fields = ['recipe', 'product', 'quantity']
        labels = {
            'recipe': 'Рецепт',
            'product': 'Продукт',
            'quantity': 'Количество',
        }
        widgets = {
            'recipe': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class OrderListForm(forms.ModelForm):
    class Meta:
        model = OrderList
        fields = ['customer', 'product', 'quantity', 'date_order', 'price']
        widgets = {
            'date_order': forms.HiddenInput(),
        }
        labels = {
            'customer': 'Клиент',
            'product': 'Продукт',
            'quantity': 'Количество',
            'date_order': 'Дата заказа',
            'price': 'Стоимость 1 товара',
        }

    def __init__(self, *args, **kwargs):
        super(OrderListForm, self).__init__(*args, **kwargs)
        userdj = Userdj.objects.first()
        if userdj:
            self.initial['date_order'] = userdj.date_now


class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ['name', 'max_capacity', 'recipe']
        labels = {
            'name': 'Название мастерской',
            'max_capacity': 'Максимальная производительность кг/сут',
            'recipe': 'Рецепт',
        }
        widgets = {
            'max_capacity': forms.NumberInput(attrs={'min': 0}), 
        }

class WarehouseProductsForm(forms.ModelForm):
    class Meta:
        model = WarehouseProducts
        fields = ['product', 'quantity', 'production_date']
        labels = {
            'product': 'Продукт',
            'quantity': 'Количество',
            'production_date': 'Дата производства',
        }
        
    def __init__(self, *args, **kwargs):
        super(WarehouseProductsForm, self).__init__(*args, **kwargs)
        userdj = Userdj.objects.first()
        if userdj:
            self.initial['production_date'] = userdj.date_now

class UserdjForm(forms.ModelForm):
    class Meta:
        model = Userdj
        fields = ['date_now']
        widgets = {
            'date_now': forms.HiddenInput(),
            }

    def save(self, commit=True):
        userdj = super().save(commit=False)
        if userdj.date_now:
            userdj.date_now += timezone.timedelta(days=1)
            self.new_day(userdj)
        if commit:
            userdj.save()
        return userdj

    def new_day(self, userdj):
        self.debiting(userdj)

    def debiting(self, userdj):
        warehouse_products = WarehouseProducts.objects.all()
        for warehouse_product in warehouse_products:
            if warehouse_product.production_date + timezone.timedelta(days=warehouse_product.product.expiry_date) < userdj.date_now:
                DebitingList.objects.create(
                    product = warehouse_product.product,
                    quantity = warehouse_product.quantity,
                    date_of_debiting = userdj.date_now,
                    fresh = False,
                )
                # это кринж но надо по тз
                supplier_product_price = SupplierProductPrice.objects.filter(product=warehouse_product.product).order_by('price').first()
                if supplier_product_price is not None:
                    userdj.capital += float(supplier_product_price.price )* float(warehouse_product.quantity)

                warehouse_product.delete()

        warehouses = Warehouse.objects.all()
        for warehouse in warehouses:
            max_warehouse_capacity = warehouse.max_warehouse_capacity
            warehouse_products = WarehouseProducts.objects.filter(product__in = Product.objects.filter(warehouse = warehouse))
            for warehouse_product in warehouse_products:
                max_warehouse_capacity -= warehouse_product.quantity
                if max_warehouse_capacity < 0:
                    DebitingList.objects.create(
                        product = warehouse_product.product,
                        quantity = warehouse_product.quantity,
                        date_of_debiting = userdj.date_now,
                        fresh = True,
                    )
                    # это кринж но надо по тз
                    supplier_product_price = SupplierProductPrice.objects.filter(product=warehouse_product.product).order_by('price').first()
                    if supplier_product_price:
                        userdj.capital += float(supplier_product_price.price) * float(warehouse_product.quantity)

                    warehouse_product.delete()
                    self.debiting(userdj)
                    break




                

