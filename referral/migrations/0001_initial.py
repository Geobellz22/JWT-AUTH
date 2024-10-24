# Generated by Django 4.2.4 on 2024-09-07 09:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referral_code', models.CharField(max_length=6, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('referred_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referred_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReferralReward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3'), (4, 'Level 4')])),
                ('reward_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('referral', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='referral.referral')),
            ],
        ),
    ]