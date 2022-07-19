from distutils.command import check
from django import views
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from django.views import View
from store.models import Category, Customer, Products, Order
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password



class Index(View):
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        request.session['cart'] = cart
        
        return redirect('homepage')
  
    def get(self, request):
        print('###########', request.get_full_path())
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')
  
  
def store(request):
    cart = request.session.get('cart')
    
    if not cart:
        request.session['cart'] = {}
    
    products = None
    categories = Category.get_all_categories()
    
    categoryID = request.GET.get('category')
    if categoryID:
        products = Products.get_all_products_by_categoryid(categoryID)
    else:
        products = Products.get_all_products()
  
    data = {}
    data['products'] = products
    data['categories'] = categories
    data['cart'] = cart
    print('you are : ', request.session.get('email'))
    print('****cart****', cart)
    return render(request, 'estore/index.html', data)


class Login(View):
   return_url = None

   def get(self, request):
        Login.return_url = request.GET.get('return_url')
        print('&&&&&&&&&&&&&', Login.return_url)
        return render(request, 'estore/login.html')

   def post(self, request):
       email = request.POST.get('email')
       password = request.POST.get('password')
       customer = Customer.get_customer_by_email(email)
       error_message = None
       request.session['customer'] = customer.id
       print(request.session['customer'] , '************')
       if customer:
           flag = check_password(password, customer.password)
           request.session['email'] = customer.email
           request.session['customer_name'] = customer.first_name + ' ' + customer.last_name
           print('----session.-->>', request.session['email'])
           print('session customer name -----------', request.session['customer_name'])
           print('--------flag-----------', flag)
           if flag:
               request.session['customer'] = customer.id
               print(request.session['customer'], '#################')
               if Login.return_url:
                   print('login.return_url------->>>>', Login.return_url)
                   return HttpResponseRedirect(Login.return_url)
               else:
                   print('eTTTTTTTTTTTTTTTT')
                   Login.return_url = None
                   return redirect('homepage')
           else:
               error_message = 'Invalid !!'
       else:
           error_message = 'Invalid !!'
        
        
       print(email, password)
       return render(request, 'estore/login.html', {'error':error_message })


def Logout(request):
    request.session.clear()
    return redirect('login')



class Signup(View):
    def get(self, request):
        return render(request, 'estore/signup.html')

    def post(self, request):
        postData = request.POST
        first_name = postData.get('first_name')
        last_name = postData.get('last_name')
        phone = postData.get('phone')
        email =  postData.get('email')
        password = postData.get('password')

        value = {
            'first_name': first_name,
            'last_name' : last_name,
            'phone': phone,
            'email': email,
        }

        error_message = None
        customer = Customer(first_name=first_name, last_name=last_name, phone=phone, email=email, password=password)
        request.session['email'] = customer.email
        request.session['customer_name'] = customer.first_name + ' ' + customer.last_name
        print("request.session['customer_name']---------->>>", request.session['customer_name']) 
        error_message = self.validateCustomer(customer)

        if (not error_message):
            print (first_name, last_name, phone, email, password)
            customer.password = make_password (customer.password)
            customer.register()
            # return HttpResponse('Customer details successfully submitted')
            return redirect('homepage')
        else:
            data = {
                'error': error_message,
                'values': value
            }
        return render(request, 'estore/signup.html', data)
        
    def validateCustomer(self, customer):
        error_message = None
        if (not customer.first_name):
            error_message = "Please Enter your First Name !!"
        elif len (customer.first_name) < 3:
            error_message = 'First Name must be 3 char long or more'
        elif not customer.last_name:
            error_message = 'Please Enter your Last Name'
        elif len (customer.last_name) < 3:
            error_message = 'Last Name must be 3 char long or more'
        elif not customer.phone:
            error_message = 'Enter your Phone Number'
        elif len (customer.phone) < 10:
            error_message = 'Phone Number must be 10 char Long'
        elif len (customer.password) < 5:
            error_message = 'Password must be 5 char long'
        elif len (customer.email) < 5:
            error_message = 'Email must be 5 char long'
        elif customer.isExists ():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message


# --------------Checkout----------

class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Products.get_products_by_id(list(cart.keys()))
        print(address, phone, customer, cart, products)
  
        for product in products:
            print(cart.get(str(product.id)))
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart'] = {}
  
        return redirect('cart')


# ------------OrderView-------------


class OrderView(View):
    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print('orders ------------ ', orders)
        return render(request, 'estore/orders.html', {'orders': orders})


class Cart(View):
    def get(self , request):
        ids = list(request.session.get('cart').keys())
        products = Products.get_products_by_id(ids)
        print('####### cart ########', products)
        return render(request , 'estore/cart.html' , {'products' : products} )




class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Products.get_products_by_id(list(cart.keys()))
        print(address, phone, customer, cart, products)
  
        for product in products:
            print(cart.get(str(product.id)))
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart'] = {}
  
        return redirect('cart')