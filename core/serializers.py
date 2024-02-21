from core.models import Foods, Collection, Review, FoodImage, Cart, OrderItem, Order, Customer, CollectionImage, \
    OtpRequest, User
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as UserSerializerDjoser, UserSerializer as UserSerializerDjoser


class CollectionImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        collection_id = self.context['collection_id']
        return CollectionImage.objects.create(collection_id=collection_id, **validated_data)

    class Meta:
        model = CollectionImage
        fields = ['id', 'image']


class CollectionSerializer(serializers.ModelSerializer):
    images = CollectionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'images']


class FoodImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        food_id = self.context['food_id']
        return FoodImage.objects.create(food_id=food_id, **validated_data)

    class Meta:
        model = FoodImage
        fields = ['id', 'image']


class FoodSerializer(serializers.ModelSerializer):
    images = FoodImageSerializer(many=True, read_only=True)
    collection = CollectionSerializer()

    class Meta:
        model = Foods
        fields = ['id', 'description', 'title', 'price', 'inventory', 'collection', 'images', 'max_buy', 'unit_price']


class CreateFoodSerializer(serializers.ModelSerializer):
    images = FoodImageSerializer(many=True, read_only=True)

    # collection = CollectionSerializer()

    class Meta:
        model = Foods
        fields = ['id', 'description', 'title', 'price', 'inventory', 'collection', 'images', 'max_buy', 'unit_price']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['foods', 'name', 'description', 'date']

        def create(self, validated_data):
            food_id = self.context['food_id']
            return Review.objects.create(food_id=food_id, **validated_data)


class UserCreateSerializer(UserSerializerDjoser):
    class Meta(UserSerializerDjoser.Meta):
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']


class UserSerializer(UserSerializerDjoser):
    class Meta(UserSerializerDjoser.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserSerializerForId(UserSerializerDjoser):
    class Meta(UserSerializerDjoser.Meta):
        fields = ['id', 'username']


class RequestOTPSerializer(serializers.Serializer):
    # class Meta:
    #    fields = ['receiver', 'channel']

    receiver = serializers.CharField(max_length=50, allow_null=False)
    channel = serializers.ChoiceField(allow_null=False, choices=OtpRequest.OtpChannel.choices)


class RequestOTPResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpRequest
        fields = ['request_id', 'password']


class VerifyOtpRequestSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(allow_null=False)
    password = serializers.CharField(max_length=4, allow_null=False)
    receiver = serializers.CharField(max_length=64, allow_null=False)


class ObtainTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128, allow_null=False)
    refresh = serializers.CharField(max_length=128, allow_null=False)
    created = serializers.BooleanField()
    user = UserSerializer()


class OrderItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'food', 'quantity', 'unit_price']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Customer
        fields = ['gender',  'user']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()
    customer = CustomerSerializer()

    def get_total_price(self, cart):
        return sum([item.quantity * item.food.price for item in cart.items.all()])

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items', 'total_price' , 'description']
