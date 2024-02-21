from rest_framework import serializers
from core.models import Foods, Collection, Review, CartItem, Cart, OrderItem, Order, Customer, Address, Customer
from django.db import transaction
from core.signal import order_created
from core.serializers import CollectionImageSerializer, FoodImageSerializer


class CollectionSerializer(serializers.ModelSerializer):
    images = CollectionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'images']


class FoodSerializer(serializers.ModelSerializer):
    images = FoodImageSerializer(many=True, read_only=True)
    collection = CollectionSerializer()

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


class CartItemSerializer(serializers.ModelSerializer):
    foods = FoodSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.foods.price

    class Meta:
        model = CartItem
        fields = ['id', 'foods', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    # id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.foods.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    foods_id = serializers.IntegerField()

    def save(self, **kwargs):
        foods_id = self.validated_data['foods_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, foods_id=foods_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'foods_id', 'quantity']


class EditCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'food', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['gender', 'user_id']


class CreateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['gender']

    def create(self, validated_data):
        user_id = self.context['user_id']
        return Customer.objects.create(user_id=user_id, **validated_data)


class AddressSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = Address
        fields = ['id', 'street', 'plaque', 'unit', 'lat', 'len', 'customer']


class CreateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'plaque', 'unit', 'lat', 'len']

    def create(self, validated_data):
        (customer, created) = Customer.objects.get_or_create(user_id=self.context["user_id"])
        return Address.objects.create(customer=customer, **validated_data)


#class CreateOrderSerializer(serializers.Serializer):
#    cart_id = serializers.IntegerField()
#    description = serializers.CharField()
#    address = serializers.IntegerField()
#
#    def validate_cart_id(self, cart_id):
#        if Cart.objects.filter(pk=cart_id).exists():
#            return cart_id
#        else:
#            raise serializers.ValidationError('cart dosnt exist')
#
#    def save(self, **kwargs):
#        address_id = self.validated_data['address']
#        description = self.validated_data['description']
#        with transaction.atomic():
#            (customer, created) = Customer.objects.get_or_create(user_id=self.context["user_id"])
#            address = Address.objects.get(id=address_id)
#
#            order = Order.objects.create(customer=customer, description=description, address=address)
#            cart_items = CartItem.objects.select_related('foods').filter(cart_id=self.validated_data['cart_id'])
#            print(cart_items[0].foods, 'cart_items')
#            order_item = [OrderItem(
#                order=order,
#                foods=item.foods,
#                unit_price=item.foods.price,
#                quantity=item.quantity
#            ) for item in cart_items]
#            OrderItem.objects.bulk_create(order_item)
#            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()
#            # order_created.send_robust(self.__class__,order=order)
#            return order
#            # return super().save(**kwargs)
#

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    description = serializers.CharField()
    address = serializers.IntegerField()
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        address_id = self.validated_data['address']
        description = self.validated_data['description']
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            address = Address.objects.get(id=address_id)
            customer = Customer.objects.get(
                user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer, description=description, address=address)

            cart_items = CartItem.objects \
                .select_related('foods') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    food=item.foods,
                    unit_price=item.foods.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

           # order_created.send_robust(self.__class__, order=order)

            return order