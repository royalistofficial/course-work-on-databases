from django import forms
from .models import (
    Customer, 
    Supplier, 
    Warehouse, 
    Product, 
    CustomerProductPrice, 
    Recipe, 
    RecipeProducts, 
    OrderList, 
    Userdj,
    Workshop
)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']
        labels = {
            'name': 'Имя клиента',
        }
        help_texts = {
            'name': 'Введите полное имя клиента.',
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
        help_texts = {
            'name': 'Введите полное имя поставщика.',
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
        fields = ['category', 'max_warehouse_capacity']
        labels = {
            'category': 'Категория',
            'max_warehouse_capacity': 'Максимальная вместимость склада',
        }
        help_texts = {
            'category': 'Выберите категорию склада.',
            'max_warehouse_capacity': 'Введите максимальную вместимость склада.',
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
        help_texts = {
            'name': 'Введите название продукта.',
            'warehouse': 'Выберите склад, на котором хранится продукт.',
            'expiry_date': 'Выберите срок годности продукта.',
            'mass': 'Введите массу продукта в килограммах.',
        }
        widgets = {
            'mass': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_mass(self):
        mass = self.cleaned_data.get('mass')
        if mass is not None and mass < 0:
            raise forms.ValidationError('Mass cannot be negative.')
        return mass

class CustomerProductPriceForm(forms.ModelForm):
    class Meta:
        model = CustomerProductPrice
        fields = ['customer', 'product', 'price']
        labels = {
            'customer': 'Клиент',
            'product': 'Продукт',
            'price': 'Цена',
        }
        help_texts = {
            'customer': 'Выберите клиента.',
            'product': 'Выберите продукт.',
            'price': 'Введите цену продукта для клиента.',
        }
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
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
        help_texts = {
            'name': 'Введите название рецепта.',
            'finish_product': 'Выберите готовый продукт, связанный с рецептом.',
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
        help_texts = {
            'recipe': 'Выберите рецепт, к которому относится продукт.',
            'product': 'Выберите продукт, используемый в рецепте.',
            'quantity': 'Введите количество продукта, необходимое для рецепта.',
        }
        widgets = {
            'recipe': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class OrderListForm(forms.ModelForm):
    class Meta:
        model = OrderList
        fields = ['customer', 'product', 'quantity', 'date_order']
        widgets = {
            'date_order': forms.HiddenInput(),
        }
        labels = {
            'customer': 'Клиент',
            'product': 'Продукт',
            'quantity': 'Количество',
            'date_order': 'Дата заказа',
        }

    def __init__(self, *args, **kwargs):
        super(OrderListForm, self).__init__(*args, **kwargs)
        userdj_instance = Userdj.objects.first()
        if userdj_instance:
            self.initial['date_order'] = userdj_instance.date_now


class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ['name', 'max_capacity', 'recipe']
        labels = {
            'name': 'Название мастерской',
            'max_capacity': 'Максимальная вместимость',
            'recipe': 'Рецепт',
        }
        help_texts = {
            'name': 'Введите название мастерской.',
            'max_capacity': 'Введите максимальное количество участников.',
            'recipe': 'Выберите рецепт, связанный с мастерской.',
        }
        widgets = {
            'max_capacity': forms.NumberInput(attrs={'min': 0}), 
        }