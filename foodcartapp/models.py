from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


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


class Order(models.Model):
    UNPROCESSED = 'UNP'
    DELIVERY = 'DLV'
    DELIVERED = 'DLD'
    STATUS_CHOISES = [
        (UNPROCESSED, 'Необработанный'),
        (DELIVERY, 'Доставка'),
        (DELIVERED, 'Доставлен'),
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
