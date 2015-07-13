from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext
from .form import UserForm,UserProfileForm,SharingForm,ProfilePictureForm
from .models import UserProfile,Sharing,ProfilePicture
from django.template import Context, loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login,get_user
from django.views.decorators.debug import sensitive_variables,sensitive_post_parameters
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from collections import defaultdict
from .utilities import age
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .exceptions import AlreadyExistsError
from .models import Follow



'''
Registration View
'''
@sensitive_post_parameters()
def register(request):
    context = RequestContext(request)
    registered = False
    registration_errors=False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
        else:
            registration_errors=True
        return render_to_response(
            'template_files/welcome.html',
            {'user_form': user_form,'registered': registered,'registration_errors':registration_errors},
            context)
    return HttpResponseRedirect('/')



'''
Login View
'''
@sensitive_variables('username','password')
@sensitive_post_parameters()
def login(request):
    context = RequestContext(request)
    details_invalid=False
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request,user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("<strong>Your e-Sharing account is disabled.</strong><br><a href='/signup/'>Register Again.</a>")
        else:
            details_invalid=True
            return render_to_response('template_files/login.html',{'details_invalid':details_invalid},context)

'''
followers & following
'''
def followers(username):
    """ List this user's followers """
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.followers(user)
    return followers


def following(username):
    """ List who this user follows """
    user = get_object_or_404(User, username=username)
    following = Follow.objects.following(user)

    return following



'''
Home Page View
'''
@sensitive_variables('username')
def home_page(request):
    context_dict=defaultdict(str)
    context = RequestContext(request)
    authenticated=False
    logged_user=get_user(request)
    share_form=SharingForm()
    profile_form = UserProfileForm()
    profile_picture_form = ProfilePictureForm()
    if not logged_user.is_authenticated():
        context_dict['authenticated']=authenticated
        registered = False
        registration_errors=False
        user_form = UserForm()
        return render_to_response(
            'template_files/welcome.html',
            {'user_form': user_form,'registered': registered,'registration_errors':registration_errors},
            context)
    else:
        context_dict['followers']=followers(logged_user)
        context_dict['following']=following(logged_user)
        userprofile=UserProfile.objects.filter(user=logged_user)
        if userprofile:
            userprofile=UserProfile.objects.filter(user=logged_user)
            for p in userprofile:
                context_dict['age']=age(p.dob)
                context_dict['gender']=p.gender
                context_dict['institute']=p.institute
                context_dict['number']=p.number
            context_dict['dob']=p.dob
            initial_values={'dob':context_dict['dob'],'gender':context_dict['gender'],'institute':context_dict['institute'],'number':context_dict['number']}
            profile_form = UserProfileForm(initial=initial_values)
        userprofile=ProfilePicture.objects.filter(user=logged_user)
        if userprofile:
            for p in userprofile:
                context_dict['profile_picture']=p.picture
        userprofile=User.objects.filter(username__iexact=logged_user)
        for p in userprofile:
            context_dict['email']=p.email
            context_dict['name']=p.first_name
        context_dict['authenticated']=True
        share_to=Sharing.objects.filter(share_from=logged_user).order_by('-shared_at')
        context_dict['share_summary']=share_to
        share_from=Sharing.objects.filter(share_to=logged_user).order_by('-shared_at')
        context_dict['share_home']=share_from
        return render_to_response('template_files/welcome.html',{'user_info':context_dict,'profile_form':profile_form,'profile_picture_form':profile_picture_form,'share_form':share_form},context)
    return HttpResponseRedirect('/')

