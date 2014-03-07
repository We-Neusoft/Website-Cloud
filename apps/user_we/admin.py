from django.contrib import admin

from models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('encoded_user_id', 'user')

    def encoded_user_id(self, obj):
        return obj.user.encode()
admin.site.register(User, UserAdmin)
