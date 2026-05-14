import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, DetailView, TemplateView

from .forms import LoginForm, RegisterForm
from .models import Candy, Order, OrderItem


class StoreView(TemplateView):
    template_name = 'shop/store.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candies'] = Candy.objects.filter(is_active=True).order_by('id')
        return context


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = self.request.build_absolute_uri(
            reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
        )

        subject = 'Confirma tu cuenta en FRUNAS'
        message = render_to_string(
            'shop/emails/confirm_account.txt',
            {
                'user': user,
                'activation_url': activation_url,
            },
        )

        send_mail(
            subject,
            message,
            None,
            [user.email],
            fail_silently=False,
        )

        messages.success(
            self.request,
            'Tu cuenta fue creada correctamente. Revisa tu correo para activarla.',
        )
        return response


class UserLoginView(LoginView):
    template_name = 'shop/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Credenciales incorrectas. Revisa tu nombre de usuario y contrasena.',
        )
        return super().form_invalid(form)


class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('store')

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('store')


class CheckoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def handle_no_permission(self):
        messages.info(
            self.request,
            'Debes iniciar sesion para confirmar tu compra.',
        )
        return redirect(f"{reverse('login')}?next={reverse('store')}")

    def post(self, request, *args, **kwargs):
        raw_payload = request.POST.get('cart_data', '')
        try:
            cart_items = json.loads(raw_payload)
        except json.JSONDecodeError:
            messages.error(request, 'No pudimos procesar tu carrito. Intentalo de nuevo.')
            return redirect('store')

        normalized_map = {}
        for item in cart_items:
            try:
                candy_id = int(item.get('candy_id'))
                quantity = int(item.get('quantity'))
            except (TypeError, ValueError, AttributeError):
                continue
            if quantity > 0:
                normalized_map[candy_id] = normalized_map.get(candy_id, 0) + quantity

        normalized_items = [
            {'candy_id': candy_id, 'quantity': quantity}
            for candy_id, quantity in normalized_map.items()
        ]

        if not normalized_items:
            messages.error(request, 'Selecciona al menos un dulce para continuar.')
            return redirect('store')

        with transaction.atomic():
            candy_ids = [item['candy_id'] for item in normalized_items]
            candies = {
                candy.id: candy
                for candy in Candy.objects.select_for_update().filter(
                    id__in=candy_ids,
                    is_active=True,
                )
            }
            order_items = []
            total_amount = Decimal('0.00')

            for entry in normalized_items:
                candy = candies.get(entry['candy_id'])
                quantity = entry['quantity']
                if candy is None:
                    messages.error(request, 'Uno de los dulces seleccionados ya no esta disponible.')
                    return redirect('store')
                if quantity > candy.stock:
                    messages.error(
                        request,
                        f'Solo quedan {candy.stock} unidades de {candy.name}.',
                    )
                    return redirect('store')

                unit_price = candy.price
                line_total = unit_price * quantity
                total_amount += line_total
                order_items.append(
                    {
                        'candy': candy,
                        'product_name': candy.name,
                        'unit_price': unit_price,
                        'quantity': quantity,
                        'line_total': line_total,
                    }
                )

            order = Order.objects.create(user=request.user, total_amount=total_amount)
            for item in order_items:
                OrderItem.objects.create(order=order, **item)
                candy = item['candy']
                candy.stock -= item['quantity']
                candy.save(update_fields=['stock', 'updated_at'])

        messages.success(request, 'Tu compra fue registrada con exito.')
        return redirect('order_success', pk=order.pk)


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.request.user.orders.prefetch_related('items').all()
        return context


class UserOrderMixin(LoginRequiredMixin):
    model = Order
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related('items__candy')
        )


class OrderDetailView(UserOrderMixin, DetailView):
    template_name = 'shop/order_detail.html'
    context_object_name = 'order'


class OrderSuccessView(UserOrderMixin, DetailView):
    template_name = 'shop/order_success.html'
    context_object_name = 'order'


class ActivateAccountView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(get_user_model(), pk=uid)
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            messages.success(request, 'Tu cuenta fue activada. Ya puedes iniciar sesion.')
        else:
            messages.error(request, 'El enlace de activacion no es valido o ya expiro.')

        return redirect('login')
