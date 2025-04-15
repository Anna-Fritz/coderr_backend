from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class that extends `PageNumberPagination` to define pagination settings for list views.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 50
