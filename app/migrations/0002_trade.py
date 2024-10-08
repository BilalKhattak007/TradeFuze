# Generated by Django 5.0.6 on 2024-10-05 15:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_date', models.DateField()),
                ('entry_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('exit_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('trade_type', models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell')], max_length=4)),
                ('stop_loss', models.DecimalField(decimal_places=2, max_digits=15)),
                ('reason', models.TextField()),
                ('leverage_used', models.IntegerField(default=1)),
                ('profit_or_loss', models.DecimalField(decimal_places=2, max_digits=15)),
                ('winning_trade', models.BooleanField(default=False)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.wallet')),
            ],
        ),
    ]
