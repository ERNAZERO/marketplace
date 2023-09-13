from rest_framework import serializers
from .models import Product, Cart, Customer, Comment


class ProductSerializer(serializers.ModelSerializer):
    sold = serializers.CharField(
        write_only=True,
    )
    views_by = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = Product
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True)
    class Meta:
        model = Cart
        fields = ['customer', 'product']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class PaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    currency = serializers.CharField(max_length=3, default='usd')
    stripe_token = serializers.CharField(max_length=100)