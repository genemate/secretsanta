# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('santa_game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='gift_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата вручения подарка'),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='min_budget',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Минимальный бюджет'),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='max_budget',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Максимальный бюджет'),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание/Правила игры'),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='reminder_enabled',
            field=models.BooleanField(default=True, verbose_name='Включить напоминания'),
        ),
    ]
