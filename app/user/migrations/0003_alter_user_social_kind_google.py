from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_withdrawaluserproxy_alter_user_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="social_kind",
            field=models.CharField(
                blank=True,
                choices=[("kakao", "카카오"), ("apple", "애플"), ("google", "구글")],
                max_length=8,
                null=True,
                verbose_name="소셜로그인 종류",
            ),
        ),
    ]
