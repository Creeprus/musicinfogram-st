from rest_framework.pagination import PageNumberPagination


class PagesPagination(PageNumberPagination):
    """Класс, ответственный за пагинацию"""
    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = 6
    max_page_size = 100

    def get_paginated_response(self, data):
        """Функция, которая возвращает спагинированную страницу"""
        response = super().get_paginated_response(data)
        response.data['count'] = self.page.paginator.count
        response.data['next'] = self.get_next_link()
        response.data['previous'] = self.get_previous_link()
        response.data['results'] = data
        return response
