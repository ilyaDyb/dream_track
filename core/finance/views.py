
# financial-profile/
# financial-profile/<int:id>

# deposits/
# deposits/<int:id>
# deposits/<int:id>/transactions 
# deposits/<int:id>/transactions/<int:transaction_id>

from rest_framework import generics, permissions

from drf_yasg.utils import swagger_auto_schema

from core.docs.templates import AUTH_HEADER
from .models import FinancialProfile, Deposit, DepositTransaction
from .serializers import (
    FinancialProfileSerializer,
    DepositSerializer,
    DepositTransactionSerializer
)

class FinancialProfileListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FinancialProfileSerializer
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        return FinancialProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FinancialProfileDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FinancialProfileSerializer
    lookup_field = 'id'
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_queryset(self):
        return FinancialProfile.objects.filter(user=self.request.user)

class DepositListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepositSerializer
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DepositDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepositSerializer
    lookup_field = 'id'
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user)

class DepositTransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepositTransactionSerializer
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        deposit_id = self.kwargs.get('id')
        return DepositTransaction.objects.filter(deposit__id=deposit_id, deposit__user=self.request.user)
    
    def perform_create(self, serializer):
        deposit_id = self.kwargs.get('id')
        deposit = Deposit.objects.get(id=deposit_id, user=self.request.user)
        serializer.save(deposit=deposit)

class DepositTransactionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepositTransactionSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'transaction_id'
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)    
    
    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[AUTH_HEADER])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        deposit_id = self.kwargs.get('id')
        return DepositTransaction.objects.filter(deposit__id=deposit_id, deposit__user=self.request.user)
    