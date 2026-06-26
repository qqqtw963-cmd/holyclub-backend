from django.apps import apps
from django.db import models
from django.db.models import FileField, ImageField

FIELD_CHOICES = []


def get_file_fields():
    global FIELD_CHOICES
    if not FIELD_CHOICES:
        for model in apps.get_models():
            for field in model._meta.fields:
                if isinstance(field, (ImageField, FileField)):
                    field_id = f"{model._meta.app_label}.{model.__name__}.{field.name}"
                    field_label = f"{field.verbose_name}"
                    FIELD_CHOICES.append((field_id, field_label))

    return FIELD_CHOICES


class FileTypeChoices(models.TextChoices):
    IMAGE = "image", "이미지 그래픽 데이터(i.e. jpeg, png, gif, apng, etc.)"
    AUDIO = "audio", "오디오/음악 데이터(i.e. mpeg, vorbis, etc.)"
    TEXT = "text", "텍스트 데이터(i.e. plain, csv, html, etc.)"
    VIDEO = "video", "비디오 데이터(i.e. mp4, etc.)"
    APPLICATION = "application", "이진 데이터(i.e. pdf, zip, pkcs8, etc.)"
