from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema

from .models import *
from .serializers import *


class QuizPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_query_param = "p"
    page_size_query_param = "count"


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = QuizPagination
    permission_class = (IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    serializer.context['is_detail'] = True
    return Response(serializer.data, status=status.HTTP_200_OK)


class QuizListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    pagination_class = QuizPagination
    permission_classes = (IsAuthenticated,)


class QuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    pagination_class = QuizPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)

    search_fields = ['title', "quiz__title", "quiz__category__title", "quiz__category__owner__name"]


class AnswerListCreateAPIView(APIView):
    serializer_class = AnswerSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = QuizPagination

    def get(self, request):
        answer = Answer.objects.all()
        serializer = self.serializer_class(answer, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AnswerSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnswerDetailView(APIView):
    serializer_class = AnswerSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = self.serializer_class(answer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AnswerSerializer)
    def put(self, request, pk, format=None):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = self.serializer_class(instance=answer, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk, format=None):
        answer = get_object_or_404(Answer, pk=pk)
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

