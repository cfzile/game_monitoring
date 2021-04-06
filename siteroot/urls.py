from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from monitoring import views

handler404 = 'monitoring.views.handler404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.monitoring_table),
    path('monitor/<int:page>', views.monitoring_table, name='monitoring_table'),
    # path('sign_in', views.sign_in, name='sign_in'),
    # path('sign_up', views.sign_up, name='sign_up'),
    # path('sign_out', views.sign_out, name='sign_out'),
    path('u<int:user_id>', views.profile, name='profile'),
    path('s<int:server_id>', views.server_profile, name='server_profile'),
    path('add_server', views.add_server, name='add_server'),
    path('buy_place', views.buy_place, name='buy_place'),
    path('add_voice', views.add_voice, name='add_voice'),
    path('add_all_servers', views.add_all_servers, name='add_all_servers'),
    path('success_payment', views.success_payment, name='success_payment'),
    path('failed_payment', views.failed_payment, name='failed_payment'),
    # path('faq', views.faq, name='faq'),
    path('offer', views.offer, name='offer'),
    path('rules', views.rules, name='rules'),
    path('add_places', views.add_places, name='add_places'),
    path('PgP4YgOG2PNStqQnWt5MeeYXkwICL157WnLsOBqnrPaTwnN243wkspfCljKlBmtMeRTF5NO5H2cBXQq5owdKjjefK3oxdzhkxEFO', views.payment_result, name='result_payment'),

    path(
        "robots.txt",
        TemplateView.as_view(template_name="monitoring/robots.txt", content_type="text/plain"),
    ),

    path(
        "favicon.ico",
        TemplateView.as_view(template_name="monitoring/favicon.ico", content_type="image/x-icon"),
    ),
]