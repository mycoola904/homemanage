from django.contrib import admin

# Register your models here.
from .models import Transaction, Account
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'amount', 'transaction_type', 'description')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'household', 'name', 'institution', 'account_type', 'status', 'current_balance')