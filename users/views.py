from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import (
    FileUploadParser,
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from cms.permissions import IsUserOrManager
from files.methods import is_mediacms_manager

from .forms import ChannelForm, UserForm
from .models import Channel, User
from .serializers import LoginSerializer, UserDetailSerializer, UserSerializer


def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None


def view_user(request, username):
    context = {}
    user = get_user(username=username)
    if not user:
        return HttpResponseRedirect("/")
    context["user"] = user
    context["CAN_EDIT"] = True if ((user and user == request.user) or is_mediacms_manager(request.user)) else False
    context["CAN_DELETE"] = True if is_mediacms_manager(request.user) else False
    return render(request, "cms/user.html", context)


def view_user_media(request, username):
    context = {}
    user = get_user(username=username)
    if not user:
        return HttpResponseRedirect("/")

    context["user"] = user
    context["CAN_EDIT"] = True if ((user and user == request.user) or is_mediacms_manager(request.user)) else False
    context["CAN_DELETE"] = True if is_mediacms_manager(request.user) else False
    return render(request, "cms/user_media.html", context)


def view_user_playlists(request, username):
    context = {}
    user = get_user(username=username)
    if not user:
        return HttpResponseRedirect("/")

    context["user"] = user
    context["CAN_EDIT"] = True if ((user and user == request.user) or is_mediacms_manager(request.user)) else False
    context["CAN_DELETE"] = True if is_mediacms_manager(request.user) else False

    return render(request, "cms/user_playlists.html", context)


def view_user_about(request, username):
    context = {}
    user = get_user(username=username)
    if not user:
        return HttpResponseRedirect("/")

    context["user"] = user
    context["CAN_EDIT"] = True if ((user and user == request.user) or is_mediacms_manager(request.user)) else False
    context["CAN_DELETE"] = True if is_mediacms_manager(request.user) else False

    return render(request, "cms/user_about.html", context)


@login_required
def edit_user(request, username):
    user = get_user(username=username)
    if not user or (user != request.user and not is_mediacms_manager(request.user)):
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = UserForm(request.user, request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return HttpResponseRedirect(user.get_absolute_url())
    else:
        form = UserForm(request.user, instance=user)
    return render(request, "cms/user_edit.html", {"form": form})


def view_channel(request, friendly_token):
    context = {}
    channel = Channel.objects.filter(friendly_token=friendly_token).first()
    if not channel:
        user = None
    else:
        user = channel.user
    context["user"] = user
    context["CAN_EDIT"] = True if ((user and user == request.user) or is_mediacms_manager(request.user)) else False
    return render(request, "cms/channel.html", context)


@login_required
def edit_channel(request, friendly_token):
    channel = Channel.objects.filter(friendly_token=friendly_token).first()
    if not (channel and request.user.is_authenticated and (request.user == channel.user)):
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = ChannelForm(request.POST, request.FILES, instance=channel)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.save()
            return HttpResponseRedirect(request.user.get_absolute_url())
    else:
        form = ChannelForm(instance=channel)
    return render(request, "cms/channel_edit.html", {"form": form})


class UserList(APIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    parser_classes = (JSONParser, MultiPartParser, FormParser, FileUploadParser)

    def get(self, request, format=None):
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        users = User.objects.filter()
        location = request.GET.get("location", "").strip()
        if location:
            users = users.filter(location=location)

        page = paginator.paginate_queryset(users, request)

        serializer = UserSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class UserDetail(APIView):
    """"""

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsUserOrManager)
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    def get_user(self, username):
        try:
            user = User.objects.get(username=username)
            # this need be explicitly called, and will call
            # has_object_permission() after has_permission has succeeded
            self.check_object_permissions(self.request, user)
            return user
        except PermissionDenied:
            return Response({"detail": "not enough permissions"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "user does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, username, format=None):
        # Get user details
        user = self.get_user(username)
        if isinstance(user, Response):
            return user

        serializer = UserDetailSerializer(user, context={"request": request})
        return Response(serializer.data)

    def post(self, request, username, format=None):
        # USER
        user = self.get_user(username)
        if isinstance(user, Response):
            return user

        serializer = UserDetailSerializer(user, data=request.data, context={"request": request})
        if serializer.is_valid():
            logo = request.data.get("logo")
            if logo:
                serializer.save(logo=logo)
            else:
                serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, uid, format=None):
        # ADMIN
        user = self.get_user(uid)
        if isinstance(user, Response):
            return user

        if not request.user.is_superuser:
            return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get("action")
        if action == "feature":
            user.is_featured = True
            user.save()
        elif action == "unfeature":
            user.is_featured = False
            user.save()

        serializer = UserDetailSerializer(user, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, username, format=None):
        # Delete a user
        user = self.get_user(username)
        if isinstance(user, Response):
            return user

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserWhoami(generics.RetrieveAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserDetailSerializer

    def get_object(self):
        return User.objects.get(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        return super(UserWhoami, self).get(request, *args, **kwargs)


class UserToken(APIView):
    parser_classes = (JSONParser,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        token = Token.objects.filter(user=request.user).first()
        if not token:
            token = Token.objects.create(user=request.user)

        return Response({'token': str(token)}, status=200)


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    def post(self, request):
        data = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
