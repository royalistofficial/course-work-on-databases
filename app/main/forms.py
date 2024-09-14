from django import forms
from django.db import transaction
from django.db.models import Sum
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
    DebitingList,
    Cheque,
    ChequeProduct
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

    def save(self, commit=True):
        warehouse_product = super(WarehouseProductsForm, self).save(commit=commit)
        
        if commit:
            if self.add_cheque_buy(warehouse_product):
                raise ValidationError("Такой продукт не продается")
        
        return warehouse_product
    
    def add_cheque_buy(self, warehouse_product):
        supplier_product_price = SupplierProductPrice.objects.filter(product=warehouse_product.product).order_by('price').first()
        if supplier_product_price:
            userdj = Userdj.objects.first()
            cheque = Cheque.objects.create(
                date=userdj.date_now,  
                customer=None,
                supplier=supplier_product_price.supplier,
            )
            ChequeProduct.objects.create(
                cheque=cheque,
                product=warehouse_product.product,
                price=supplier_product_price.price,
                quantity=warehouse_product.quantity,
            )
            userdj.capital -= float(warehouse_product.quantity) * float(supplier_product_price.price)
            userdj.save()
            return False
        return True

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
        self.workshop_update(userdj)
        self.order_update(userdj)
        self.debiting_update(userdj)
    
    def order_update(self, userdj):
        order_list = OrderList.objects.all()
        for order in order_list:
            warehouse_products = WarehouseProducts.objects.filter(product = order.product)
            total_quantity = warehouse_products.aggregate(total=Sum('quantity'))['total']
            if total_quantity < order.quantity:
                cheque = Cheque.objects.create(
                    date=userdj.date_now,  
                    customer=order.customer,
                    supplier=None,
                )
                ChequeProduct.objects.create(
                    cheque=cheque,
                    product=order.product,
                    price= total_quantity * float(order.price),
                    quantity = total_quantity,
                )
                userdj.capital += total_quantity * float(order.price)
                userdj.save()
                warehouse_products.delete()
                order.quantity -= total_quantity
                order.save()
            elif total_quantity >= order.quantity:
                cheque = Cheque.objects.create(
                    date=userdj.date_now,  
                    customer=order.customer,
                    supplier=None,
                )
                ChequeProduct.objects.create(
                    cheque=cheque,
                    product=order.product,
                    price=order.quantity * float(order.price),
                    quantity=order.quantity,
                )
                userdj.capital += order.quantity * float(order.price)
                userdj.save()
                for warehouse_product in warehouse_products:
                    if warehouse_product.quantity >= order.quantity:
                        warehouse_product.quantity -= order.quantity
                        warehouse_product.save()
                        break
                    else:
                        order.quantity -= warehouse_product.quantity
                        warehouse_product.delete()
                order.delete()

    def workshop_update(self, userdj):
        workshops = Workshop.objects.all()
        for workshop in workshops:
            if workshop.recipe:
                recipe_products = RecipeProducts.objects.filter(recipe = workshop.recipe)
                quantity = int(float(workshop.max_capacity) / float(workshop.recipe.finish_product.mass))
                end_of_work = True
                for recipe_product in recipe_products:
                    quantity_recipe_product = recipe_product.quantity * quantity
                    warehouse_products = WarehouseProducts.objects.filter(product = recipe_product.product)
                    supplier_product_price = SupplierProductPrice.objects.filter(product=recipe_product.product).order_by('price').first()
                    sum_warehouse = sum(item['quantity'] for item in warehouse_products.values('quantity'))
                    if sum_warehouse < quantity_recipe_product or supplier_product_price:
                        cheque = Cheque.objects.create(
                            date=userdj.date_now,  
                            customer=None,
                            supplier=supplier_product_price.supplier,
                        )
                        ChequeProduct.objects.create(
                            cheque=cheque,
                            product=recipe_product.product,
                            price=supplier_product_price.price,
                            quantity = quantity - sum_warehouse,
                        )
                        userdj.capital -= (quantity_recipe_product - sum_warehouse) * float(supplier_product_price.price)
                        userdj.save()
                        for i in warehouse_products:
                            i.delete()
                    elif sum_warehouse >= quantity_recipe_product:
                        for warehouse_product in warehouse_products:
                            if warehouse_product.quantity >= quantity_recipe_product:
                                warehouse_product.quantity -= quantity_recipe_product
                                warehouse_product.save()
                            else:
                                quantity_recipe_product -= warehouse_product.quantity
                                warehouse_product.delete()
                    else:
                        end_of_work = False


                if end_of_work:
                    WarehouseProducts.objects.create(
                        product = workshop.recipe.finish_product,
                        quantity = quantity,
                        production_date = userdj.date_now,

                    )
                workshop.recipe = None
                workshop.save()

        order_list = OrderList.objects.all()
        for order, workshop in zip([order for order in order_list if Recipe.objects.get(finish_product=order.product)], workshops):
            workshop.recipe = Recipe.objects.get(finish_product=order.product)
            workshop.save()

    def debiting_update(self, userdj):
        warehouse_products = WarehouseProducts.objects.all()
        for warehouse_product in warehouse_products:
            if warehouse_product.quantity == 0:
                warehouse_products.delete()
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
                    self.debiting_update(userdj)
                    break

                

