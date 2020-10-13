from django.db import transaction
from django.templatetags.static import static
from django.http import JsonResponse
from rest_framework.status import HTTP_201_CREATED
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderProduct
from .serializers import OrderSerializer, ProductSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
    )
    order_products = [
        OrderProduct(
            product=product['product'],
            quantity=product['quantity'],
            order=order,
            total_price=product['product'].price * product['quantity'],
        )
        for product in serializer.validated_data['products']
    ]
    OrderProduct.objects.bulk_create(order_products)

    order_serializer = OrderSerializer(order)

    return Response(order_serializer.data, status=HTTP_201_CREATED)
