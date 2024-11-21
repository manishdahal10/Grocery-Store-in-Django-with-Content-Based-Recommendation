from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings



# Home view 
def home_view(request):
    categories = models.Category.objects.all()
    products = models.Product.objects.all()
    top_search_products = models.Product.objects.filter(search_count__gt=0).order_by('-search_count')[:5]

    # Fetch cart count from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')

    return render(request, 'ecom/index.html', {
        'categories': categories,
        'products': products,
        'top_search_products': top_search_products,
    })
  
    
# --------------------About us---------
def aboutus_view(request):
    return render(request,'ecom/aboutus.html')



#-------------------------Signup---------------------------------
def customer_signup_view(request):
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)

        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            
            my_customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group.user_set.add(user)

            # Set a success message
            request.session['success_message'] = 'User created successfully. Please login.'
            return redirect('success')  # Redirect to success page

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        userForm = forms.CustomerUserForm()
        customerForm = forms.CustomerForm()

    return render(request, 'ecom/customersignup.html', {
        'userForm': userForm,
        'customerForm': customerForm
    })

def success_page(request):
    message = request.session.pop('success_message', None)
    return render(request, 'ecom/success.html', {'message': message})  

            
# Utility function to check if a user is a customer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()




#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # For cards on dashboard
    customercount = models.Customer.objects.count()
    productcount = models.Product.objects.count()

      # Exclude 'Delivered' orders from the order count
    ordercount = models.Orders.objects.exclude(status='Delivered').count()
   

     

    # For recent orders, ordered by date descending
    orders = models.Orders.objects.all().order_by('-order_date')
    order_items_list = []

    # Exclude 'Delivered' orders
    orders = models.Orders.objects.exclude(status='Delivered')

    for order in orders:
        # Get all order items for each order
        order_items = order.order_items.all()
        # Add to list as tuple of (order_items, customer, order)
        order_items_list.append((order_items, order.customer, order))

    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': ordercount,
        'data': order_items_list,
    }
    
    return render(request, 'ecom/admin_dashboard.html', context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')



@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)

    if request.method == 'POST':
        # Initialize forms with POST data and files
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        
        # Check if forms are valid
        if userForm.is_valid() and customerForm.is_valid():
            # Save the user form without committing to database
            user = userForm.save(commit=False)

            # Check if the password field is provided
            new_password = userForm.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)
            
            # Save the user instance with updated password if any
            user.save()

            # Save the customer form
            customerForm.save()

            return redirect('view-customer')
    else:
        # Initialize forms with existing instance data for GET request
        userForm = forms.CustomerUserForm(instance=user)
        customerForm = forms.CustomerForm(instance=customer)

    return render(request, 'ecom/admin_update_customer.html', {
        'userForm': userForm,
        'customerForm': customerForm,
    })

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Orders, OrderItem  # Ensure OrderItem is imported
@login_required(login_url='adminlogin')
def admin_history_view(request):
    # Fetch only orders with status 'Delivered'
    delivered_orders = Orders.objects.filter(status='Delivered')

    data = []
    for order in delivered_orders:
        # Fetch all items related to this order
        order_items = OrderItem.objects.filter(order=order)
        customer = order.customer.user.username  # Assuming there's a relation to Customer and User
        data.append((order_items, customer, order))

    return render(request, 'ecom/admin_history.html', {'data': data})



@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    # Fetch all orders
    orders = models.Orders.objects.all()

     # Exclude 'Delivered' orders
    orders = models.Orders.objects.exclude(status='Delivered')
    
    # Fetch related ordered products and customers
    ordered_products = []
    ordered_bys = []
    
    for order in orders:
        # Fetch related products for each order
        order_items = order.order_items.all()  # Using related_name 'order_items'
        for order_item in order_items:
            ordered_products.append(order_item.product)
            ordered_bys.append(order.customer)  # Only need to add the customer once

    # Create a context dictionary
    context = {
        'orders': orders,
        'ordered_products': ordered_products,
        'ordered_bys': ordered_bys
    }
    
    return render(request, 'ecom/admin_view_booking.html', context)

