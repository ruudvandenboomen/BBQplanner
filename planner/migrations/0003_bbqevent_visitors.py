# Generated by Django 3.0.4 on 2020-03-14 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_auto_20200313_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='bbqevent',
            name='visitors',
            field=models.ManyToManyField(to='planner.Visitor'),
        ),
    ]