from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import reverse, redirect

from .models import (Restaurant, Product, RestaurantMenuItem, ProductCategory,
                     Order, OrderProduct)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly,
        # so search will be buggy. Migration to PostgreSQL is necessary
        'name',
        'category',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'ingridients',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                "admin/foodcartapp.css",
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" height="200"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" height="50"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class CategoryAdmin(admin.ModelAdmin):
    pass


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'first_name',
        'last_name',
        'address',
        'phone_number',
    ]
    inlines = [
        OrderProductInline
    ]

    def response_change(self, request, obj):
        if 'next' in request.GET:
            # Security check, details in comments here: https://stackoverflow.com/a/12282414
            if url_has_allowed_host_and_scheme(request.GET['next'], settings.ALLOWED_HOSTS):
                return redirect(request.GET['next'])
            else:
                return redirect('/')
        else:
            return super(OrderAdmin, self).response_change(request, obj)
