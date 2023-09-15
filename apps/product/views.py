from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import permissions, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.user.models import Customer
from .serializers import ProductSerializer, CartSerializer, CommentSerializer, CartDetailSerializer, PaymentSerializer
from .models import Product, Cart, Category, Comment
from apps.user.permissions import IsSellerPermission, IsOwnerOrReadOnly
from .pagination import CustomLimitOffsetPagination
import stripe
from django.conf import settings
from django.core.cache import cache

def get_object(id: int, table):
    try:
        return table.objects.get(id=id)
    except table.DoesNotExist:
        raise Http404


class ProductCreateAPIView(APIView):
    permission_classes = [IsSellerPermission]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            category_id = request.data['category']
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                name=request.data['name'],
                description=request.data['description'],
                price=request.data['price'],
                category=category,
                seller_id=request.data['seller'],
            )
            product.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = cache.get("product_list")

        if not products:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            cache.set("product_list", serializer.data, timeout=3600)

        return Response(products, status=status.HTTP_200_OK)


class ProductDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        product = get_object(id, Product)
        serializer = ProductSerializer(product)
        product.views_by += 1
        product.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductUpdateAPIView(APIView):
    permission_classes = [IsSellerPermission, IsOwnerOrReadOnly]

    def put(self, request, id):
        product = get_object(id, Product)
        if 'seller' in request.data and int(request.data['seller']) != product.seller_id:
            return Response({"error": "You cannot change the seller ID."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteAPIView(APIView):
    permission_classes = [IsSellerPermission, IsOwnerOrReadOnly, permissions.IsAdminUser]

    def delete(self, request, id):
        product = get_object(id, Product)
        if product:
            product.delete()
            return Response({"message": "Deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)


class AddToCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user_id = request.user.customer
        try:
            cart = Cart.objects.get(customer_id=user_id)
        except Cart.DoesNotExist:
            raise Http404
        serializer = CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartDetailAPIView(APIView):
    def get(self, request):
        customer = request.user.customer
        try:
            cart = Cart.objects.get(customer=customer)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartDetailSerializer(cart)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductRatingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        product = get_object_or_404(Product, id=id)
        customer = get_object_or_404(Customer, id=request.user.id)
        new_rating = float(request.data.get('rating', 0))
        if 1 <= new_rating <= 5:
            existing_rating = product.ratings.filter(customer=customer).first()
            if existing_rating:
                product.total_rating_points -= existing_rating.rating
                product.total_ratings -= 1
            product.total_ratings += 1
            product.total_rating_points += new_rating
            product.rating = product.total_rating_points / product.total_ratings
            product.save()
            if existing_rating:
                existing_rating.rating = new_rating
                existing_rating.save()
            else:
                product.ratings.create(customer=customer, rating=new_rating)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid rating value. Rating should be between 1 and 5."},
                            status=status.HTTP_400_BAD_REQUEST)


class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.user.id
            try:
                customer = Customer.objects.get(id=user_id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer.save(customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductPaginationListView(generics.ListAPIView):
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [permissions.AllowAny]
    #
    def get(self, request):
        products = Product.objects.all()
        page = self.paginate_queryset(products)

        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductSearchAPIView(APIView):
    def get(self, request):
        name = request.query_params.get('name', '')
        products = Product.objects.filter(name__contains=name)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        product = get_object(id, Product)

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                charge = stripe.Charge.create(
                    amount=serializer.validated_data['amount'],
                    currency=serializer.validated_data['currency'],
                    source=serializer.validated_data['stripe_token']
                )
                amount = request.data.get('amount')
                if product.price > amount:
                    return Response({"message": "Не хватает средств"})
                product.sold += 1
                product.save()
                return Response({'message': 'Оплата прошла успешно'}, status=status.HTTP_200_OK)
            except stripe.error.StripeError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCommentsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommentSerializer

    def get_queryset(self):
        product_id = self.kwargs['id']
        return Comment.objects.filter(product_id=product_id)


    # select_releated, future_releated