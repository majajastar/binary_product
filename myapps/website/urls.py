from django.urls import path, include
from django.views.generic import RedirectView
from . import views
 
urlpatterns = [
    # Other URL patterns...
    path('', RedirectView.as_view(url='/about-us', permanent=False), name='home'),
    path('about-us', views.about_us, name='about_us'),
    path('contact-us', views.contact_us, name='contact_us'),
    path('my-orders', views.my_orders, name='my_orders'),
    path('produt-page-default', RedirectView.as_view(url='/product-page/usd-eur/', permanent=False), name='product_page_default'),
    path('product-page/<str:product_type>/', views.product_page, name='product_page'),
    path('get-product-data/<str:product_type>/', views.get_product_data, name='get_product_data'),
    path('get-order-data/<str:product_type>/', views.get_order_data, name='get_order_data'),
]