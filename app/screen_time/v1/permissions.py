from rest_framework.permissions import IsAuthenticated


class ScreenTimePermission(IsAuthenticated):
    pass
