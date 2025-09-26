from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogoViewSet, BannerViewSet

router = DefaultRouter()
router.register(r'logos', LogoViewSet)
router.register(r'banners', BannerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
