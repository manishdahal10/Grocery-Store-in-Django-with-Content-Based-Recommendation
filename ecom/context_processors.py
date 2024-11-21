from .models import Product

def cart_count(request):
    product_count_in_cart = 0
    
    # Check if the cart cookie exists
    if 'cart' in request.COOKIES:
        cart = request.COOKIES['cart']
        if cart:
            # Split the cart cookie string to get product ids and quantities
            cart_items = cart.split('|')
            product_count_in_cart = len(cart_items)
    
    return {
        'product_count_in_cart': product_count_in_cart,
    }
