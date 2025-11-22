# chatbot/urls.py
from django.urls import path
from .views import SimpleChatbotView,ChatbotWidgetDemoView,PopularItemsView

urlpatterns = [
    path("simple/", SimpleChatbotView.as_view(), name="chatbot-simple"),
    path("widget-demo/", ChatbotWidgetDemoView.as_view(), name="chatbot-demo-ui"),
    path("popular-items/", PopularItemsView.as_view(), name="chatbot_popular_items"),
]
