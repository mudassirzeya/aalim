# Generated by Django 3.2.5 on 2022-06-26 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aalim', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='father_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
