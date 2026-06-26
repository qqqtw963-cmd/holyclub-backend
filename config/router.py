from django.conf import settings
from django.db import transaction


class Router:
    databases = settings.DATABASES
    default_app_labels: set = {}

    def db_for_read(self, model, **hints):
        if not self.databases.get("reader"):
            return "default"
        if self._check_in_atomic_block():
            return "default"
        return "reader"

    @staticmethod
    def db_for_write(model, **hints):
        return "default"

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        return True

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        return True

    @staticmethod
    def _check_in_atomic_block():
        transaction.get_autocommit()
        if transaction.get_connection("default").in_atomic_block:
            return True
        return False
