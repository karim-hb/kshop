from . import views
from core.views import ReviewViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('foods', views.FoodViewSet, basename="foods")
router.register('collection', views.CollectionViewSet)
router.register('cart', views.CartViewSet)
router.register('order', views.OrderViewSet, basename="order")
router.register('userInfo', views.CustomerView, basename="customer")
router.register('address', views.AddressView, basename="address")


foods_router = routers.NestedDefaultRouter(router, 'foods', lookup='food')
foods_router.register('reviews', ReviewViewSet, basename='food-reviews')

cart_router = routers.NestedDefaultRouter(router, 'cart', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + foods_router.urls + cart_router.urls
