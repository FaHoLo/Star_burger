from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Order, OrderProduct


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
