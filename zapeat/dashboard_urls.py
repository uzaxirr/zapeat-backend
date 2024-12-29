from django.urls import path, include

from orders.views import DashboardOrdersView

urlpatterns = [
    path('orders/', DashboardOrdersView.as_view(), name='admin-orders'),
]
