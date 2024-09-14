from django.db import models
from django.core.exceptions import ValidationError


class Userdj(models.Model):
    user_id = models.AutoField(primary_key=True)
    date_now = models.DateField()
    capital = models.FloatField()
    
    objects = models.Manager()
    class Meta:
        db_table = 'userdj'

    def __str__(self):
        return (f"Капитал: {self.capital}, Дата: {self.date_now}")


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return f"Клиент {self.name}"


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'supplier'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_supplier_name')
        ]

    def __str__(self):
        return f"Поставщик {self.name}"


class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=32)
    max_warehouse_capacity = models.IntegerField()

    class Meta:
        db_table = 'warehouse'

    def __str__(self):
        return (f"Склад {self.warehouse_id}: "
                f"Категория: {self.category}, "
                f"Максимальная вместимость: {self.max_warehouse_capacity}")
    
  
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='products')
    expiry_date = models.IntegerField()
    mass = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return (f"Продукт {self.product_id}: "
                f"Название: {self.name}, "
                f"Тип: {self.warehouse.category}, "
                f"Срок годности: {self.expiry_date}, "
                f"Масса: {self.mass:.2f} кг")
    
    def clean(self):
        if self.mass < 0:
            raise ValidationError('Mass cannot be negative.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class DebitingList(models.Model):
    debiting_list_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date_of_debiting = models.DateField()
    fresh = models.BooleanField()

    class Meta:
        db_table = 'debiting_list'

    def __str__(self):
        return (f"Список списания {self.debiting_list_id}: "
                f"Дата: {self.date_of_debiting}, "
                f"Количество: {self.quantity}, "
                f"Свежий: {self.fresh}")

class WarehouseProducts(models.Model):
    warehouse_products_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    production_date = models.DateField()

    class Meta:
        db_table = 'WarehouseProducts'


    def __str__(self):
        return (f"Продукт: {self.product.name}, "
                f"Количество: {self.quantity}, "
                f"Дата производства: {self.production_date}")
    
    def save(self, *args, **kwargs):
        if self.quantity < 0:
            raise ValidationError("Количество не может быть отрицательным.")
        if self.add_cheque():
            raise ValidationError("Такой продукт не продается")
        super().save(*args, **kwargs)

    def add_cheque(self):
        supplier_product_price = SupplierProductPrice.objects.filter(product=self.product).order_by('price').first()
        if supplier_product_price is not None:
            userdj = Userdj.objects.first()
            cheque = Cheque.objects.create(
                date=userdj.date_now,  
                customer=None,
                supplier=supplier_product_price.supplier,
            )
            ChequeProduct.objects.create(
                cheque = cheque,
                product = self.product,
                price = supplier_product_price.price,
                quantity = self.quantity,
            )
            userdj.capital -= float(self.quantity) * float(supplier_product_price.price)
            userdj.save()
            return False
        return True


class SupplierProductPrice(models.Model):
    supplier_product_price_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'supplier_product_price'
        unique_together = ('supplier', 'product')

    def __str__(self):
        return (f"Цена для продукта {self.product.name} от поставшика {self.supplier.name}: "
                f"{self.price:.2f} руб.")
    
    def clean(self):
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')


class Cheque(models.Model):
    cheque_id = models.AutoField(primary_key=True)
    date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'cheque'

    def __str__(self):
        return (f"Чек {self.cheque_id} - Дата: {self.date} - Клиент: {self.customer} - Поставщик: {self.supplier}")
    
class ChequeProduct(models.Model):
    cheque_product_id = models.AutoField(primary_key=True)
    cheque = models.ForeignKey(Cheque, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'cheque_product'
    
    def __str__(self):
        return (f"Продукт: {self.product.name}, "
                f"Цена: {self.price:.2f}, "
                f"Количество: {self.quantity}")
    

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    finish_product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'recipe'
        constraints = [
            models.UniqueConstraint(fields=['finish_product', 'name'], name='unique_recipe_product_recipe_name')
        ]

    def __str__(self):
        return (f"Рецепт {self.recipe_id}: "
                f"Название: {self.name}, "
                f"Готовый продукт: {self.finish_product.name}")



class RecipeProducts(models.Model):
    recipe_products_id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'recipe_products'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'product'], name='unique_recipe_product')
        ]

    def __str__(self):
        return (f"Продукт: {self.product.name}, "
                f"Количество: {self.quantity}")

class Workshop(models.Model):
    workshop_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    max_capacity = models.FloatField()
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'workshop'

    def __str__(self):
        recipe_name = self.recipe.name if self.recipe else "Нет рецепта"
        return (f"Мастерская {self.workshop_id}: "
                f"Название: {self.name}, "
                f"Максимальная вместимость: {self.max_capacity}, "
                f"Рецепт: {recipe_name}")


class OrderList(models.Model):
    order_list_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_order = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_list'


    def __str__(self):
        total_price = self.quantity * self.price
        return (f"Заказ {self.order_list_id}: "
                f"Клиент: {self.customer}, "
                f"Продукт: {self.product.name}, "
                f"По цене: {self.price}, "
                f"Количество: {self.quantity}, "
                f"Дата: {self.date_order}, "
                f"Общая стоимость: {total_price:.2f}")