from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings

from .utils import get_restaurant_distance


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    ingridients = models.CharField('ингредиенты', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderQuerySet(models.QuerySet):
    def all_with_restaurants(self) -> list:
        """Get all orders with restaurant names and distances to them.

        This query use RestaurantMenuItem model as entry point to reduce
        the number of queries.

        Environments:
            GEOCODER_KEY: yandex geocoder api key, docs here:
                https://yandex.ru/dev/maps/geocoder/

        Returns:
            sorted_orders: collected and sorted by id orders with restaurants data
        """
        rest_menu_items = RestaurantMenuItem.objects.select_related('restaurant', 'product') \
            .prefetch_related('product__orderproduct_set__order')

        apikey = settings.GEOCODER_KEY
        orders = set()
        handled_order_products = set()
        for menu_item in rest_menu_items:
            if not menu_item.availability:
                continue
            for order_product in menu_item.product.orderproduct_set.all():
                try:
                    order_product.order.restaurants
                except AttributeError:
                    order_product.order.restaurants = dict()
                    order_product.order.total_price = 0

                orders.add(order_product.order)

                if menu_item.restaurant.name not in order_product.order.restaurants.keys():
                    order_product.order.restaurants[menu_item.restaurant.name] = \
                        get_restaurant_distance(
                            apikey, order_product.order.address,
                            menu_item.restaurant.address)

                if order_product not in handled_order_products:
                    order_product.order.total_price += order_product.total_price
                    handled_order_products.add(order_product)

        sorted_orders = sorted(list(orders), key=lambda order: order.id)
        for order in sorted_orders:
            # order.restaurants is dict of resta_name: distance_to_resta
            order.restaurants = sorted(order.restaurants.items(), key=lambda rest: rest[1])
        return sorted_orders


class Order(models.Model):
    UNPROCESSED = 'UNP'
    DELIVERY = 'DLV'
    DELIVERED = 'DLD'
    STATUS_CHOISES = [
        (UNPROCESSED, 'Необработанный'),
        (DELIVERY, 'Доставка'),
        (DELIVERED, 'Доставлен'),
    ]
    CASH = 'CSH'
    ONLINE = 'ONL'
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Наличными'),
        (ONLINE, 'Онлайн'),
    ]
    firstname = models.CharField('имя', max_length=30)
    lastname = models.CharField('фамилия', max_length=50)
    phonenumber = models.CharField(verbose_name='номер телефона', max_length=20)
    address = models.TextField('адрес доставки')
    status = models.CharField('статус', max_length=3, choices=STATUS_CHOISES, default=UNPROCESSED)
    comment = models.TextField('комментарий', blank=True)
    registered_at = models.DateTimeField('зарегистрирован в', default=timezone.now)
    called_at = models.DateTimeField('звонок совершен в', blank=True, null=True)
    delivered_at = models.DateTimeField('доставлен в', blank=True, null=True)
    payment_method = models.CharField('способ оплаты', max_length=3,
                                      choices=PAYMENT_METHOD_CHOICES, default=CASH)

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, verbose_name='продукт', on_delete=models.CASCADE)
    quantity = models.IntegerField('количество', validators=[MinValueValidator(1)])
    order = models.ForeignKey(Order, verbose_name='заказ', on_delete=models.CASCADE,
                              related_name='products')
    total_price = models.DecimalField('цена', max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'продукт заказа'
        verbose_name_plural = 'продукты заказа'
