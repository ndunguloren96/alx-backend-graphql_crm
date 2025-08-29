import graphene
from graphene_django import DjangoObjectType
from core import models as core_models
from django.db import transaction
from datetime import datetime
from crm.models import Product

class CustomerType(DjangoObjectType):
    class Meta:
        model = core_models.Customer
        fields = ("id", "email", "created_at")

class ProductType(DjangoObjectType):
    class Meta:
        model = core_models.Product
        fields = ("id", "name", "stock")
        
class OrderType(DjangoObjectType):
    class Meta:
        model = core_models.Order
        fields = ("id", "order_date", "customer", "product")

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    @staticmethod
    def mutate(root, info):
        log_path = '/tmp/low_stock_updates_log.txt'
        updated_products_list = []
        
        with transaction.atomic():
            low_stock_products = core_models.Product.objects.filter(stock__lt=10)
            
            if not low_stock_products.exists():
                message = "No low-stock products to update."
                with open(log_path, 'a') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp}: {message}\n")
                return UpdateLowStockProducts(success=True, message=message, updated_products=[])

            for product in low_stock_products:
                product.stock += 10
                product.save()
                updated_products_list.append(product)
                
            message = f"Successfully updated stock for {len(updated_products_list)} products."
            
            with open(log_path, 'a') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp}: {message}\n")
                for product in updated_products_list:
                    f.write(f"  - Updated product: {product.name}, new stock: {product.stock}\n")

        return UpdateLowStockProducts(success=True, message=message, updated_products=updated_products_list)

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="World"))
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)
    
    def resolve_hello(self, info, name):
        return f'Hello, {name}! GraphQL is working.'
    
    def resolve_all_products(self, info):
        return core_models.Product.objects.all()

    def resolve_all_orders(self, info):
        return core_models.Order.objects.all()

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
