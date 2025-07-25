from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Region, City, Address
from apps.users.serializers import RegionSerializer, AddressSerializer, CitySerializer, CreateAddressSerializer


class GetRegionListView(APIView):

    def get(self, request):
        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)


class GetCitiesListView(APIView):
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)


class UserDeliveryAddress(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        address = get_object_or_404(Address, user=request.user)
        serializer = AddressSerializer(address,
                                       context={'phone_number': request.user.phone_number, 'email': request.user.email})
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateAddressSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        address = get_object_or_404(Address, user=request.user)
        serializer = CreateAddressSerializer(address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        address = get_object_or_404(Address, user=request.user)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

