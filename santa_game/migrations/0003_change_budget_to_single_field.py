# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('santa_game', '0002_add_game_session_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesession',
            name='min_budget',
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='max_budget',
        ),
        migrations.AddField(
            model_name='gamesession',
            name='budget',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Бюджет на подарок'),
        ),
    ]
