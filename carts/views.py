from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    
    if request.method == "POST":
        # Get color and size from POST data
        color = request.POST.get('color')
        size = request.POST.get('size')
        
        try:
            # Get color variation
            if color:
                color_variation = variation.objects.get(
                    product=product,
                    variation_category__iexact='color',
                    variation_value__iexact=color
                )
                product_variation.append(color_variation)
            
            # Get size variation
            if size:
                size_variation = variation.objects.get(
                    product=product,
                    variation_category__iexact='size',
                    variation_value__iexact=size
                )
                product_variation.append(size_variation)
        except variation.DoesNotExist:
            pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    
    # Get the first cart item for this product
    cart_item = CartItem.objects.filter(product=product, cart=cart).first()
    
    if cart_item:
        # If cart item exists, increment its quantity
        cart_item.quantity += 1
        cart_item.save()
    else:
        # If no cart item exists, create a new one
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if len(product_variation) > 0:
            for item in product_variation:
                cart_item.variations.add(item)
        cart_item.save()
    
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.filter(product=product, cart=cart).first()
        if cart_item:
            cart_item.delete()
    except Exception as e:
        print(f"Error removing cart item: {e}")
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total)/100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, "store/cart.html", context)