from django.contrib import admin

from .models import Guest, Invitation, Visit


class GuestAdmin(admin.ModelAdmin):

    list_display = ['name', 'email', 'phone_number']


class InvitationAdmin(admin.ModelAdmin):
    pass


class VisitAdmin(admin.ModelAdmin):
    pass


admin.site.register(Guest, GuestAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Visit, VisitAdmin)
