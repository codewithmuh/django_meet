from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    page_size = 10
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link().replace("http", "https") if self.get_next_link() else self.get_next_link()),
            ('previous', self.get_previous_link().replace("http", "https") if self.get_previous_link() else self.get_previous_link()),
            ('results', data)
        ]))

