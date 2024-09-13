from django.db import models
from django.core.exceptions import ValidationError


class Userdj(models.Model):
    user_id = models.AutoField(primary_key=True)
    date_now = models.DateField()
    capital = models.FloatField()
    
    objects = models.Manager()
    class Meta:
        db_table = 'userdj'


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return f"Customer {self.name}"


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'supplier'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_supplier_name')
        ]

    def __str__(self):
        return f"Supplier {self.name}"


class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=32)
    max_warehouse_capacity = models.IntegerField()

    class Meta:
        db_table = 'warehouse'

    def __str__(self):
        return f"Warehouse {self.warehouse_id}: Category: {self.category}, Max Capacity: {self.max_warehouse_capacity}"
    
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='products')
    expiry_date = models.IntegerField()
    mass = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return f"Product {self.product_id}: {self.name}"

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
        return f"Debiting List {self.debiting_list_id}: Date: {self.date_of_debiting}, Fresh: {self.fresh}"


class WarehouseProducts(models.Model):
    warehouse_products_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    production_date = models.DateField()

    class Meta:
        db_table = 'WarehouseProducts'


    def __str__(self):
        return f"Warehouse Product {self.warehouse_products_id}: Product: {self.product}, Quantity: {self.quantity}, Production Date: {self.production_date}, Debiting List: {self.debiting_list}"

class CustomerProductPrice(models.Model):
    customer_product_price_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('customer', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'customer_product_price'
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"Price for {self.product} for {self.customer}: {self.price}"

    def clean(self):
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Cheque(models.Model):
    cheque_id = models.AutoField(primary_key=True)
    date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'cheque'

    def __str__(self):
        return f"Cheque {self.cheque_id} - Date: {self.date} - Customer: {self.customer} - Supplier: {self.supplier}"

class ChequeProduct(models.Model):
    cheque_product_id = models.AutoField(primary_key=True)
    cheque_reference = models.ForeignKey(Cheque, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'cheque_product'


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
        return f"Recipe {self.recipe_id}: Name: {self.name}, Finish Product: {self.finish_product}"

    def clean(self):
        if not self.name:
            raise ValidationError('Name cannot be empty.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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
        return f"Recipe Product {self.recipe_products_id}: Recipe: {self.recipe}, Product: {self.product}, Quantity: {self.quantity}"


class Workshop(models.Model):
    workshop_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    max_capacity = models.FloatField()
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'workshop'

    def __str__(self):
        return f"Workshop {self.workshop_id}: {self.name} (Max Capacity: {self.max_capacity}, Recipe: {self.recipe})"


class OrderList(models.Model):
    order_list_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_order = models.DateField()

    class Meta:
        db_table = 'order_list'

    def __str__(self):
        return f"Order {self.order_list_id}: Customer: {self.customer}, Product: {self.product}, Quantity: {self.quantity}, Date: {self.date_order}"

