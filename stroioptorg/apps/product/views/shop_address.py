from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Region
from apps.product.serializers import ShopAddressesByRegionListSerializer


class ShopAddressesAPIView(APIView):
    def get(self, request):
        addresses = Region.objects.prefetch_related(
            Prefetch(
                'cities__shops_addresses'
            )
        ).all()
        serializer = ShopAddressesByRegionListSerializer(addresses, many=True)
        return Response(serializer.data)
