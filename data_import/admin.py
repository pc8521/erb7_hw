from django.contrib import admin
from .models import Person, Category, Transaction

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('person', 'category', 'amount', 'date')
    list_filter = ('date', 'category')
    search_fields = ('person__first_name', 'person__last_name', 'notes')