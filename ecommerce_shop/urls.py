"""ecommerce_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from shop import views

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.home_page),
    path('about', views.about_page),
    path('contacts', views.contacts_page),
    path('service', views.service_page),
    path('products', views.ProductsPage.as_view()),
    path('cart', login_required(views.CartPageView.as_view(), login_url='/login')),
    path('checkout', views.CheckoutPage.as_view()),
    path('wishlist', views.wishlist_page),
    path('register', views.register_page),
    path('login', views.login_page),
    path('products/<slug>', views.ProductDetail.as_view(), name='product'),
    path('add-to-cart/<slug>', views.add_to_cart),
    path('remove-from-cart/<slug>', views.remove_from_cart),
    path('complete-order', views.PaymentView.as_view()),
    path('logout', views.logout_view),
    path('my-account', views.AccountPage.as_view()),
    path('my-account/<str:user_page>', views.AccountOrdersPage.as_view()),
    path('my-account/order-details/<int:order_id>', views.AccountOrdersDetails.as_view())
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)