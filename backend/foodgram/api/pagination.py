from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пагинация для API."""
    page_size_query_param = 'limit'
