from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)
    
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'division')
    search_fields = ('name',)
    ordering = ('id',)

@admin.register(Upazila)
class UpazilaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'district')
    search_fields = ('name',)
    ordering = ('id',)