@login_required(login_url='adminlogin')
def delete_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

@login_required(login_url='adminlogin')
def update_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    orderForm = forms.OrderForm(instance=order)
    if request.method == 'POST':
        orderForm = forms.OrderForm(request.POST, instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request, 'ecom/update_order.html', {'orderForm': orderForm})


def search_view(request):
    query = request.GET.get('query')
    if query:
        products = Product.objects.filter(name__icontains=query)  # Filter products by name
    else:
        products = Product.objects.none()  # Return an empty queryset if no query

    context = {
        'products': products,
        'query': query,
    }
     # Update search count for the products found
    for product in products:
        product.search_count += 1
        product.save()
    return render(request, 'ecom/search_results.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Product
from django.http import HttpResponseRedirect

def add_to_cart_view(request, pk):
    # Fetch all products
    products = Product.objects.all()

    # Get the quantity from the form (defaults to 1)
    quantity = int(request.POST.get('quantity', 1))

    # Fetch the current cart from cookies
    cart = request.COOKIES.get('cart', '')
    product_list = cart.split('|') if cart else []

    # Check if the product is already in the cart
    product_in_cart = False
    updated_product_list = []
    
    for item in product_list:
        if item:
            product_id, old_quantity = item.split(',')
            if int(product_id) == pk:
                product_in_cart = True
            updated_product_list.append(item)

    if not product_in_cart:
        # Add product with the specified quantity if not already in the cart
        updated_product_list.append(f"{pk},{quantity}")

    # Set updated cart in cookies
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('cart', '|'.join(updated_product_list))
    
    # Success message
    product = get_object_or_404(Product, id=pk)
    if product_in_cart:
        messages.info(request, f"Product already in cart!")
    else:
        messages.info(request, f"{quantity} of {product.name} added to cart successfully!")
    
    return response



# for checkout of cart
def cart_view(request):
    # Initialize variables
    products = []
    total = 0
    product_count_in_cart = 0
    
    # Check if the cart cookie exists
    if 'cart' in request.COOKIES:
        cart = request.COOKIES['cart']
        if cart:
            # Split the cart cookie string to get product ids and quantities
            cart_items = cart.split('|')
            
            # Loop through each item in the cart
            for item in cart_items:
                product_id, quantity = item.split(',')
                quantity = int(quantity)
                
                # Fetch the product from the database
                product = models.Product.objects.get(id=product_id)
                
                # Calculate total price for this product
                total_price = product.price * quantity

                # Add the product, its quantity, and total price to the products list
                products.append({'product': product, 'quantity': quantity, 'total_price': total_price})
                
                # Add to the overall total price
                total += total_price

            # Calculate product count in the cart
            product_count_in_cart = len(cart_items)

    return render(request, 'ecom/cart.html', {
        'products': products,
        'total': total,
        'product_count_in_cart': product_count_in_cart
    })

from django.http import JsonResponse
from django.contrib import messages

def clear_cart(request):
    # Clear the cart cookie by setting it to an empty string
    response = JsonResponse({'message': 'Cart has been cleared successfully!'})
    
    # Set the 'cart' cookie to an empty value and expire it
    response.delete_cookie('cart')
    
    
    return response


from django.http import JsonResponse

def update_cart_quantity_view(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        
        if 'cart' in request.COOKIES:
            cart = request.COOKIES['cart']
            cart_items = cart.split('|')
            updated_cart_items = []
            
            for item in cart_items:
                item_id, item_quantity = item.split(',')
                
                if int(item_id) == int(product_id):
                    updated_cart_items.append(f"{item_id},{quantity}")  # Update the quantity
                else:
                    updated_cart_items.append(item)
            
            response = JsonResponse({'status': 'success'})
            response.set_cookie('cart', '|'.join(updated_cart_items))
            return response
        
    return JsonResponse({'status': 'error'}, status=400)



def remove_from_cart_view(request, pk):
    products = []
    total = 0

    # Check if the cart cookie exists
    if 'cart' in request.COOKIES:
        cart = request.COOKIES['cart']
        cart_items = cart.split('|')
        updated_cart_items = []

        for item in cart_items:
            product_id, quantity = item.split(',')
            if int(product_id) == pk:
                continue  # Skip the product to remove
            updated_cart_items.append(item)

            # Fetch the remaining products from the database
            product = models.Product.objects.get(id=product_id)
            quantity = int(quantity)

            # Add the remaining product to the products list
            products.append({'product': product, 'quantity': quantity})

            # Update the total price (price * quantity)
            total += product.price * quantity

    # Create the response to render the cart
    response = render(request, 'ecom/cart.html', {
        'products': products,
        'total': total
    })

    # Update the cart cookie
    if updated_cart_items:
        response.set_cookie('cart', '|'.join(updated_cart_items))
    else:
        response.delete_cookie('cart')

    return response


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    categories = models.Category.objects.all()
    products = models.Product.objects.all()
    top_search_products = models.Product.objects.filter(search_count__gt=0).order_by('-search_count')[:5]

     # Fetch cart count from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        print("Product IDs from cookies:", product_ids)  # Debug line
        counter = product_ids.split('|')
        product_count_in_cart = len(counter)
        print("Product count in cart:", product_count_in_cart)  # Debug line
    else:
        product_count_in_cart = 0
       

    return render(request, 'ecom/customer_home.html', {
        'categories': categories,
        'products': products,
        # 'product_count_in_cart': product_count_in_cart,
        'top_search_products': top_search_products,
    })




from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Customer, Orders, Product

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
@login_required(login_url='customerlogin')  
def my_order_view(request):
    # Get the customer associated with the logged-in user
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return render(request, 'ecom/my_order.html', {'error': 'Customer not found.'})

    # Fetch all orders for the customer, including delivered and pending orders
    orders = Orders.objects.filter(customer=customer).order_by('-order_date')

    # Prepare order details, including order items and their details
    order_details = []
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        order_details.append({
            'order': order,
            'order_items': order_items,
        })

    return render(request, 'ecom/my_order.html', {'order_details': order_details})






@login_required(login_url='customerlogin')
def customer_address_view(request):
    product_in_cart = False
    if 'cart' in request.COOKIES:
        cart = request.COOKIES['cart']
        if cart != "":
            product_in_cart = True
            product_count_in_cart = len(cart.split('|'))
        else:
            product_count_in_cart = 0
    else:
        product_count_in_cart = 0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']

            total = 0
            if 'cart' in request.COOKIES:
                cart = request.COOKIES['cart']
                if cart != "":
                    cart_items = cart.split('|')
                    product_ids_quantities = [item.split(',') for item in cart_items]
                    product_ids = [item[0] for item in product_ids_quantities]
                    quantities = [int(item[1]) for item in product_ids_quantities]

                    products = models.Product.objects.filter(id__in=product_ids)
                    for product in products:
                        quantity = quantities[product_ids.index(str(product.id))]
                        total += product.price * quantity

            response = render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response

    return render(request, 'ecom/customer_address.html', {
        'addressForm': addressForm,
        'product_in_cart': product_in_cart,
        'product_count_in_cart': product_count_in_cart
    })
 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='customerlogin')
def payment_success_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    products = []
    quantities = []
    email = request.COOKIES.get('email', None)
    mobile = request.COOKIES.get('mobile', None)
    address = request.COOKIES.get('address', None)

    if 'cart' in request.COOKIES:
        cart = request.COOKIES['cart']
        if cart:
            cart_items = cart.split('|')
            product_ids_quantities = [item.split(',') for item in cart_items]
            product_ids = [item[0] for item in product_ids_quantities]
            quantities = [int(item[1]) for item in product_ids_quantities]

            products = models.Product.objects.filter(id__in=product_ids)

            # Create an order
            order = models.Orders.objects.create(
                customer=customer,
                email=email,
                mobile=mobile,
                address=address,
                total_amount=sum(
                    product.price * quantities[product_ids.index(str(product.id))]
                    for product in products
                ),
                status='Pending'
            )

            # Create OrderItems for the order
            for product in products:
                quantity = quantities[product_ids.index(str(product.id))]
                models.OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )

    # Clear cookies
    response = render(request, 'ecom/payment_success.html', {'order': order})
    response.delete_cookie('cart')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')

    return response



