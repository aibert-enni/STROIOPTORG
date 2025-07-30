from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Region
from apps.product.serializers import ShopAddressesByRegionListSerializer, ShopAddressesSuccessResponseSerializer


class ShopAddressesAPIView(APIView):
    @extend_schema(
        operation_id='get shop address list',
        summary='Получить адреса магазинов компании',
        description='Получаем адреса всех магазинов компании',
        tags=['address'],
        responses={
            200: ShopAddressesSuccessResponseSerializer
        }

    )
    def get(self, request):
        addresses = Region.objects.prefetch_related(
            Prefetch(
                'cities__shops_addresses'
            )
        ).all()
        serializer = ShopAddressesByRegionListSerializer(addresses, many=True)

        return Response({
            'status': 'success',
            'message': 'Адреса магазинов получены',
            'data': serializer.data
        })
