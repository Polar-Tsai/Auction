from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls), # Disabled custom admin
    path('', include('auctions.urls')),
]
