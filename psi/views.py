from functools import partial
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import request, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes

from drf_yasg.utils import swagger_auto_schema

from psi.decorators import validate_datetime

from .models import Psi, AirTemperature
from .serializers import PsiSerializer, AirTemperatureSerializer, SearchDateSerializer
from .decorators import validate_datetime


class PsiPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 200
    page_query_param = "p"
    page_size_query_param = "count"


class PsiViewSet(ModelViewSet):
    serializer_class = PsiSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Psi.objects.all()
    pagination_class = PsiPagination

    @swagger_auto_schema(request_body=SearchDateSerializer)
    @action(methods=['POST'], detail=False)
    @validate_datetime
    def search(self, request, *args, **kwargs):
        param = kwargs['param']
        
        if param.get('type') == "date":
            data = Psi.objects.filter(updated_timestamp__date=param.get("value"))
        elif param.get("type") == "datetime":
            data = Psi.objects.filter(updated_timestamp=param.get("value"))

        if not data.exists():
            data = Psi.objects.filter(updated_timestamp__date=Psi.objects.latest("updated_timestamp").updated_timestamp.date())

        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirTemperatureViewSet(ViewSet):
    serializer_class = AirTemperatureSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        air_temperatures = AirTemperature.objects.all()
        serializer = self.serializer_class(air_temperatures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AirTemperatureSerializer)    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        serializer = self.serializer_class(air_temperature)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AirTemperatureSerializer)        
    def update(self, request, pk=None):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        serializer = self.serializer_class(instance=air_temperature, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=AirTemperatureSerializer)        
    def partial_update(self, request, pk=None):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        serializer = self.serializer_class(instance=air_temperature, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        air_temperature.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=SearchDateSerializer)
    @action(methods=['POST'], detail=False)
    @validate_datetime
    def search(self, request, *args, **kwargs):
        param = kwargs['param']
        
        if param.get('type') == "date":
            data = AirTemperature.objects.filter(timestamp__date=param.get("value"))
        elif param.get("type") == "datetime":
            data = AirTemperature.objects.filter(timestamp=param.get("value"))

        if not data.exists():
            data = AirTemperature.objects.filter(timestamp__date=AirTemperature.objects.latest("timestamp").timestamp.date())

        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)