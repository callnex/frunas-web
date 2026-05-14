from decimal import Decimal

from django.db import migrations


def seed_candies(apps, schema_editor):
    Candy = apps.get_model('shop', 'Candy')
    candies = [
        {
            'name': 'Brinky Chocolate',
            'price': Decimal('1.200'),
            'stock': 1000,
            'image_path': 'img/candies/brinky_chocolate.webp',
        },
        {
            'name': 'Brinky Vainilla',
            'price': Decimal('1.200'),
            'stock': 1000,
            'image_path': 'img/candies/brinky_vainilla.webp',
        },
        {
            'name': 'Mini Chocoso',
            'price': Decimal('1.000'),
            'stock': 1000,
            'image_path': 'img/candies/mini_chocoso.webp',
        },
        {
            'name': 'Mini Brownie',
            'price': Decimal('1.200'),
            'stock': 1000,
            'image_path': 'img/candies/mini_brownie.webp',
        },
        {
            'name': 'Barra BonbonBum',
            'price': Decimal('500'),
            'stock': 1000,
            'image_path': 'img/candies/barra_bonbonbum.webp',
        },
        {
            'name': 'Barra Muuu',
            'price': Decimal('800'),
            'stock': 1000,
            'image_path': 'img/candies/barra_muuu.webp',
        },
    ]
    for candy in candies:
        Candy.objects.update_or_create(name=candy['name'], defaults=candy)


def unseed_candies(apps, schema_editor):
    Candy = apps.get_model('shop', 'Candy')
    Candy.objects.filter(
        name__in=[
            'Brinky Chocolate',
            'Brinky Vainilla',
            'Mini Chocoso',
            'Mini Brownie',
            'Barra BonbonBum',
            'Barra Muuu',
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_candies, unseed_candies),
    ]
