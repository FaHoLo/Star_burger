from django.templatetags.static import static
from django.http import JsonResponse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderProduct
from .serializers import OrderSerializer


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


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'ingridients': product.ingridients,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    required_fields = ['firstname', 'lastname', 'phonenumber', 'address']
    for field_name in required_fields:
        field_value = serializer.data.get(field_name)
        if not field_value:
            return Response({'Error': f'Field {field_name} can\'t be null.'},
                            status=HTTP_400_BAD_REQUEST)
        elif not isinstance(field_value, str):
            return Response({'Error': f'Field {field_name} must be string.'},
                            status=HTTP_400_BAD_REQUEST)

    products = serializer.data.get('products')
    if not products:
        return Response({'Error': 'Field products can\'t be null.'}, status=HTTP_400_BAD_REQUEST)
    if not isinstance(products, list):
        return Response({'Error': 'Wrong products type, list expected.'},
                        status=HTTP_400_BAD_REQUEST)

    for product_data in products:
        try:
            Product.objects.get(pk=product_data['product'])
        except Product.DoesNotExist:
            return Response({'Error': f'No such product: {product_data["product"]}'},
                            status=HTTP_404_NOT_FOUND)

    order = Order.objects.create(
        firstname=serializer.data['firstname'],
        lastname=serializer.data['lastname'],
        phonenumber=serializer.data['phonenumber'],
        address=serializer.data['address']
    )
    order_products = [
        OrderProduct(
            product=Product.objects.get(pk=product['product']),
            quantity=product['quantity'],
            order=order,
        )
        for product in serializer.data['products']
    ]
    OrderProduct.objects.bulk_create(order_products)

    return Response(serializer.data, status=HTTP_201_CREATED)
