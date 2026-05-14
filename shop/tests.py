import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Candy, Order


class ShopFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.candy = Candy.objects.create(
            name='Gomitas Magicas',
            price=Decimal('4.50'),
            stock=12,
            image_path='img/candies/gomitas-magicas.svg',
            is_active=True,
        )
        cls.other_candy = Candy.objects.create(
            name='Paleta Remolino',
            price=Decimal('2.00'),
            stock=0,
            image_path='img/candies/paleta-remolino.svg',
            is_active=True,
        )
        cls.user = User.objects.create_user(
            username='dulcefan',
            email='dulce@example.com',
            password='CandyPass123',
            first_name='Dulce Fan',
        )
        cls.other_user = User.objects.create_user(
            username='otrofan',
            email='otro@example.com',
            password='CandyPass123',
        )

    def test_store_is_public(self):
        response = self.client.get(reverse('store'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dulces Disponibles')
        self.assertContains(response, 'data-candy-price="4.50"')
        self.assertNotContains(response, 'Stock: 12')
        self.assertNotContains(response, 'Agregar')
        self.assertNotContains(response, 'Compra simulada activa')
        self.assertContains(response, '/static/js/store.js')

    def test_store_shows_extra_seed_products(self):
        Candy.objects.create(
            name='Bastones de Menta',
            price=Decimal('2.70'),
            stock=48,
            image_path='img/candies/bastones-menta.svg',
            is_active=True,
        )
        Candy.objects.create(
            name='Choco Bombs',
            price=Decimal('5.40'),
            stock=30,
            image_path='img/candies/choco-bombs.svg',
            is_active=True,
        )
        Candy.objects.create(
            name='Corazones de Azucar',
            price=Decimal('3.20'),
            stock=72,
            image_path='img/candies/corazones-azucar.svg',
            is_active=True,
        )
        Candy.objects.create(
            name='Aros Frutales',
            price=Decimal('2.50'),
            stock=56,
            image_path='img/candies/aros-frutales.svg',
            is_active=True,
        )
        response = self.client.get(reverse('store'))
        self.assertContains(response, 'Bastones de Menta')
        self.assertContains(response, 'Choco Bombs')
        self.assertContains(response, 'Corazones de Azucar')
        self.assertContains(response, 'Aros Frutales')

    def test_register_rejects_duplicate_username(self):
        response = self.client.post(
            reverse('register'),
            {
                'full_name': 'Nuevo Usuario',
                'username': 'dulcefan',
                'email': 'nuevo@example.com',
                'password1': 'CandyPass123',
                'password2': 'CandyPass123',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este nombre de usuario ya existe.')

    def test_register_rejects_duplicate_email(self):
        response = self.client.post(
            reverse('register'),
            {
                'full_name': 'Nuevo Usuario',
                'username': 'nuevofan',
                'email': 'dulce@example.com',
                'password1': 'CandyPass123',
                'password2': 'CandyPass123',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este correo ya esta registrado.')

    def test_register_creates_inactive_user_and_sends_email(self):
        response = self.client.post(
            reverse('register'),
            {
                'full_name': 'Nuevo Usuario',
                'username': 'nuevofan',
                'email': 'nuevo@example.com',
                'password1': 'CandyPass123',
                'password2': 'CandyPass123',
            },
            follow=True,
        )

        user = get_user_model().objects.get(username='nuevofan')
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Confirma tu cuenta en FRUNAS', mail.outbox[0].subject)
        self.assertRedirects(response, reverse('login'))

    def test_activation_link_activates_user(self):
        user = get_user_model().objects.create_user(
            username='pendiente',
            email='pendiente@example.com',
            password='CandyPass123',
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            reverse('activate_account', kwargs={'uidb64': uid, 'token': token}),
            follow=True,
        )

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertRedirects(response, reverse('login'))

    def test_login_with_username(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'dulcefan', 'password': 'CandyPass123'},
        )
        self.assertRedirects(response, reverse('store'))

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'dulcefan', 'password': 'clave-invalida'},
            follow=True,
        )
        self.assertContains(response, 'Credenciales incorrectas.')

    def test_logout_redirects_to_store(self):
        self.client.login(username='dulcefan', password='CandyPass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('store'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_guest_checkout_redirects_to_login(self):
        response = self.client.post(
            reverse('checkout'),
            {'cart_data': json.dumps([{'candy_id': self.candy.id, 'quantity': 1}])},
        )
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('store')}")

    def test_checkout_creates_order_and_updates_stock(self):
        self.client.login(username='dulcefan', password='CandyPass123')
        response = self.client.post(
            reverse('checkout'),
            {
                'cart_data': json.dumps(
                    [
                        {'candy_id': self.candy.id, 'quantity': 2},
                    ]
                )
            },
        )
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse('order_success', kwargs={'pk': order.pk}))
        self.candy.refresh_from_db()
        self.assertEqual(self.candy.stock, 10)
        self.assertEqual(order.total_amount, Decimal('9.00'))
        self.assertEqual(order.items.count(), 1)

    def test_order_success_page_has_no_success_hero_image(self):
        order = Order.objects.create(user=self.user, total_amount=Decimal('9.00'))
        self.client.login(username='dulcefan', password='CandyPass123')
        response = self.client.get(reverse('order_success', kwargs={'pk': order.pk}))
        self.assertNotContains(response, 'success-hero.svg')
        self.assertContains(response, 'Gracias por tu compra')
        self.assertContains(response, "localStorage.removeItem('sugar_rush_cart')")

    def test_cannot_buy_more_than_stock(self):
        self.client.login(username='dulcefan', password='CandyPass123')
        response = self.client.post(
            reverse('checkout'),
            {
                'cart_data': json.dumps(
                    [
                        {'candy_id': self.candy.id, 'quantity': 99},
                    ]
                )
            },
            follow=True,
        )
        self.assertContains(response, 'Solo quedan 12 unidades de Gomitas Magicas.')
        self.assertEqual(Order.objects.count(), 0)

    def test_empty_cart_does_not_create_order(self):
        self.client.login(username='dulcefan', password='CandyPass123')
        response = self.client.post(
            reverse('checkout'),
            {'cart_data': json.dumps([])},
            follow=True,
        )
        self.assertContains(response, 'Selecciona al menos un dulce para continuar.')
        self.assertEqual(Order.objects.count(), 0)

    def test_account_only_shows_user_orders(self):
        Order.objects.create(user=self.user, total_amount=Decimal('4.50'))
        Order.objects.create(user=self.other_user, total_amount=Decimal('2.00'))
        self.client.login(username='dulcefan', password='CandyPass123')
        response = self.client.get(reverse('account'))
        self.assertContains(response, '$4,50')
        self.assertNotContains(response, '$2,00')

    def test_user_cannot_see_other_user_order(self):
        other_order = Order.objects.create(user=self.other_user, total_amount=Decimal('2.00'))
        self.client.login(username='dulcefan', password='CandyPass123')
        response = self.client.get(reverse('order_detail', kwargs={'pk': other_order.pk}))
        self.assertEqual(response.status_code, 404)
