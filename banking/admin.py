from django.contrib import admin
from .models import UserAccount

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'account_number', 'account_type', 'balance']
    search_fields = ['username', 'account_number']
