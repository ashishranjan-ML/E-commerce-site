from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='ShopHome'),
    path('about/', views.about, name='AboutUs'),
    path('contact/', views.contacts, name='ContactUs'),
    path('tracker', views.tracker, name='trackingstatus'),
    path('search/', views.search, name='Search'),
    path('cart/', views.cart, name='Cart'),
    path('productview/<int:myid>', views.prodView, name='Productview'),
    path('checkout', views.checkout, name='CheckoutUs'),
    path('handlerequest/', views.handlerequest, name='HandleRequest'),
]