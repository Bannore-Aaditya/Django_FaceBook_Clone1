from itertools import chain

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowerCount
from itertools import chain

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.all()

    user_followingList = []
    feed = []
    user_following = FollowerCount.objects.filter(followers=request.user.username)

    for user in user_following:
        user_followingList.append(user.user)

    for usernames in user_followingList:
        feedList = Post.objects.filter(user=usernames)
        feed.append(feedList)

    feedLists = list(chain(*feed))

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feedLists})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already registered.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already registered.')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model,id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username not found.')
            return redirect('signup')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    print(user_profile.profile_pic)

    if request.method == 'POST':
        if request.FILES.get('profile_pic')==None:
            image = user_profile.profile_pic
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profile_pic = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            return redirect('settings')
        if request.FILES.get('profile_pic')!=None:
            image = request.FILES['profile_pic']
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profile_pic = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            return redirect('settings')
    return render(request, 'setting.html', {'user_profile':user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(caption=caption, user=user, image=image)
        new_post.save()
        return redirect('/')
    else:
        return redirect("/")
    #return HttpResponse('upload')

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id,username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_postLen = len(user_posts)

    follower = request.user.username
    user = pk
    user_followers = FollowerCount.objects.filter(user=pk).count()
    user_following = FollowerCount.objects.filter(followers=pk).count()
    if FollowerCount.objects.filter(followers=follower,user=user).first():
        button = "Unfollow"
    else:
        button = "Follow"

    context = {
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_postLen': user_postLen,
        'user_object': user_object,
        'button': button,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowerCount.objects.filter(followers=follower,user=user).first():
            delete_follower = FollowerCount.objects.get(followers=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowerCount.objects.create(followers=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile =[]
        username_profile_list = []
        for user in username_object:
            username_profile.append(user.id)

        for id in username_profile:
            profile = Profile.objects.filter(id_user=id)
            username_profile_list.append(profile)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})