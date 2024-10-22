from django.urls import path

from equipment import views


urlpatterns = [
    path('', views.equipment_dashboard_view, name='equipment_dashboard'),
    path('item-query/', views.item_query_view, name='equipment_item_query'),
    path('item-detail/<str:pk>/', views.item_detail_view, name='equipment_item_detail'),
    path('create-item/', views.create_item_view, name='equipment_create_item'),
    path('update-item/<str:pk>/', views.update_item_view, name='equipment_update_item'),
    path('update-item-service/<str:pk>/', views.update_item_service_view, name='equipment_update_service'),
    path('delete-item/<str:pk>/', views.delete_item_view, name='equipment_delete_item'),
    
    path('assign-item/<str:pk>/', views.assign_item_view, name='equipment_assign_item'),
    path('unassign-item/<str:pk>/', views.unassign_item_view, name='equipment_unassign_item'),
    
    path('booking-summary/', views.booking_summary_view, name='equipment_booking_summary'),
    path('booking-summary-cancel/', views.booking_summary_cancel_view, name='equipment_booking_summary_cancel'),
    path('booking-summary-confirm/', views.booking_summary_confirm_view, name='equipment_booking_summary_confirm'),
    path('booking-update/<str:pk>/', views.booking_update_view, name='equipment_booking_update'),
    path('booking-update-meta/<str:pk>/', views.booking_update_meta_view, name='equipment_booking_update_meta'),
    path('booking-cancel/<str:pk>/', views.booking_cancel_view, name='equipment_booking_cancel'),
    path('booking-add/<str:pk>/', views.add_to_booking_view, name='equipment_booking_add_item'),
    path('booking-remove/<str:pk>/', views.remove_from_booking_view, name='equipment_booking_remove_item'),
    path('booking-query/', views.booking_query_view, name='equipment_booking_query'),
    path('booking-calendar/', views.booking_calendar_view, name='equipment_booking_calendar'),
    path('booking-detail/<str:pk>/', views.booking_detail_view, name='equipment_booking_detail'),
    path('booking-cost/<str:pk>/', views.booking_cost_view, name='equipment_booking_cost'),
    path('booking-invoice/<str:pk>/', views.booking_invoice_view, name='equipment_booking_invoice'),
]