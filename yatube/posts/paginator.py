from django.core.paginator import Paginator

PAGINATOR_COUNT = 10


def paginator_page(request, queryset):
    return Paginator(
        queryset, PAGINATOR_COUNT).get_page(request.GET.get('page'))
