from django.db import migrations
def initialize_cards(apps, schema_editor):
    Flashcard = apps.get_model('scheduler', 'Flashcard')
    cards = [
        Flashcard(vocab='Indigenous'),
        Flashcard(vocab='Tacticity'),
        Flashcard(vocab='Lycoris'),
        Flashcard(vocab='Deceitful'),
        Flashcard(vocab='Spectroscopy')
    ]
    Flashcard.objects.bulk_create(cards)

class Migration(migrations.Migration):
    dependencies = [
        ('scheduler', '0003_alter_reviewresult_due_date_and_more')
    ]

    operations = [
        migrations.RunPython(initialize_cards)
    ]