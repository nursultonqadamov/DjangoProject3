from rest_framework import serializers
from .models import StockEntry, StockExit, CurrentStock

class StockEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = StockEntry
        fields = '__all__'
        read_only_fields = ['entered_by', 'timestamp']

class StockExitSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockExit
        fields = '__all__'
        read_only_fields = ['removed_by', 'timestamp']

class CurrentStockSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = CurrentStock
        fields = ['id', 'product', 'product_name', 'quantity']
