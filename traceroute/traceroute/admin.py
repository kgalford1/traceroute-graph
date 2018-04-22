from django.contrib import admin
from traceroute.models import Target, Partner, Location, Time


class LocationInline(admin.TabularInline):
    model = Location
    extra = 0


class AddTargetInline(admin.TabularInline):
    model = Target
    extra = 1
    verbose_name_plural = 'Add Targets'

    def has_change_permission(self, request, obj=None):
        return False


class TargetInline(admin.TabularInline):
    model = Target
    extra = 0
    readonly_fields = ('ip_address',)
    verbose_name_plural = 'Current Targets'

    def has_add_permission(self, request):
        return False


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (LocationInline,)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('partner', 'location',)
    inlines = (AddTargetInline, TargetInline,)


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ('rrd_graph_time',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

