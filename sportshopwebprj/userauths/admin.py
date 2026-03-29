from django.contrib import admin
from .models import User, ContactUs


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'date_joined')
    ordering = ('-date_joined',)

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'subject', 'message', 'contact_date')
    search_fields = ('email',)
    list_filter = ('contact_date',)
    ordering = ('-contact_date',)

admin.site.register(User, UserAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
