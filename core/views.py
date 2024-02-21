from django.contrib.auth import get_user_model
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
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes

from .models import Foods, Collection, Review, FoodImage, CollectionImage, OtpRequest, Order
from .serializers import FoodSerializer, CollectionSerializer, ReviewSerializer, FoodImageSerializer, \
    CreateFoodSerializer, UserSerializer, CollectionImageSerializer, RequestOTPSerializer, RequestOTPResponseSerializer, \
    VerifyOtpRequestSerializer, ObtainTokenSerializer, OrderSerializer
from .filters import FoodFilter
from .permisions import IsAminOrReadOnly
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.views import APIView
from openpyxl import Workbook
from django.http import HttpResponse


class FoodViewSet(ModelViewSet):
    queryset = Foods.objects.select_related('collection').prefetch_related('images').all()

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FoodFilter
    pagination_class = PageNumberPagination
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'max_buy', 'title', 'unit_price']
    permission_classes = [IsAminOrReadOnly]

    def get_serializer_class(self):
        if (self.request.method == 'GET'):
            return FoodSerializer
        else:
            return CreateFoodSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        food = get_object_or_404(Foods, pk=pk)
        if food.orderitem_set.count() > 0:
            return Response({'error': 'this food cannot be deleted'})
        food.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FoodImageViewSet(ModelViewSet):
    serializer_class = FoodImageSerializer

    def get_queryset(self):
        return FoodImage.objects.filter(food_id=self.kwargs['food_pk'])

    def get_serializer_context(self):
        return {'food_id': self.kwargs['food_pk']}


class CollectionImageViewSet(ModelViewSet):
    serializer_class = CollectionImageSerializer

    def get_queryset(self):
        return CollectionImage.objects.filter(collection_id=self.kwargs['collection_pk'])

    def get_serializer_context(self):
        return {'collection_id': self.kwargs['collection_pk']}


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related('images').all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination
    search_fields = ['title']

    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.foods_set.count() > 0:
            return Response({'error': 'this collection cannot be deleted'})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAminOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(foods_id=self.kwargs['food_pk'])

    def get_serializer_context(self):
        return {'food_id': self.kwargs['food_pk']}


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination
    search_fields = ['email', 'username']


class OTPView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='receiver',
                location='query',
                required=True,
                type=str,
                description='receiver info'
            ),
            OpenApiParameter(
                name='channel',
                location='query',
                required=True,
                type=str,
                description='channel option : Phone , E-Mail'
            ),
        ],

    )
    def get(self, request):
        serializer = RequestOTPSerializer(data=request.query_params)

        if serializer.is_valid():

            data = serializer.validated_data
            try:
                otp = OtpRequest.objects.generate(data)
                return Response(data=RequestOTPResponseSerializer(otp).data)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @extend_schema(
        request=VerifyOtpRequestSerializer,
        responses={200: VerifyOtpRequestSerializer},
    )
    def post(self, request):
        serializer = VerifyOtpRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if OtpRequest.objects.is_valid(data['receiver'], data['request_id'], data['password']):

                return Response(self._handle_login(data))
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def _handle_login(self, otp):
        User = get_user_model()
        query = User.objects.filter(username=otp['receiver'])
        if query.exists():
            created = False
            user = query.first()
        else:
            user = User.objects.create(username=otp['receiver'], email=otp['receiver'], phone_number=otp['receiver'])
            created = True

        refresh = RefreshToken.for_user(user)

        return ObtainTokenSerializer({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'created': created,
            'user': user,
            #   'phone_number': user.phone_number,
        }).data


class OrderView(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete']
    pagination_class = PageNumberPagination
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related('address').all()
    filter_backends = [OrderingFilter]
    permission_classes = [IsAminOrReadOnly]
    ordering_fields = ['placed_at']


class ExcelExportView(APIView):
    def get(self, request):
        queryset = Order.objects.all()
        serializer = OrderSerializer(queryset, many=True)

        # Create a new workbook and add a worksheet
        workbook = Workbook()
        worksheet = workbook.active

        # Write header row
        header = ["1","2","3"]
        worksheet.append(header)

        # Write data rows
        for item in serializer.data:

            row = ['item.payment_status']
            worksheet.append(row)

        # Create a response with Excel content type
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=your_exported_data.xlsx'

        # Save the workbook to the response
        workbook.save(response)

        return response