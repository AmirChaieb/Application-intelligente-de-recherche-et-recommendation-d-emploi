from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.loginregister, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('home/',views.home, name="offers"),
    path('profil/',views.profil, name="profil"),
    path('profil2/',views.profil2, name="profil2"),
    path('jobs/',views.jobs, name="jobs"),
    path('offre/<int:offre_id>/', views.offre_detail, name='offre_detail'),
    path('cv/<slug:pdfSlug>/', views.pdf_view, name='view_cv'),
    path("cv/<slug:pdfSlug>/", views.pdf_view, name="pdf_view"),




    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
