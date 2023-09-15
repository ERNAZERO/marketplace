from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.product.pagination import CustomLimitOffsetPagination
from .serializers import SellerSerializer, CustomerSerializer, MyTokenObtainPairSerializer, AdminSerializer, \
    AllUserSerializer, UserSettingsChangeSerializer, ProductsForAdminSerializer
from .models import Seller, Customer, MyUser, Admin, VerificationCode
from .permissions import AnnonPermission
from apps.product.models import Cart, Product
from apps.product.serializers import ProductSerializer
from rest_framework import generics
# from .permissions import IsOwnerOfCartItem
import random
from django.core.mail import send_mail

def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))


def send_verification_email(email, verification_code):
    subject = 'Верификация вашего аккаунта'
    message = f'Ваш верификационный код: {verification_code}'
    from_email = 'erkinbekovernaz@gmail.com'
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)



def get_object(id:int, table):
    try:
        return table.objects.get(id=id)
    except table.DoesNotExist:
        raise Http404


class LoginView(TokenObtainPairView):
    permission_classes = (AnnonPermission, )
    serializer_class = MyTokenObtainPairSerializer


class AdminRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            admin = Admin.objects.create(
                email=request.data['email'],
                is_staff=True,
                name=request.data['name'],
                second_name=request.data['second_name'],
                phone_number=request.data['phone_number'],
            )
            admin.set_password(request.data['password'])
            admin.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SellerSerializer(data=request.data)
        if serializer.is_valid():
            seller = Seller.objects.create(
                email=request.data['email'],
                is_Seller=True,
                name=request.data['name'],
                second_name=request.data['second_name'],
                phone_number=request.data['phone_number'],
                description=request.data['description']
            )
            seller.set_password(request.data['password'])
            seller.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = Customer.objects.create(
                email=request.data['email'],
                name=request.data['name'],
                second_name=request.data['second_name'],
                phone_number=request.data['phone_number'],
                card_number=request.data['card_number'],
                address=request.data['address'],
                post_code=request.data['post_code']
            )
            customer.set_password(request.data['password'])
            customer.save()
            cart = Cart.objects.create(customer=customer)
            cart.save()

            code = generate_verification_code()
            expiration_time = timezone.now() + timezone.timedelta(minutes=15)
            verification_code = VerificationCode(user=customer, code=code, expiration_time=expiration_time)
            verification_code.save()

            # send_verification_email(request.data['email'], code)
            print (request.data['email'], code)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get (self, request, id):
        customer = get_object(id, Customer)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SellerListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        sellers = Seller.objects.all()
        serializer = SellerSerializer(sellers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SellerDetailAPIView(APIView):
    def get(self, request, seller_id):
        seller = get_object_or_404(Seller, pk=seller_id)
        seller_serializer = SellerSerializer(seller)

        products = Product.objects.filter(seller=seller)
        products_serializer = ProductSerializer(products, many=True)
        response_data = {
            "seller_info": seller_serializer.data,
            "products": products_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AllUsersAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = MyUser.objects.all()
        serializer = AllUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyEmailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            verification_code = VerificationCode.objects.get(user__email=email, code=code)
            if verification_code.expiration_time < timezone.now():
                verification_code.delete()
                return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                verification_code.user.is_active = True
                verification_code.user.save()
                verification_code.delete()
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        except VerificationCode.DoesNotExist:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, id):
        user = get_object(id, MyUser)
        if user:
            user.delete()
            return Response({"User has deleted!"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)


class UserSettingsChangeAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, id):
        user = get_object(id, MyUser)
        serializer = UserSettingsChangeSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductsForAdminAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductsForAdminSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSearchAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        email = request.query_params.get('email', '')
        user = MyUser.objects.filter(email__icontains=email)
        serializer = AllUserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPaginationListView(generics.ListAPIView):

    pagination_class = CustomLimitOffsetPagination
    permission_classes = [permissions.IsAdminUser]
    #
    def get(self, request):
        users = MyUser.objects.all()
        page = self.paginate_queryset(users)

        if page is not None:
            serializer = AllUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(users, many=True)
        return Response(serializer.data)