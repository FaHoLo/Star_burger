from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Order, OrderProduct, Product, ProductCategory


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True, write_only=True)

    def validate_products(self, value):
        """Empty list validation."""
        if not value:
            raise ValidationError('Got empty products list.')
        return value

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name']


class ProductSerializer(ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'
