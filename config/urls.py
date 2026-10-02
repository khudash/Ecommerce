from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Django default admin hataya — custom dashboard use karo
    path('admin/', RedirectView.as_view(url='/admin-panel/', permanent=False)),
    path('', include('store.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )