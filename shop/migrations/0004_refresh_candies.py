from decimal import Decimal

from django.db import migrations


CANDIES = [
    {
            'name': 'Brinky Chocolate',
            'price': Decimal('1200.00'),
            'stock': 1000,
            'image_path': 'img/candies/brinky_chocolate.webp',
        },
        {
            'name': 'Brinky Vainilla',
            'price': Decimal('1200.00'),
            'stock': 1000,
            'image_path': 'img/candies/brinky_vainilla.webp',
        },
        {
            'name': 'Mini Chocoso',
            'price': Decimal('1000.00'),
            'stock': 1000,
            'image_path': 'img/candies/mini_chocoso.webp',
        },
        {
            'name': 'Mini Brownie',
            'price': Decimal('1200.00'),
            'stock': 1000,
            'image_path': 'img/candies/mini_brownie.webp',
        },
        {
            'name': 'Barra BonbonBum',
            'price': Decimal('500.00'),
            'stock': 1000,
            'image_path': 'img/candies/barra_bonbonbum.webp',
        },
        {
            'name': 'Barra Muuu',
            'price': Decimal('800.00'),
            'stock': 1000,
            'image_path': 'img/candies/barra_muuu.webp',
        },
        {
            'name': 'Nucita',
            'price': Decimal('1200.00'),
            'stock': 1000,
            'image_path': 'img/candies/nucita.webp',
        },
        {
            'name': 'Choco Galleta',
            'price': Decimal('600.00'),
            'stock': 1000,
            'image_path': 'img/candies/choco_galleta.webp',
        },
        {
            'name': 'Choco Ball',
            'price': Decimal('300.00'),
            'stock': 1000,
            'image_path': 'img/candies/choco_ball_w.webp',
        },
        {
            'name': 'Revolcones',
            'price': Decimal('300.00'),
            'stock': 1000,
            'image_path': 'img/candies/revolcones.webp',
    },
]


def refresh_candies(apps, schema_editor):
    Candy = apps.get_model('shop', 'Candy')
    Candy.objects.all().delete()

    for candy in CANDIES:
        Candy.objects.create(**candy)


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0003_more_candies'),
    ]

    operations = [
        migrations.RunPython(refresh_candies, migrations.RunPython.noop),
    ]