@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer
from .forms import CustomerUserForm, CustomerForm
from django.contrib.auth import authenticate, login
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = CustomerUserForm(request.POST, instance=request.user)
        customer_form = CustomerForm(request.POST, request.FILES, instance=request.user.customer)

        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)

            # Handle password change
            new_password = user_form.cleaned_data.get('password')
            if new_password:
                # Set the new password securely
                user.set_password(new_password)

            # Save the user object after setting the password
            user.save()
            customer_form.save()

            # Re-authenticate and log the user back in after password change
            if new_password:
                user = authenticate(username=user.username, password=new_password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Your profile and password have been updated successfully.')
                else:
                    messages.error(request, 'Password update failed. Please try again.')
                    return redirect('edit-profile')
            else:
                messages.success(request, 'Your profile has been updated successfully.')

            return redirect('my-profile')
    else:
        user_form = CustomerUserForm(instance=request.user)
        customer_form = CustomerForm(instance=request.user.customer)

    return render(request, 'ecom/edit_profile.html', {
        'userForm': user_form,
        'customerForm': customer_form
    })

#-------------------------Admin -------------------------------------------

def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')




from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def category_view(request, category_name):
    # Fetch the category object
    category = get_object_or_404(Category, name=category_name)
    # Fetch products belonging to this category
    products = Product.objects.filter(category=category)

    context = {
        'category': category,
        'products': products,
        'categories': Category.objects.all()
    }

    # Render the template with category and products
    return render(request, 'ecom/category.html', context)


# Recommendation
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
import numpy as np
import pickle
from .models import Product, Category
def load_data():
    global similarity_matrix, products
    try:
        similarity_matrix = np.load('similarity_matrix.npy')
        print("Similarity matrix loaded successfully.")
    except Exception as e:
        print(f"Error loading similarity matrix: {e}")

    try:
        with open('products.pkl', 'rb') as f:
            products = pickle.load(f)
        print("Products data loaded successfully.")
    except Exception as e:
        print(f"Error loading products data: {e}")

load_data()

def get_product_index(class_id):
    try:
        return next((index for (index, d) in enumerate(products) if d['label'] == class_id), None)
    except Exception as e:
        print(f"Error finding product index: {e}")
        return None


def recommend_products(product_index, top_n=5):
    if product_index is not None:
        try:
            similar_indices = similarity_matrix[product_index].argsort()[-top_n:][::-1]
            print(f"Recommended indices: {similar_indices}")
            return similar_indices
        except Exception as e:
            print(f"Error recommending products: {e}")
            return []
    else:
        print("Product index not found.")
        return []

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    
    product_index = get_product_index(product.class_id)
    
    if product_index is not None:
        recommended_indices = recommend_products(product_index)
        
        recommended_products = []
        for index in recommended_indices:
            try:
                recommended_product = Product.objects.get(class_id=products[index]['label'])
                recommended_products.append(recommended_product)
            except Product.DoesNotExist:
                print(f"Product with class_id {products[index]['label']} does not exist.")
    else:
        recommended_products = []

    context = {
        'product': product,
        'recommended_products': recommended_products,
    }
    return render(request, 'product_detail.html', context)