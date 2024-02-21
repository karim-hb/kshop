from . import views
from rest_framework_nested import routers
from django.urls import path

router = routers.DefaultRouter()
router.register('foods', views.FoodViewSet, basename="foods")
router.register('collection', views.CollectionViewSet)
router.register('orders', views.OrderView, basename="orders")
# router.register('user', views.UserViewSet, basename="users")

# router.register('images', views.FoodImageViewSet, basename="food_images")
foods_router = routers.NestedDefaultRouter(router, 'foods', lookup='food')
collection_router = routers.NestedDefaultRouter(router, 'collection', lookup='collection')
collection_router.register('image', views.CollectionImageViewSet, basename='collection-image')

foods_router.register('reviews', views.ReviewViewSet, basename='food-reviews')
foods_router.register('image', views.FoodImageViewSet, basename='food-image')
urlpatterns = router.urls + foods_router.urls + collection_router.urls
