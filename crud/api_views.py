from crud.models import Property, Account, District, Sector, Cell, Village
from crud.serializers import *
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404
from rest_framework import generics, viewsets

class PropertyListx(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        prop= Property.objects.all()[0]
        serializer = PropertySerializer(prop)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PropertySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyApi(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class AccountApi(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class DistrictApi(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class SectorApi(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer


class CellApi(viewsets.ModelViewSet):
    queryset = Cell.objects.all()
    serializer_class = CellSerializer


class VillageApi(viewsets.ModelViewSet):
    queryset = Village.objects.all()
    serializer_class = VillageSerializer
