from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_image = models.ImageField(upload_to=f"user_photo/%Y/%m/%d/")
    description = models.TextField(blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)  # add this
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return self.user_name


class Content(models.Model):
    description = models.TextField(blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    liked = models.ManyToManyField(User, default=None, blank=True, related_name='liked', null=True)
    time_create = models.DateTimeField(auto_now=True, verbose_name='Час створення')
    tags = models.ManyToManyField('Tag', default=None, blank=True, related_name='tags', null=True)

    def __str__(self):
        return str(self.user)

    @property
    def num_likes(self):
        return self.liked.all().count()

    class Meta:
        ordering = ['-time_create']


LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, null=True)
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)

    def __str__(self):
        return self.content


class Post(models.Model):
    content_id = models.ForeignKey(Content, default=None, on_delete=models.CASCADE, related_name='content_id')
    image = models.ImageField(upload_to='content_photo/%Y/%m/%d/')


class Tag(models.Model):
    tag_name = models.TextField(blank=True)

    def __str__(self):
        return self.tag_name


class Subscribe(models.Model):
    subscribe = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='sub')
    sub_user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='sub_user')


    def __str__(self):
        return self.sub_user
