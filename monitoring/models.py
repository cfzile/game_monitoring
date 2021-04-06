import os

import a2s
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import timezone, dateformat
from fuzzywuzzy import process
from monitoring import constance
from siteroot import settings


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user', related_query_name='user', on_delete=models.CASCADE,
                                primary_key=True)
    servers = ArrayField(models.IntegerField(null=True, blank=True), null=True, default=[])
    avatar = models.ImageField(upload_to='monitoring/users_avatar/', blank=True,
                               null=True, default='monitoring/users_avatar/default.jpg')

    def get_absolute_url(self):
        return reverse("profile", kwargs={"user_id": self.user_id})


class Server(models.Model):
    ip = models.CharField(max_length=15)
    port = models.IntegerField()
    gameType = models.CharField(max_length=20, null=True)
    map_name = models.CharField(max_length=50, null=True)
    gameVersion = models.CharField(max_length=15, null=True)
    name = models.CharField(max_length=100, null=True)
    max_players = models.IntegerField(null=True)
    player_count = models.IntegerField(null=True)
    num_points = models.IntegerField(default=0)
    state = models.IntegerField(null=True)
    status = models.CharField(default="disconnected", max_length=20)
    owner = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True)
    position_in_table = models.IntegerField()
    date_last_update = models.DateTimeField(default=timezone.localtime)
    ordered = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='monitoring/servers_avatar/', blank=True,
                               null=True, default='monitoring/servers_avatar/free_place.jpg')

    def __str__(self):
        return self.ip + ":" + str(self.port)

    def update_info(self):

        if timezone.localtime().timestamp() - self.date_last_update.timestamp() < 60 and (self.name is not None):
            return False

        if Order.objects.filter(place=1, server=self.id, date_from__gte=timezone.localtime(),
                                date_to__lte=timezone.localtime()):
            self.ordered = True
        else:
            self.ordered = False

        try:

            address = (self.ip, int(self.port))
            info = a2s.info(address, timeout=0.5)

            self.player_count = info.player_count
            self.max_players = info.max_players
            self.map_name = info.map_name
            self.name = info.server_name
            self.status = "connected"
            self.date_last_update = timezone.localtime()

            a = process.extract(self.map_name, os.listdir(settings.BASE_DIR + "/media/monitoring/servers_avatar/"))
            a = sorted(a, key=lambda x: x[1])

            print(self.map_name, a[-1])
#             if a[-1][1] > 70:
#                 self.avatar = "monitoring/servers_avatar/" + a[-1][0]
#             else:
#                 self.avatar = "monitoring/servers_avatar/no_screenshot.jpg"

            self.save()

        except:

            self.status = "disconnected"
            if self.ordered == False and (self.name is not None) and timezone.localtime().timestamp() - self.date_last_update.timestamp() > 60 * 60 * 24 * 3:
                self.delete()

            return False

        return True


class Place(models.Model):
    game = models.CharField(max_length=50, default='')
    place_number = models.IntegerField(default=0, null=False)
    price = models.IntegerField(default=0)
    name = models.CharField(max_length=50, default='')
    status = models.IntegerField(default=0)
    disabled_dates = ArrayField(models.CharField(max_length=50, null=False), null=True)

    def update_disabled_dates(self):
        orders = Order.objects.filter(place__id=self.id)
        self.disabled_dates = []

        for order in orders:

            current = order.date_from

            while current <= order.date_to:
                formatted_date = dateformat.format(current, constance.DATE_FORMAT_PYTHON_TO)
                self.disabled_dates.append(str(formatted_date))
                current = current + timezone.timedelta(days=1)

        self.save()


class Order(models.Model):
    server = models.ForeignKey('Server', on_delete=models.CASCADE, null=False)
    date_creation = models.DateTimeField(default=timezone.localtime)
    date_from = models.DateField(default=timezone.localtime, null=False)
    date_to = models.DateField(default=timezone.localtime, null=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, default=0)
    active = models.BooleanField(default=False)
    date_of_create = models.DateTimeField(default=timezone.localtime)
    order_id = models.CharField(max_length=50, null=False, default=0)
    sum = models.IntegerField(default=0, null=False)
    email = models.EmailField()
