import debug_toolbar
from django.conf.urls import include, re_path
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

urlpatterns = [
    re_path(r"^__debug__/", include(debug_toolbar.urls)),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    re_path(r"^", include("files.urls")),
    re_path(r"^", include("users.urls")),
    re_path(r"^accounts/", include("allauth.account.urls")),
    re_path(r"^api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
]
