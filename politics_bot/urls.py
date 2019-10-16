from django.contrib import admin
from django.urls import path

from candidates.views import SlackAPIResponderView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('slack-listener/', SlackAPIResponderView.as_view())
]
