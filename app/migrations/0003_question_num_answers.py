# Generated by Django 5.1.3 on 2024-11-09 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_likeanswer_answer_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='num_answers',
            field=models.IntegerField(default=0),
        ),
    ]
