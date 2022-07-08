from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.CharField(max_length=300, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('venue', models.CharField(max_length=300)),
                ('section', models.CharField(max_length=20)),
                ('row', models.CharField(max_length=20)),
                ('seat', models.CharField(max_length=10)),
                ('face', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TicketSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('ticketid', models.CharField(max_length=300))
            ],
        ),
    ]