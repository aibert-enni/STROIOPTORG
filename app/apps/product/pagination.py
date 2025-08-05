from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ProductListPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'paginate_by'
    max_page_size = 24

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'message': 'Каталог получен',
            'data': {
                'current_page': self.page.number,
                'max_page': self.page.paginator.num_pages,
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data,
            },
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'example': 'success'
                },
                'message': {
                    'type': 'string',
                    'example': 'Каталог получен'
                },
                'data': {
                    'type': 'object',
                    'properties': {
                        'current_page': {'type': 'integer', 'example': 2},
                        'max_page': {'type': 'integer', 'example': 10},
                        'count': {'type': 'integer', 'example': 100},
                        'next': {'type': ['string', 'null'], 'format': 'uri', 'example': "http://localhost:8000/api/v1/catalog/elektroinstrument/?page=3&paginate_by=9"},
                        'previous': {'type': ['string', 'null'], 'format': 'uri', 'example': "http://localhost:8000/api/v1/catalog/elektroinstrument/?paginate_by=9"},
                        'results': schema
                    }
                }
            }
        }
