from django.contrib import admin
from .models import StockEntry, StockExit, CurrentStock
# Register your models here.


admin.site.register(StockEntry)
admin.site.register(StockExit)
admin.site.register(CurrentStock)
