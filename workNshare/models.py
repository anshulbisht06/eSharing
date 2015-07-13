from django.db import models
from PIL import Image as img
import math
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from .exceptions import AlreadyExistsError
from .signals import follower_created, following_created, follower_removed, following_removed
from .utilities import ContentTypeRestrictedFileField


'''
Simple User Profile model
'''
class UserProfile(models.Model):
    user = models.OneToOneField(User,related_name="profile")
    dob = models.CharField(max_length=10,blank=False)
  #  picture = models.ImageField(upload_to='profile_images',blank=True)
    gender = models.CharField(blank=False,max_length=10)
    institute = models.CharField(max_length=100,blank=False)
    number = models.CharField(max_length=15,blank=False)

    def __unicode__(self):
        return self.user.username+"profile"




'''Profile Picture model'''
class ProfilePicture(models.Model):
    user = models.OneToOneField(User,related_name="profile picture")
    picture = models.ImageField(upload_to='profile_images',blank=True)

    def __unicode__(self):
        return self.user.username+"profile picture"

    def save(self, *args, **kwargs):
        '''
        Resize the image when size it is greater than 200x180 using Python Imaging Library.
        After resizing, save it with super-sampling done using ANTIALIAS filter.
        '''
        if self.picture:
            super(ProfilePicture, self).save()
            present_width = self.picture.width
            present_height = self.picture.height
            max_width = 200
            max_height = 180
            if(present_width>max_width) or (present_height>max_height):
                filename = str(self.picture.path)
                imageObj = img.open(filename)
                ratio = 1
                if(present_width>max_width):
                    ratio=max_width/float(present_width)
                    present_width=max_width
                    present_height=int(math.floor(float(present_height)*ratio))
                if(present_height>max_height):
                    ratio=ratio*(max_height/float(present_height))
                    present_height=max_height
                    present_width=int(math.floor(float(present_height)*ratio))

                imageObj = imageObj.resize((present_width,present_height),img.ANTIALIAS)
                imageObj.save(filename)


'''default model'''
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


'''caches configuration'''
CACHE_TYPES = {
    'followers': 'fo-%d',
    'following': 'fl-%d',
}

BUST_CACHES = {
    'followers': ['followers'],
    'following': ['following'],
}


def cache_key(type, user_pk):
    """
    Build the cache key for a particular type of cached value
    """
    return CACHE_TYPES[type] % user_pk


def bust_cache(type, user_pk):
    """
    Bust our cache for a given type, can bust multiple caches
    """
    bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % user_pk for k in bust_keys]
    cache.delete_many(keys)




'''
follower-following models & manager
'''
class FollowingManager(models.Manager):
    """ Following manager """

    def followers(self, user):
        """ Return a list of all followers """
        key = cache_key('followers', user.pk)
        followers = cache.get(key)
        if followers is None:
            qs = Follow.objects.filter(followee=user).all()
            followers = [u.follower for u in qs]
            cache.set(key, followers)

        return followers

    def following(self, user):
        """ Return a list of all users the given user follows """
        key = cache_key('following', user.pk)
        following = cache.get(key)

        if following is None:
            qs = Follow.objects.filter(follower=user).all()
            following = [u.followee for u in qs]
            cache.set(key, following)

        return following

    def add_follower(self, follower, followee):
        """ Create 'follower' follows 'followee' relationship """
        if follower == followee:
            raise ValidationError("Users cannot follow themselves")

        relation, created = Follow.objects.get_or_create(follower=follower, followee=followee)

        if created is False:
            raise AlreadyExistsError("User '%s' already follows '%s'" % (follower, followee))

        follower_created.send(sender=self, follower=follower)
        following_created.send(sender=self, follow=followee)

        bust_cache('followers', followee.pk)
        bust_cache('following', follower.pk)

        return relation

    def remove_follower(self, follower, followee):
        """ Remove 'follower' follows 'followee' relationship """
        try:
            rel = Follow.objects.get(follower=follower, followee=followee)
            follower_removed.send(sender=rel, follower=rel.follower)
            following_removed.send(sender=rel, following=rel.followee)
            rel.delete()
            bust_cache('followers', followee.pk)
            bust_cache('following', follower.pk)
            return True
        except Follow.DoesNotExist:
            return False

    def follows(self, follower, followee):
        """ Does follower follow followee? Smartly uses caches if exists """
        followers = cache.get(cache_key('following', follower.pk))
        following = cache.get(cache_key('followers', followee.pk))

        if followers and followee in followers:
            return True
        elif following and follower in following:
            return True
        else:
            try:
                Follow.objects.get(follower=follower, followee=followee)
                return True
            except Follow.DoesNotExist:
                return False


class Follow(models.Model):
    """ Model to represent Following relationships """
    follower = models.ForeignKey(AUTH_USER_MODEL, related_name='following')
    followee = models.ForeignKey(AUTH_USER_MODEL, related_name='followers')
    created = models.DateTimeField(default=timezone.now)

    objects = FollowingManager()

    class Meta:
        verbose_name = _('Following Relationship')
        verbose_name_plural = _('Following Relationships')
        unique_together = ('follower', 'followee')

    def __unicode__(self):
        return "User #%d follows #%d" % (self.follower_id, self.followee_id)

    def save(self, *args, **kwargs):
        #Users can't be friends with themselves
        if self.follower == self.followee:
            raise ValidationError("Users cannot follow themselves.")
        super(Follow, self).save(*args, **kwargs)


'''
Sharing Model
Allowed Type : PDFs,XMLs,ZIPs,BZs,BZ2s,GIFs,PNGs,JPEGs,BMPs,SVGs,HTMLs,TXTs(all plain texts),DOCs,PPTs.
Maximum Size : 5 MB
'''
class Sharing(models.Model):
    allowed_content_types=['application/xml','application/pdf','application/zip','application/x-bzip','application/x-bzip2'
                           'image/gif','image/png','image/jpeg','image/bmp','image/svg+xml',
                           'text/html','text/plain',
                           'application/msword','application/mspowerpoint',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                           ]
    share_from = models.CharField(max_length=30,blank=False)
    share_to = models.CharField(max_length=30,blank=False)
    document = ContentTypeRestrictedFileField(
        upload_to='shared_documents',
        content_types=allowed_content_types,
        max_upload_size=5242880
    )
    message=models.CharField(max_length=120,blank=True)
    shared_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return "User %s shares with %s" % (self.share_from, self.share_to)

    def save(self, *args, **kwargs):
        #Users can't share with themselves
        if self.share_from == self.share_to:
            raise ValidationError("Users cannot share with themselves.")
        super(Sharing, self).save(*args, **kwargs)
