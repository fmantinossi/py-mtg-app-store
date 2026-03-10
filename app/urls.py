"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store.views import CardsView, NewCardView, DetailCardView, UpdateCardView, DeleteCardView
from accounts.views import register_view, login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cards/', CardsView.as_view(), name='cards'),
    path('cards/<int:pk>/', DetailCardView.as_view(), name='card_detail'),
    path('cards/<int:pk>/update/', UpdateCardView.as_view(), name='card_update'),
    path('cards/<int:pk>/delete/', DeleteCardView.as_view(), name='card_delete'),
    path('new_card/', NewCardView.as_view(), name='new_card'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
