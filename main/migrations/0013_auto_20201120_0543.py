# Generated by Django 3.1.3 on 2020-11-20 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_repository_fork'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commit_file',
            name='file',
        ),
        migrations.AddField(
            model_name='commit_file',
            name='url',
            field=models.TextField(null=True),
        ),
    ]