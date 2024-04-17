from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    ordering = ('email',)  # Order users by email

admin.site.register(CustomUser, CustomUserAdmin)
from .models import UserProfile, Product, Cart, CartItem, Order, OrderItem

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
