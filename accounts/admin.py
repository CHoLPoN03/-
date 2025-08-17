from django.contrib import admin
from .models import BalanceSheetItem, BalanceGroup, Account, Transaction


@admin.register(BalanceSheetItem)
class BalanceSheetItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


@admin.register(BalanceGroup)
class BalanceGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'item', 'code')
    list_filter = ('item',)
    search_fields = ('name', 'code')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'type', 'group', 'created_at')
    list_filter = ('type', 'group')
    search_fields = ('number', 'name')
    readonly_fields = ('number', 'created_at', 'updated_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'debit_account', 'credit_account', 'amount', 'description')
    list_filter = ('created_at',)
    search_fields = ('debit_account__name', 'credit_account__name', 'description')
