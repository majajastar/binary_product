from django.urls import path, include
from django.views.generic import RedirectView
from . import views
 
urlpatterns = [
    # Other URL patterns...
    path('', RedirectView.as_view(url='/product-page/productA/', permanent=False), name='home'),
    path('product-page/<str:product_type>/', views.product_page, name='product_page'),
    path('get-product-data/<str:product_type>/', views.get_product_data, name='get_product_data'),
    path('get-order-data/<str:product_type>/', views.get_order_data, name='get_order_data'),
]