# Generated by Django 4.0.4 on 2022-05-28 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0003_alter_donation_options_alter_donation_sponsor_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='status',
        ),
        migrations.RemoveField(
            model_name='student',
            name='status',
        ),
    ]
