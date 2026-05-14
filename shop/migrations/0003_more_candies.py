from decimal import Decimal

from django.db import migrations


NEW_CANDIES = [
    {
        'name': 'Nucita',
        'price': Decimal('1.200'),
        'stock': 1000,
        'image_path': 'img/candies/nucita.webp',
    },
    {
        'name': 'Choco Galleta',
        'price': Decimal('600'),
        'stock': 1000,
        'image_path': 'img/candies/choco_galleta.webp',
    },
    {
        'name': 'Choco Ball',
        'price': Decimal('300'),
        'stock': 1000,
        'image_path': 'img/candies/choco_ball_w.webp',
    },
    {
        'name': 'Revolcones',
        'price': Decimal('300'),
        'stock': 1000,
        'image_path': 'img/candies/revolcones.webp',
    },
]


def add_more_candies(apps, schema_editor):
    Candy = apps.get_model('shop', 'Candy')
    for candy in NEW_CANDIES:
        Candy.objects.update_or_create(name=candy['name'], defaults=candy)


def remove_more_candies(apps, schema_editor):
    Candy = apps.get_model('shop', 'Candy')
    Candy.objects.filter(name__in=[item['name'] for item in NEW_CANDIES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0002_seed_candies'),
    ]

    operations = [
        migrations.RunPython(add_more_candies, remove_more_candies),
    ]
