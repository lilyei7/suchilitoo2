from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0001_initial'),  # Ajustar según corresponda a la última migración
    ]

    operations = [
        migrations.AlterField(
            model_name='receta',
            name='producto',
            field=models.OneToOneField(null=True, on_delete=models.SET_NULL, related_name='receta', to='restaurant.productoventa'),
        ),
    ]
