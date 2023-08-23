from rest_framework.pagination import PageNumberPagination

from core import constants


class LimitPageNumberPagination(PageNumberPagination):
    '''Show 6 recipes'''
    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
