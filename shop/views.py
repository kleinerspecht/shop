import slug as slug
import stripe
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from ecommerce_shop import settings
from .forms import PaymentForm, BillingForm
from .models import CreateUser, Categories, Item, OrderItem, Order, PaymentModel, PaidOrders
from django.contrib import messages
from . import forms
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.

def home_page(request):
    return render(request, 'index.html')


def about_page(request):
    return render(request, 'about.html')


def contacts_page(request):
    return render(request, 'contact-us.html')


def service_page(request):
    return render(request, 'service.html')


def wishlist_page(request):
    return render(request, 'wishlist.html')

class AccountPage(View):
    template_name = 'my-account.html'

    def get(self, request):
        return render(request, self.template_name)

class AccountOrdersPage(View):

    def get(self, request, user_page):
        user_orders = Order.objects.filter(user=request.user, confirmed=True)
        if user_page == 'my-orders':
            return render(request, 'my-orders.html',  {'orders': user_orders})


class ProductsPage(ListView):
    model = Item
    products_cat = Categories.objects.annotate(prod_num=Count('item'))
    template_name = 'shop.html'



class ProductDetail(DetailView):
    model = Item
    template_name = 'shop-detail.html'


@login_required(login_url='/login', redirect_field_name='next')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, confirmed=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item_qs = order.items.filter(item__slug=item.slug)
        if order_item_qs.exists():
            order_item = order_item_qs[0]
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(item=item)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order_item = OrderItem.objects.create(item=item)
    order.items.add(order_item)
    return redirect('/cart')


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, confirmed=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item_qs = order.items.filter(item__slug=item.slug)
        if order_item_qs.exists():
            order_item = OrderItem.objects.filter(
                item=item,
                confirmed=False
            )[0]
            order_item.delete()
        else:
            return redirect('/cart')
    else:
        return redirect('/cart')
    return redirect('/cart')

class CartPageView(View):
    template_name = 'cart.html'

    def get(self, request):
        self.model = Order.objects.filter(user=request.user, confirmed=False)
        if self.model.exists():
            order_model = self.model[0]
            order_items = order_model.items.all()
            if order_items.exists():
                return render(request, self.template_name, {'cart_items': order_items, 'order': order_model})
            else:
                return HttpResponse('Cart is empty!')
        else:
            return HttpResponse('Cart is empty!')

    def post(self, request):
        self.model = Order.objects.filter(user=request.user, confirmed=False)
        if self.model.exists():
            order_model = self.model[0]
            order_items = order_model.items.all()
            post_qty_qry = [item.item.slug for item in order_items]
            for slug in post_qty_qry:
                new_qty = self.request.POST.get(f'qty-{slug}')
                item = order_model.items.filter(item__slug=slug)[0]
                item.quantity = new_qty
                item.save()
                order_items = order_model.items.all()
        return render(request, self.template_name, {'cart_items': order_items, 'order': order_model})


class CheckoutPage(View):
    template_name = 'checkout.html'

    def get(self, request):
        self.model = Order.objects.filter(user=request.user, confirmed=False)
        if self.model.exists():
            order_model = self.model[0]
            order_items = order_model.items.all()
            if order_items.exists():
                form = PaymentForm()
                return render(request, self.template_name,
                              {'cart_items': order_items, 'order': order_model, 'form': form})
        else:
            return HttpResponse('There is no cart/order that we can proceed with processing!')

    def post(self, request):
        form = PaymentForm(self.request.POST or None)
        self.model = Order.objects.filter(user=request.user, confirmed=False)
        if self.model.exists():
            order_model = self.model[0]
        if form.is_valid() and order_model:
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            street_address = form.cleaned_data.get('street_address')
            street_address_2 = form.cleaned_data.get('street_address_2')
            country = form.cleaned_data.get('country')
            zip = form.cleaned_data.get('zip')
            payment_type_chosen = form.cleaned_data.get('payment_option')
            payment_form = PaymentModel(
                user=self.request.user,
                first_name=first_name,
                last_name=last_name,
                street_address=street_address,
                street_address_2=street_address_2,
                country=country,
                zip=zip
            )
            order_model.billing_address = payment_form
            order_model.delivery_status = 'Order confirmed!'
            payment_form.save()
            order_model.save()
            print(payment_type_chosen)
            if payment_type_chosen == 'S':
                return redirect('/complete-order')

            return redirect('/checkout')


class PaymentView(View):
    template_name = 'payment.html'

    def get(self, request):
        self.model = Order.objects.filter(user=request.user, confirmed=False)
        if self.model.exists():
            order_model = self.model[0]
            order_items = order_model.items.all()
            if order_items.exists():
                form = BillingForm()
                return render(request, self.template_name,
                              {'cart_items': order_items, 'order': order_model, 'form': form})

    def post(self, request):
        order = Order.objects.get(user=request.user, confirmed=False)
        token = self.request.POST.get('stripeToken')
        amount = 56 * 100 #price is in cents.

        try:
            charge = stripe.PaymentIntent.create(
                amount=amount,
                currency="bgn",
                confirmation_method="manual",
                confirm="True",
                capture_method="automatic",
                payment_method_data=dict(
                    type="card",
                    card=dict(
                        token=token
                    )
                )
            )

        except stripe.error.CardError as e:
            messages.error(self.request, f'{e.code}')
        except stripe.error.RateLimitError as e:
            messages.error(self.request, f'{e.code}')
        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, f'{e.code}')
        except stripe.error.AuthenticationError as e:
            messages.error(self.request, f'{e.code}')
        except stripe.error.APIConnectionError as e:
            messages.error(self.request, f'{e.code}')
        except stripe.error.StripeError as e:
            messages.error(self.request, f'{e.code}')
        except Exception as e:
            print('I fucked up the code...')

        # fill the payment model with the info from stripe/payment
        payment = PaidOrders()
        payment.stripe_charge_id = charge['id']
        payment.user = self.request.user
        payment.amount = order.tax_total_price
        payment.save()

        # populate order info
        order.confirmed = True
        order.payment = payment
        order.save()
        return redirect('/products')


def register_page(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            form.save()
            return redirect(ProductsPage)
        else:
            user_message = f"{form.error_messages}"
            if 'password_mismatch' in user_message:
                messages.error(request,
                               'Incorrect password. Make sure your password has letters, symbols, digits and a capital letter!')

    form = CreateUser()
    return render(request, 'register.html', {'form': form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/products')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/products')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect(home_page)


class AccountDetailsView(View):
    template_name = 'account-details.html'
    def get(self, request):
        logged_user = request.user
        return render(request, self.template_name, {'user': logged_user})
    def post(self, request):
        pass
        # todo - make POST request to the FORM

