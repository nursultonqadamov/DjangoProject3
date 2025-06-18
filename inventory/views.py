from rest_framework import viewsets, permissions
from .models import StockEntry, StockExit, CurrentStock
from .serializers import StockEntrySerializer, StockExitSerializer, CurrentStockSerializer
# Create your views here.


class StockEntryViewSet(viewsets.ModelViewSet):
    queryset = StockEntry.objects.all().order_by('-timestamp')
    serializer_class = StockEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        entry = serializer.save(entered_by=self.request.user)
        stock, created = CurrentStock.objects.get_or_create(product=entry.product)
        stock.quantity += entry.quantity
        stock.save()

class StockExitViewSet(viewsets.ModelViewSet):
    queryset = StockExit.objects.all().order_by('-timestamp')
    serializer_class = StockExitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        exit = serializer.save(removed_by=self.request.user)
        stock, created = CurrentStock.objects.get_or_create(product=exit.product)
        stock.quantity -= exit.quantity
        stock.save()

class CurrentStockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CurrentStock.objects.all()
    serializer_class = CurrentStockSerializer
    permission_classes = [permissions.IsAuthenticated]
