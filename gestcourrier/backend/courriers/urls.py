from rest_framework.routers import DefaultRouter

from courriers.views import CourrierViewSet

router = DefaultRouter()
router.register("courriers", CourrierViewSet, basename="courrier")

urlpatterns = router.urls
