from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bible", "0003_bible_verse_and_reference"),
        ("testimony_journal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="testimonyjournal",
            name="bible_reference",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="testimony_journals", to="bible.biblereference", verbose_name="성경 구절 선택"),
        ),
    ]
