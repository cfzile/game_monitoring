from django.apps import AppConfig
from django.db.models import Q
from django.http import Http404
from django.utils import timezone, dateformat
from django.utils.timezone import localdate

from monitoring import constance
from monitoring.constance import NUM_SERVERS_ON_PAGE
from monitoring.models import Server, Order, Place


class MainConfig(AppConfig):
    name = 'monitoring'


def get_premium_servers():
    server_null = Server()
    server_null.name = "---"
    server_null.ip = "-"
    server_null.port = "-"
    server_null.id = "0"
    server_null.map_name = '-'
    server_null.max_players = '-'
    server_null.player_count = '-'
    NUM_PREMIUM_PLACES = Place.objects.filter(status=1).count()

    premium_servers = [server_null] * NUM_PREMIUM_PLACES

    orders = Order.objects.filter(active=True, place__status=1, date_from__lte=localdate(), date_to__gte=localdate())
    for order in orders:
        order.server.update_info()
        if len(order.server.name) > 30:
            order.server.name = order.server.name[:25] + "..."
        if len(order.server.map_name) > 30:
            order.server.map_name = order.server.map_name[:25] + "..."
        order.server.save()
        premium_servers[order.place.place_number - 1] = order.server

    return premium_servers


def get_disabled_dates(id):
    orders = Order.objects.filter(place_id=id)
    disabled = []

    for order in orders:

        current = order.date_from

        while current <= order.date_to:
            formatted_date = dateformat.format(current, constance.DATE_FORMAT_PYTHON_TO)
            disabled.append(str(formatted_date))
            current = current + timezone.timedelta(days=1)

    return disabled


def get_servers_by_page(page):
    list_servers = Server.objects.all().filter().order_by('status')
    orders = Order.objects.all().order_by('place__place_number').filter(active=True, place__status=0,
                                                                        date_from__lte=timezone.localdate(),
                                                                        date_to__gte=timezone.localdate())

    pages = range(1, len(list_servers) // NUM_SERVERS_ON_PAGE + min(1, len(list_servers) % NUM_SERVERS_ON_PAGE) + 1)

#     if len(list_servers) == 0 and page != 1:
#         raise Http404()

#     servers = []
#     pos = max(0, NUM_SERVERS_ON_PAGE * (page - 1) - len(orders)) + 1

#     updated = 0

#     if page == 1:
#         for order in orders:
#             server = order.server
#             server.position_in_table = pos
#             server.update_info()
#             servers.append(server)
#             list_servers = list_servers.filter(~Q(ip=server.ip, port=server.port))
#             pos += 1

#     list_servers = list_servers[
#                    max(0, NUM_SERVERS_ON_PAGE * (page - 1) - len(orders)):(NUM_SERVERS_ON_PAGE * page - len(orders))]

#     for server in list_servers:

#         server.position_in_table = pos
#         if updated < 0 and server.update_info():
#             updated += 1
#         if server.status == 'connected':
#             servers.append(server)

#         pos += 1
        
#     print('Total:', len(servers))
    
#     return pages, servers

    for server in list_servers[:100]:
        server.update_info()
    return pages, list_servers[:100]


def clear_orders():
    Order.objects.filter(active=False, date_of_create__lt=timezone.localtime() - timezone.timedelta(minutes=3)).delete()
    Order.objects.filter(date_to__lt=timezone.localtime()).delete()


def add_places_():
    for i in range(1, 11):
        Place.objects.create(place_number=i, status=1, game='1.0.0.34', price=25, name='место в топе #%d' % i)

    for i in range(1, 101):
        Place.objects.create(place_number=i, status=0, game='1.0.0.34', price=20, name='место в таблице #%d' % i)
