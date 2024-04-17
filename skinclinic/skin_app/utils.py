from .models import CartItem

def calculate_total_price(user):
    cart_items = CartItem.objects.filter(cart__user=user)
    total_price = sum(item.product.sale_price * item.quantity for item in cart_items)
    return total_price
