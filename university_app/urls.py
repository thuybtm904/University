from django.urls import path
from . import views

app_name = 'university_app'

urlpatterns = [
    # Trang chủ
    path('', views.trang_chu, name='trang_chu'),
    
    # Trang tìm kiếm
    path('tim-kiem/', views.tim_kiem, name='tim_kiem'),
    path('tim-kiem/ket-qua/', views.ket_qua_tim_kiem, name='ket_qua_tim_kiem'),
    
    # Trang so sánh
    path('so-sanh/', views.so_sanh, name='so_sanh'),
    path('so-sanh/xoa/', views.clear_comparison, name='clear_comparison'),
    path('so-sanh/toggle/<str:university_name>/', views.toggle_comparison, name='toggle_comparison'),
    path('so-sanh/luu/', views.luu_ket_qua_so_sanh, name='luu_ket_qua_so_sanh'),
    
    # Trang chi tiết trường (sử dụng tên trường)
    path('truong/<str:ten_truong>/', views.chi_tiet_truong, name='chi_tiet_truong'),
    
    # API endpoints
    path('api/danh-sach-truong/', views.danh_sach_truong_api, name='danh_sach_truong_api'),

]