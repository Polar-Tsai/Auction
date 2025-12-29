from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.views.static import serve
from django.views.i18n import set_language

# Media files served without language prefix
urlpatterns = [
    re_path(r'^data_photo/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
    path('i18n/setlang/', set_language, name='set_language'),
]

# Language-specific URLs
urlpatterns += i18n_patterns(
    # path('admin/', admin.site.urls), # Disabled custom admin
    path('', include('auctions.urls')),
    prefix_default_language=True,  # Include language prefix even for default language
)
