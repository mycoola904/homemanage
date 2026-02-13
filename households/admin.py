from django.contrib import admin

# Register your models here.
from .models import Household, HouseholdMember
@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'is_archived', 'timezone', 'currency_code', 'created_by', 'created_at', 'updated_at')

@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'household', 'user', 'role', 'is_primary', 'created_at', 'updated_at')
    