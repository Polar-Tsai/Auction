from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = i18n_patterns(
    # path('admin/', admin.site.urls), # Disabled custom admin
    path('', include('auctions.urls')),
    prefix_default_language=True,  # Include language prefix even for default language
)

# Media files should be served without language prefix
# In production, use a web server (nginx/apache) to serve these files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
