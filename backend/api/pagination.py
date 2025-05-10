from rest_framework.pagination import PageNumberPagination
import constants


class PagesPagination(PageNumberPagination):
    """Класс, ответственный за пагинацию"""

    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = constants.PAGE_SIZE
    max_page_size = constants.MAX_PAGE_SIZE
