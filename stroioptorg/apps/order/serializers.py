from rest_framework import serializers

from apps.order.models import DeliveryMethod, PaymentMethod, Order, OrderItem, OrderStatus
from utils.common import format_russian_date

from utils.validators import phone_number_validator, firstname_validator, lastname_validator

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['user', 'stripe_payment_id']

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    def get_subtotal(self, obj):
        return obj.subtotal

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderResponseSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_label = serializers.SerializerMethodField()

    def get_status_label(self, instance):
        return OrderStatus(instance.status).label

    class Meta:
        model = Order
        exclude = ['user', 'stripe_payment_id', 'shop_address', 'updated_at', ]


    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['created_at'] = format_russian_date(instance.created_at)

        if data['delivery_method'] == DeliveryMethod.PICKUP and instance.shop_address:
            data['address'] = instance.shop_address.full_address

        data['payment_method'] = PaymentMethod(data['payment_method']).label

        data['delivery_method'] = DeliveryMethod(data['delivery_method']).label

        return data

class CreateOrderSerializer(serializers.Serializer):
    delivery_method = serializers.ChoiceField(choices=DeliveryMethod.choices)
    delivery_cost = serializers.IntegerField()
    shop_address = serializers.IntegerField(required=False)
    address = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices)
    comments = serializers.CharField(required=False, allow_blank=True)

    firstname = serializers.CharField(required=False, validators=[firstname_validator])
    lastname = serializers.CharField(required=False, validators=[lastname_validator])
    company = serializers.CharField(required=False, allow_blank=True)
    mail = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False, validators=[phone_number_validator])

    def validate(self, data):
        super().validate(data)
        request = self.context.get('request', None)

        if request:
            user = request.user

            if not user.is_authenticated:
                if not data['first_name']:
                    raise serializers.ValidationError('Нужно указать имя')
                if not data['last_name']:
                    raise serializers.ValidationError('Нужно указать фамилию')
                if not data['mail']:
                    raise serializers.ValidationError('Нужно указать почту')
                if not data['phone_number']:
                    raise serializers.ValidationError('Нужно указать номер телефона')



        if data['delivery_method'] == DeliveryMethod.PICKUP:
            data["address"] = ""
            if not data['shop_address']:
                raise serializers.ValidationError('Нужно указать адрес магазина с которого заберете')

        if data['delivery_method'] == DeliveryMethod.COURIER:
            data['shop_address'] = ''
            if not data['address']:
                raise serializers.ValidationError(data["address"])


        return data

class OrderRefreshPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

class OrderCalculateDeliveryCostSerializer(serializers.Serializer):
    address = serializers.CharField()

class OrderDeclineSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

class OrderConfirmSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()