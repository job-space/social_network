from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import json
from app.forms import *
from app.models import *
from .tokens import account_activation_token


@csrf_exempt
@login_required
def view_content(request):
    content_all = Content.objects.select_related('user', 'profile')
    user = request.user
    context = {
        'content_all': content_all,
        'user': user,

    }
    return render(request, 'view_content/main.html', context=context)


@csrf_exempt
def like_content(request):
    user = request.user

    if request.method == 'POST':
        content_id = request.POST.get('content_id')
        content_obj = Content.objects.get(id=content_id)

        if user in content_obj.liked.all():
            content_obj.liked.remove(user)
            liked = False
        else:
            content_obj.liked.add(user)
            liked = True

        total_likes = content_obj.liked.all().count()
        ctx = {"likes_count": total_likes, "liked": liked, "content_id": content_id}
    return HttpResponse(json.dumps(ctx), content_type='application/json')


@csrf_exempt
@login_required
def add_content(request):
    if request.method == "POST":
        add_content = request.POST.get('add_content')
        if add_content != 'True':
            user = request.user
            images = request.FILES.getlist('image')
            if images == []:
                context = {'warning': 'Please add photo'}
                return render(request, 'add_content/add_content.html', context=context)
            content = Content.objects.create(profile=user.profile)
            for image in images:
                Post.objects.create(image=image, content_id=content)

        return render(request, 'add_content/add_content.html', {'user_login': request.user})


class CreateUserProfile(CreateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'profile/create_user_profile.html'
    success_url = reverse_lazy('profile')


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user_email = form.cleaned_data.get('email')
                User.objects.get(email=user_email)
                confirm = 'User with this email address already exists.'
                return render(request, 'registration/signup.html', {'form': form, 'confirm': confirm})

            except:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                message = render_to_string('registration/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                mail_subject = 'Activate your blog account.'
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                return redirect(to='login')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@csrf_exempt
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect(to='app:create_user_profile')
    else:
        return HttpResponse('Activation link is invalid!')


@csrf_exempt
@login_required
def view_profile(request, username):

    user = User.objects.get(username=username)
    profile = Profile.objects.get(id=user.profile.id)
    user = User.objects.get(id=profile.user_id)
    sub = Subscribe.objects.filter(subscribe_id=request.user.id)

    content_all = Content.objects.filter(profile_id=profile.id)

    sub_user = []
    for users in sub:
        sub_user.append(users.sub_user)

    args = {'content_all': content_all,
            'profile': profile,
            'user_login': user,
            'user': request.user,
            'sub_user': sub_user}
    return render(request, 'profile/profile.html', args)


@csrf_exempt
@login_required
def profile(request):
    change_profile = request.POST.get('change_profile')
    if change_profile != 'True':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if profile_form.is_valid():
            profile_form.save()

            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='app:view_content')

    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'profile/create_user_profile.html', {'profile_form': profile_form, 'user': request.user})


@csrf_exempt
@login_required
def tag(request):
    if request.method == 'POST':
        tag = request.POST.get('tag')
        content_id = request.POST.get('content_id')
        content_id = int(content_id)
        content = Content.objects.get(id=content_id)

        for t in tag.split('#'):
            try:
                tag_obj = Tag.objects.get(tag_name=t)
            except:
                tag_obj = Tag.objects.create(tag_name=t)

            content.tags.add(tag_obj.id)

    user = request.user
    context = {
        'content': content,
        'user': user,
    }
    return render(request, 'view_content/post.html', context=context)


@csrf_exempt
@login_required
def view_tag(request):
    if request.method == 'POST':
        tag_name = request.POST.get('tag')
        tag = Tag.objects.get(tag_name=tag_name)
        tag_name_id = tag.id
        contents = Content.objects.filter(tags=tag_name_id)
        context = {
            'tag_name': tag_name,
            'contents': contents
        }
        return render(request, 'view_content/view_tag.html', context=context)


@csrf_exempt
@login_required
def post(request, content):
    content = Content.objects.get(id=content)
    user = request.user
    context = {
        'content': content,
        'user': user,
    }
    return render(request, 'view_content/post.html', context=context)


@csrf_exempt
def subscribe(request):
    user = request.user
    subscribe_user = request.POST.get('subscribe_user')
    subscribe_user = User.objects.get(id=int(subscribe_user))

    try:
        sub = Subscribe.objects.get(subscribe_id=user.id, sub_user_id=subscribe_user.id)
        sub.delete()
        subscribe = False
    except:
        try:
            sub_user = Subscribe.objects.get(sub_user=subscribe_user)
        except:
            sub_user = Subscribe.objects.create(sub_user=subscribe_user)
        user.sub.add(sub_user)
        subscribe = True


    ctx = {'subscribe': subscribe}
    return HttpResponse(json.dumps(ctx), content_type='application/json')


@csrf_exempt
@login_required
def followers(request):
    user = request.user
    sub_users_ids = Subscribe.objects.filter(sub_user_id=user.id)
    sub_user_list = []
    for sub_user in sub_users_ids:
        sub_user_list.append(Content.objects.filter(profile_id = sub_user.subscribe_id))

    return render(request, 'subscribe/following.html', {'content_all': sub_user_list,
                                                        'user': user,
                                                        'type_follow': 'Followers'})


@csrf_exempt
@login_required
def following(request):
    user = request.user
    sub_users_ids = Subscribe.objects.filter(subscribe_id=user.id)
    sub_user_list = []
    for sub_user in sub_users_ids:
        sub_user_list.append(Content.objects.filter(profile_id=sub_user.sub_user_id))

    return render(request, 'subscribe/following.html', {'content_all': sub_user_list,
                                                        'type_follow': 'Following',
                                                        'user': user})
