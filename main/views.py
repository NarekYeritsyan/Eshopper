from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render , redirect
from django.views.generic import ListView , DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm , UserCreationForm
from .models import (
    GeneralSlider , HeaderTop , Category , Product,
    CooperativeCompanies , GetInTouch , Store,
    ShoppingCart,
)

from .forms import (
    ContactUsForm, StayUpdatedForm, NewUserForm
)



class HomeListView(ListView):
    template_name = 'index.html'

    @staticmethod
    def __extract_all_data(request):
        general_sliders = GeneralSlider.objects.all()
        header = HeaderTop.objects.get()
        categories = Category.objects.all()
        just_arrived = Product.objects.order_by('-created_at')[:8]
        trandy_products = Product.objects.order_by('-id')[:8]
        cooperative_companies = CooperativeCompanies.objects.all()
        cart_items = ShoppingCart.objects.filter(user=request.user)



        context = {
            'nav': 'home',
            'general_sliders':general_sliders,
            'header':header,
            'categories':categories,
            "just_arrived":just_arrived,
            "trandy_products":trandy_products,
            "cooperative_companies":cooperative_companies,
            'cart_items':cart_items,

        }

        return context
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        return render(request , self.template_name , context=self.__extract_all_data(request))


    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = StayUpdatedForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = StayUpdatedForm()
        

        return redirect('home')


class ShopListView(ListView):
    template_name = 'shop.html'
    paginate_by = 2  # Number of products per page


    @staticmethod
    def __extract_all_data(request):
        categories = Category.objects.all()
        products = Product.objects.all()
        cart_items = ShoppingCart.objects.filter(user=request.user)
        paginator = Paginator(products, ShopListView.paginate_by)
        page = request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            products = paginator.page(paginator.num_pages)

        context = {
            'nav': 'shop',
            'products': products,
            'categories':categories,
            'cart_items':cart_items,

        }

        return context


    @staticmethod
    def product_filter_by_price(queryset , price_ranges):
        new_queryset = []
        for price in price_ranges:
            try:
                upper_bound , lower_bound = map(int , price.replace('$' , '').split(' - '))
            except Exception as ex:
                price(ex)
                return queryset
            else:
                queryset = queryset.filter(price__range=(lower_bound , upper_bound))
                new_queryset.append(queryset)

    @staticmethod
    def product_filter_by_color(queryset, color_ids):
        try:
            queryset = queryset.filter(colors__in = color_ids)
        except Exception as ex:
            return queryset

    @staticmethod
    def product_filter_by_size(queryset, size_ids):
        queryset = queryset.filter(sizes__in = size_ids)



    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        return render(request , self.template_name , context=self.__extract_all_data(request))



class ShopDetailView(DetailView):
    template_name = 'detail.html'


    def get(self, request: HttpRequest, prod_id, *args: Any, **kwargs: Any) -> HttpResponse:
        categories = Category.objects.all()
        product = Product.objects.get(pk=prod_id)
        cart_items = ShoppingCart.objects.filter(user=request.user)


        context = {
            'categories':categories,
            'product':product,
            'cart_items':cart_items,
        }
        return render(request , self.template_name , context=context)


    def post(self, request: HttpRequest, prod_id , *args: Any, **kwargs: Any) -> HttpResponse:
        user = request.user
        product = Product.objects.get(pk=prod_id)
        quantity = request.POST.get('quantity')

        try:
            cart = ShoppingCart.objects.get(user=user , product=product)
        except:
            ShoppingCart.objects.create(
                user = user,
                product = product,
                quantity = 1,
            )
        else:
            cart.quantity += 1
            cart.save()

        return redirect('home')


class ContactListView(ListView):
    template_name = 'contact.html'

    @staticmethod
    def __extract_all_data(request):

        categories = Category.objects.all()
        get_in_touch = GetInTouch.objects.get()
        stores = Store.objects.all()
        cart_items = ShoppingCart.objects.filter(user=request.user)


        context = {
            'nav': 'contact',
            'categories':categories,
            'get_in_touch':get_in_touch,
            'stores':stores,
            'cart_items':cart_items,

        }
        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        return render(request , self.template_name , context=self.__extract_all_data(request))


    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = ContactUsForm()

        return redirect("contact")


class CartListView(ListView):
    template_name = 'cart.html'


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        categories = Category.objects.all()
        cart_items = ShoppingCart.objects.filter(user=request.user)
        total_price = sum([item.product.price * item.quantity for item in cart_items])
        

        context = {
            'nav': 'cart',
            'categories':categories,
            'cart_items': cart_items,
            'total_price':total_price,

        }
        return render(request , self.template_name , context=context)



class CheckoutListView(ListView):
    template_name = 'checkout.html'


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        categories = Category.objects.all()
        cart_items = ShoppingCart.objects.filter(user=request.user)


        context = {
            'nav': 'checkout',
            'categories':categories,
            'cart_items':cart_items,

        }
        return render(request , self.template_name , context=context)




def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render(request=request, template_name="register.html", context={"register_form":form})


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("home")

