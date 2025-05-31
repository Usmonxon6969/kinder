from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from reports.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('users/', include('users.urls')),
    path('ingredients/', include('ingredients.urls')),
    path('meals/', include('meals.urls')),
    path('reports/', include('reports.urls')),
    path('common/', include('common.urls')),  # Add common URLs

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)