'''
Update Details except Profile Picture View
'''
@transaction.atomic
@login_required
def update_profile(request):
    _username_object=get_user(request)
    userprofile=UserProfile.objects.filter(user=_username_object)
    if request.method == 'POST':
        if userprofile:
            userprofile.delete()
        profile_form = UserProfileForm(data=request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = _username_object
            profile.save()
            return HttpResponseRedirect('/')
    else:
        return HttpResponse(json.dumps({"Error in updating details.Try once again"}),content_type="application/json")



'''
Update Profile Picture View
'''
@transaction.atomic
@login_required
def update_profile_picture(request):
    _username_object=get_user(request)
    userprofile=ProfilePicture.objects.filter(user=_username_object)
    if request.method == 'POST':
        if userprofile:
            for p in userprofile:
                if p.picture!='profile_images/default_DP.png':
                    p.picture.delete()
            userprofile.delete()
        profile_picture_form = ProfilePictureForm(data=request.POST)
        if profile_picture_form.is_valid():
            picture = profile_picture_form.save(commit=False)
            picture.user = _username_object
            if 'picture' in request.FILES:
                picture.picture = request.FILES.get('picture')
            else:
                return profile_picture_form.errors
            picture.save()
            return HttpResponseRedirect('/')
    else:
        return HttpResponse(json.dumps({"Error in updating details.Try once again"}),content_type="application/json")






'''
#Auto-complete View for guessing all users
'''
def guess_users(request):
    if 'query' in request.GET:
        q = request.GET.get('query')
        usernames_list=[]
        user_dict={}
        user_object=User.objects.all().filter(first_name__icontains=q)
        for user in user_object:
            usernames_list.append(user.first_name)
        user_dict['options']=usernames_list
        data=json.dumps(user_dict)
        return HttpResponse(data, content_type='application/json')
    return HttpResponse()




'''
#Find User Object View
'''
@login_required
def find(request):
    context_dict={}
    context_dict['authenticated']=True
    context = RequestContext(request)
    searched_user_name=request.GET['searched_user']
    context_dict['searched_user_name']=searched_user_name
    user_objects=User.objects.all().filter(first_name__icontains=searched_user_name)
    context_dict['found_users']=user_objects

    page_size=0
    if len(user_objects)<=30:
        page_size=6
    else:
        page_size=10
    paginator = Paginator(user_objects, page_size)
    page = request.GET.get('page')
    context_dict['page_value']=page
    try:
        context_dict['total_list'] = paginator.page(page)
    except PageNotAnInteger:
        context_dict['total_list'] = paginator.page(1)
    except EmptyPage:
        context_dict['total_list'] = paginator.page(paginator.num_pages)
    return render_to_response('template_files/search_users_result.html',{'user_info':context_dict},context)

'''
#Searched User's Profile View
'''
@login_required
def show_profile(request,searched_username):
    logged_user=get_user(request)
    if searched_username==logged_user.username:
        return HttpResponseRedirect('/')
    context_dict={}
    matched=False
    context = RequestContext(request)
    context_dict['searched_username']=searched_username
    followers_list=followers(searched_username)
    share_form=SharingForm()
    if logged_user in followers_list:
        connected=True
        context_dict['followers_list']=followers_list
        context_dict['following_list']=following(searched_username)
    else:
        connected=False
    if request.method == 'POST':
        followee = User.objects.get(username__iexact=searched_username)
        follower = request.user
        try:
            Follow.objects.add_follower(follower, followee)
            connected=True
            return HttpResponseRedirect('/profile/'+searched_username)
        except AlreadyExistsError:
            connected=True
    context_dict['profile_picture']=False
    user=User.objects.filter(username=searched_username)
    userprofile=UserProfile.objects.filter(user=user)
    if userprofile:
        for p in userprofile:
            context_dict['institute']=p.institute
            context_dict['number']=p.number
            context_dict['gender']=p.gender
            context_dict['dob']=p.dob
        context_dict['age']=age(context_dict['dob'])
    userprofile=ProfilePicture.objects.filter(user=user)
    if userprofile:
        for p in userprofile:
            context_dict['profile_picture']=p.picture
    if not context_dict['profile_picture']:
        context_dict['profile_picture']='profile_images/default_DP.png'
    if user:
        matched=True
        for p in user:
            context_dict['name']=p.first_name
            context_dict['email']=p.email
    else:
        matched=False
    context_dict['matched']=matched
    context_dict['already_connected']=connected
    return render_to_response('template_files/user_profile.html',{'profile':context_dict,'share_form':share_form},context)


'''
auto-complete for friends
'''
def guess_friends(request):
    if 'query' in request.GET:
        usernames_list=[]
        user_dict={}
        user_object=following(get_user(request))
        for user in user_object:
            usernames_list.append(user.username)
        user_dict['options']=usernames_list
        data=json.dumps(user_dict)
        return HttpResponse(data, content_type='application/json')
    return HttpResponse()



'''
Sharing Action View from home page
'''
@transaction.atomic
@login_required
def share(request):
    relation=False
    logged_user=get_user(request)
    _followee=following(logged_user)
    share_to=request.POST['share_to']
    user_exist=User.objects.filter(username__iexact=share_to)
    if not user_exist:
        return HttpResponse('<h2>Account doesn\'t exist.</h2>')
    for user in _followee:
        if user.username==share_to:
            relation=True
            break
    if relation:
        if request.method == 'POST':
            share_form = SharingForm(request.POST,request.FILES)
            if share_form.is_valid():
                share = share_form.save(commit=False)
                share.share_from = logged_user
                if 'document' in request.FILES:
                    share.document = request.FILES['document']
                share.save()
                return HttpResponseRedirect('/')
            else:
                print(share_form.errors)

    else:
        return StreamingHttpResponse('<h2>To share  something with user, you need to follow ' +share_to+\
                            '. <a href="/profile/'+share_to+'/">Visit Profile</a>.</h2>')


def error404(request):
    # 1. Load models for this view
    #from idgsupply.models import My404Method

    # 2. Generate Content for this view
    template = loader.get_template('404.html')
    context = Context({
        'message': 'All: %s' % request,
        })

    # 3. Return Template for this view + Data
    return HttpResponse(content=template.render(context), content_type='text/html; charset=utf-8', status=404)
