from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from product.models import Product
from .models import Customer, Seller, Admin, MyUser, VerificationCode


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['email'] = user.email
        token['is_Seller'] = user.is_Seller

        #test
        token['is_staff'] = user.is_staff
        return token


class SellerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Seller.objects.all())]
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Seller
        fields = [
            'id',
            'email',
            'name',
            'second_name',
            'phone_number',
            'description',
            'password',
            'password2',
        ]

        # {
        #     "email": "seller@gmail.com",
        #     "name": "Ashot.",
        #     "second_name": "Zaebov",
        #     "phone_number": "996700100200",
        #     "description": "Horoshyi",
        #     "password": "Qwerty_12345",
        #     "password2": "Qwerty_12345"
        # }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password': 'Password fields did not match.'}
           )
        return attrs


class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Customer.objects.all())]
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True
    )


    class Meta:
        model = Customer
        fields = [
            'id',
            'email',
            'name',
            'second_name',
            'phone_number',
            'card_number',
            'address',
            'post_code',
            'password',
            'password2',
        ]


class AdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Admin.objects.all())]
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Admin
        fields = [
            'id',
            'email',
            'name',
            'second_name',
            'phone_number',
            'password',
            'password2',
        ]


class AllUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = [
            "id", "last_login", "email", 'is_active', 'is_Seller'
        ]


class ProductsForAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class UserSettingsChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = [
         "is_active"
        ]


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = '__all__'