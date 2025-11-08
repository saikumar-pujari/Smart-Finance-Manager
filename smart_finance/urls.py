from django.contrib import admin
from django.urls import path, include
admin.site.site_header="Smart Finance Manager"
admin.site.index_title="transcation tracker"
admin.site.site_header='All Transcations'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('finance/', include('home.urls'))
]
