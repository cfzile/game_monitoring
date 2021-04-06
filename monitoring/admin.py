from django.contrib import admin
from django.db.models import F
from django.utils.safestring import mark_safe

from monitoring.models import *


class ServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ip', 'port', 'status', 'date_last_update', 'position_in_table')
    ordering = ('name',)
    fields = ('id', 'name', 'ip', 'port', 'status', 'owner', 'date_last_update', 'position_in_table')
    readonly_fields = ('id', 'name')
    # view_on_site = True


class UserInline(admin.TabularInline):
    model = User
    fields = ('username', 'email')
    ordering = ('username',)
    show_change_link = True


class ProfileAdmin(admin.ModelAdmin):

    def user_link(self, obj):
        return mark_safe('<a href="/admin/auth/user/%s/change">%s</a>' % (obj.user_id, obj.user))

    user_link.allow_tags = True
    user_link.short_description = 'User edit'

    list_display = ('user_id', 'user', 'servers')
    ordering = ('user',)
    fields = ['user_link', 'servers']
    readonly_fields = ['user_link', ]
    list_display_links = ('user',)
    view_on_site = True


class OrderAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    list_display = ('id', 'server', 'place_id', 'date_from', 'date_to', 'sum')
    ordering = ('date_from',)
    fields = ('server', 'place_id', 'date_from', 'date_to', 'sum')
    readonly_fields = ('sum', 'date_from', 'date_to')


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('game', 'place_number', 'status', 'name')
    ordering = ('status', 'place_number')
    fields = ('game', 'place_number', 'status', 'name')


admin.site.register(Server, ServerAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Place, PlaceAdmin)
