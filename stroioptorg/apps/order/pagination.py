
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'paginate_by'
    max_page_size = 5

    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number,
            'max_page': self.page.paginator.num_pages,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })