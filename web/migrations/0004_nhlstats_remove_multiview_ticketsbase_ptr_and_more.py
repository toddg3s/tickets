# Generated by Django 4.0.6 on 2022-07-14 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_ticketset_tickets'),
    ]

    operations = [
        migrations.CreateModel(
            name='NHLStats',
            fields=[
                ('name', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('rank', models.CharField(max_length=2)),
                ('record', models.CharField(max_length=10)),
                ('vssea', models.CharField(max_length=10)),
                ('playoffs', models.CharField(max_length=30)),
            ],
        ),
        # migrations.RemoveField(
        #     model_name='multiview',
        #     name='ticketsbase_ptr',
        # ),
        # migrations.RemoveField(
        #     model_name='singleview',
        #     name='ticketsbase_ptr',
        # ),
        # migrations.DeleteModel(
        #     name='Home',
        # ),
        # migrations.DeleteModel(
        #     name='MultiView',
        # ),
        # migrations.DeleteModel(
        #     name='SingleView',
        # ),
        # migrations.DeleteModel(
        #     name='TicketsBase',
        # ),
    ]
