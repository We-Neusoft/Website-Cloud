from django.contrib import admin

from models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('encoded_user_id', 'client', 'user')

    def encoded_user_id(self, obj):
        return obj.id.encode()
admin.site.register(User, UserAdmin)
