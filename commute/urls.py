from django.urls import path
from .views import CommuteInsightsAPIView, RelocationCostAPIView

urlpatterns = [
    path("commute/", CommuteInsightsAPIView.as_view(), name="commute-insights"),
    path("relocation/", RelocationCostAPIView.as_view(), name="relocation-cost"),
]
