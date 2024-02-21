from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .serializer import FoodSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, \
    AddCartItemSerializer, EditCartItemSerializer, OrderSerializer, CreateOrderSerializer, CustomerSerializer, \
    CreateCustomerSerializer, AddressSerializer, CreateAddressSerializer
from core.models import Foods, Collection, Review, Cart, CartItem, Order, OrderItem, Customer, Address
from core.filters import FoodFilter


class FoodViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Foods.objects.select_related('collection').prefetch_related('images').all()
    serializer_class = FoodSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FoodFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price']

    def get_serializer_context(self):
        return {'request': self.request}


class CollectionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Collection.objects.prefetch_related('images').all()
    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class CartViewSet(CreateModelMixin, GenericViewSet, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__foods').all()


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return EditCartItemSerializer
        else:
            return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart__id=self.kwargs['cart_pk']).select_related("foods")


class OrderViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        # elif self.request.method == 'PATCH':
        #     return UpdateOrderSerializer
        else:
            return OrderSerializer

    def get_queryset(self):
        (customer_id, created) = Customer.objects.only('id').get_or_create(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}


class CustomerView(ListModelMixin, GenericViewSet, CreateModelMixin):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.only('id').prefetch_related("address").get_or_create(user_id=self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCustomerSerializer
        else:
            return CustomerSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}


class AddressView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AddressSerializer
        else:
            return CreateAddressSerializer

    def get_queryset(self):
        (customer_id, created) = Customer.objects.only('id').get_or_create(user_id=self.request.user.id)
        return Address.objects.filter(customer_id=customer_id)

    def get_serializer_context(self):

        return {'user_id': self.request.user.id}
