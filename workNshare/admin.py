from django.contrib import admin
from .models import UserProfile,Follow,Sharing,ProfilePicture

class FollowAdmin(admin.ModelAdmin):
    model = Follow
    raw_id_fields = ('follower', 'followee')

admin.site.register(UserProfile)
admin.site.register(Follow,FollowAdmin)
admin.site.register(Sharing)
admin.site.register(ProfilePicture)
