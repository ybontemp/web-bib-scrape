from django.contrib import admin

from .models import BibUser, StoredBook


admin.site.register(BibUser)
admin.site.register(StoredBook)