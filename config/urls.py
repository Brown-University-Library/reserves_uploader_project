from django.contrib import admin
from django.urls import path
from reserves_uploader_app import views


urlpatterns = [
    ## main ---------------------------------------------------------
    path( 'info/', views.info, name='info_url' ),
    path( 'uploader/', views.uploader, name='uploader_url' ),
    ## other --------------------------------------------------------
    path( '', views.root, name='root_url' ),
    # path( 'admin/', admin.site.urls ),
    path( 'error_check/', views.error_check, name='error_check_url' ),
    path( 'version/', views.version, name='version_url' ),
    # path( 'version2/', views.version2, name='version2_url' ),

]

