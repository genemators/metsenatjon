from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from club import views
from club.drf_yasg import schema_view

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('dashboard/', views.StatView.as_view())
]
router = DefaultRouter()
router.register(r'student', views.StudentViewSet, basename='student')
router.register(r'sponsor', views.SponsorViewSet, basename='sponsor')
router.register(r'donate', views.DonateViewSet, basename='donate')

urlpatterns += router.urls
urlpatterns += re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
