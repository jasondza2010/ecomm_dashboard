from django.db import models

# Create your models here.
from django.db import models


class Platform(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

    class Meta:
        app_label = "visualizer"
        db_table = "platform"

    def __str__(self):
        return self.name + " " + str(self.id)


class Product(models.Model):
    id = models.CharField(max_length=16)
    name = models.CharField(max_length=32)
    category = models.CharField(max_length=32)
    platform_id = models.ForeignKey(Platform, on_delete=models.CASCADE)

    class Meta:
        app_label = "visualizer"
        db_table = "product"
        unique_together = ("id", "name", "category", "platform_id")

    def __str__(self):
        return self.name + " " + str(self.platform_id)


class Customer(models.Model):
    id = models.CharField(primary_key=True)
    name = models.CharField(max_length=32)
    contact_email = models.CharField(max_length=255)
    platform_id = models.ForeignKey(Platform, on_delete=models.CASCADE)

    class Meta:
        app_label = "visualizer"
        db_table = "customer"

    def __str__(self):
        return self.name + " " + str(self.platform_id)


class CustomerAddressDetails(models.Model):
    id = models.CharField(primary_key=True)
    street = models.CharField(max_length=32)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.IntegerField()
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        app_label = "visualizer"
        db_table = "customer_address_details"

    def __str__(self):
        return (
            self.street + " " + self.city + " " + self.state + " " + str(self.pincode)
        )


class Order(models.Model):
    id = models.CharField(primary_key=True)
    date_of_sale = models.DateField()
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_address_details_id = models.ForeignKey(
        CustomerAddressDetails, on_delete=models.CASCADE
    )
    platform_id = models.ForeignKey(Platform, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    delivery_status = models.CharField(max_length=31)
    meta_data = models.JSONField()

    class Meta:
        app_label = "visualizer"
        db_table = "orders"

    def __str__(self):
        return (
            str(self.id)
            + " "
            + str(self.customer_id)
            + " "
            + str(self.customer_address_details_id)
            + " "
            + str(self.platform_id)
            + " "
            + str(self.delivery_date)
            + " "
            + str(self.delivery_status)
            + " "
            + str(self.meta_data)
        )


class OrderDetails(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    selling_price = models.FloatField()

    class Meta:
        app_label = "visualizer"
        db_table = "order_details"

    def __str__(self):
        return str(self.order_id) + " " + str(self.product_id)
