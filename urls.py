from django.urls import include, path
from rest_framework import routers

from ecomm_dashboard.visualizer import views as visualizer_view
from ecomm_dashboard.data_loader import views as data_loader_view

router = routers.DefaultRouter()
# router.register(r"users", views.UserViewSet)
# router.register(r"groups", views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "visualizer/monthly_sales_volume",
        visualizer_view.line_chart_monthly_sales_volume,
    ),
    path("visualizer/monthly_revenue", visualizer_view.bar_chart_monthly_revenue),
    path("visualizer/orders_summary", visualizer_view.orders_summary),
    path("data_loader/extract_order_data", data_loader_view.extract_order_data),
]
