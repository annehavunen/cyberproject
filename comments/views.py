from django.db import connection
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import CommentForm, LoginForm, RegisterForm
from .models import Comment, User
# from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def index(request, user_id):
    # if not request.user.is_authenticated:
    #     return HttpResponseForbidden("Unauthorized")
    # elif request.user.id != user_id:
    #     return HttpResponseForbidden("Unauthorized")

    if 'user_id' not in request.session:
        return HttpResponseForbidden("Unauthorized")
    # current_user_id = request.session.get("user_id")
    # if current_user_id != user_id:
    #     return HttpResponseForbidden("Unauthorized")

    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            Comment.objects.create(user=user, comment_text=text, pub_date=timezone.now())
            form = CommentForm()
    else:
        form = CommentForm()
    comment_list = Comment.objects.order_by('-pub_date')[:30]
    # return render(request, "comments/index.html", {"form": form, "comment_list": comment_list})
    return render(request, "comments/index.html", {"form": form, "comment_list": comment_list, "user": user})


def login_view(request):
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # user = authenticate(request, username=username, password=password)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM comments_user WHERE username = '{username}' AND password = '{password}'")
                # also possible:
                # cursor.execute(f"SELECT * FROM comments_user WHERE username = %s AND password = %s", [username, password])
                user = cursor.fetchone()
            if user is None:
                error_message = "Invalid username or password"
            else:
                # login(request, user)
                request.session["user_id"] = user[0]
                return HttpResponseRedirect(reverse("comments:index", args=(user[0],)))
    else:
        form = LoginForm()
    return render(request, "comments/login.html", {"form": form, "error_message": error_message})


def register_view(request):
    error_message = None
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            if User.objects.filter(username=username).exists():
                error_message = "Username is already in use."
            # else:
            #     try:
            #         validate_password(password)
            #         User.objects.create_user(
            #             username=username,
            #             password=password
            #         )
            #         return HttpResponseRedirect(reverse('comments:login'))
            #     except ValidationError as e:
            #         error_message = " ".join(e)
            else:
                User.objects.create(username=username, password=password)
                return HttpResponseRedirect(reverse('comments:login'))
    else:
        form = RegisterForm()
    return render(request, "comments/register.html", {"form": form, "error_message": error_message})


def logout_view(request):
    # logout(request)
    if 'user_id' in request.session:
        del request.session['user_id']
    return HttpResponseRedirect(reverse('comments:login'))
