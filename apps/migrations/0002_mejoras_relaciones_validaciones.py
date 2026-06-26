# Generated manually for model improvements

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ]
            ),
        ),
        migrations.AddField(
            model_name='certificate',
            name='enrollment',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='certificate',
                to='apps.enrollment',
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(
                related_name='courses',
                through='apps.CourseTag',
                to='apps.tag',
            ),
        ),
    ]
