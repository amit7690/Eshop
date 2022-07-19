from ast import Or
from django.urls import path
from  . views import Index,store, Signup, Login, Logout, Cart, OrderView,CheckOut
from .middlewares.auth import auth_middleware

urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('store', store, name='store'),
    path('signup', Signup.as_view(), name='signup'),
    path('login', Login.as_view(), name='login'),
    path('logout', Logout, name='logout'),  
    path('cart', auth_middleware(Cart.as_view()), name='cart'),
    path('order', OrderView.as_view(), name='order'),
    path('check-out', CheckOut.as_view(), name='checkout'),
]