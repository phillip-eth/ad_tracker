from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('log_user', views.log_user, name='log_user'),
    path('reg_user', views.reg_user, name='reg_user'),
    path('logout', views.log_out, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('complete_order/<int:pk>', views.complete_order, name='complete'),
    path('completed', views.completed, name='completed'),
    path('cancelled', views.cancelled, name='cancelled'),
    path('past_due', views.past_due, name='past_due'),
    path('order_info_requested', views.order_info_requested, name='order_info_requested'),
    path('orders_hold', views.orders_hold, name='orders_hold'),
    path('orders_assigned', views.orders_assigned, name='orders_assigned'),
    path('search_order', views.search_order, name='search_order'),
    path('sales', views.sales, name='sales'),
    path('payroll', views.payroll, name='payroll'),
    path('manage_users', views.manage_users, name='manage_users'),
    path('manage_appraisers', views.manage_appraisers, name='manage_appraisers'),
    path('new_appraiser', views.new_appraiser, name='new_appraiser'),
    path('edit_appraiser/<int:pk>', views.edit_appraiser, name='edit_appraiser'),
    path('process_edit_appraiser/<int:pk>', views.process_edit_appraiser, name='process_edit_appraiser'),
    path('delete_appraiser/<int:pk>', views.delete_appraiser, name='delete_appraiser'),
    path('edit_user/<int:pk>', views.edit_user, name='edit_user'),
    path('process_user_edit/<int:pk>', views.process_user_edit, name='process_user_edit'),
    path('change_pw/<int:pk>', views.change_pw, name='change_pw'),
    path('delete_user/<int:pk>', views.delete_user, name='delete_user'),
    path('manage_masters', views.manage_masters, name='manage_masters'),
    path('new_client', views.new_client, name='new_client'),
    path('delete_client/<int:pk>', views.delete_client, name='delete_client'),
    path('new_product', views.new_product, name='new_product'),
    path('delete_product/<int:pk>', views.delete_product, name='delete_product'),
    path('add_order', views.add_order, name='add_order'),
    path('order_edit/<int:pk>', views.order_edit, name='order-edit'),
    path('order_edit_process/<int:pk>', views.order_edit_process, name='order_edit_process'),
    path('update_status/<int:pk>', views.update_status, name='update_status'),
    path('delete/<int:pk>', views.delete, name='delete'),
    path('run_sales_report', views.run_sales_report, name='run_sales_report'),
    path('sales_snapshot', views.sales_snapshot, name='sales_snapshot'),
    path('recap_today', views.recap_today, name='recap_today'),
    path('run_payroll_report', views.run_payroll_report, name='run_payroll_report'),
    path('sales_by_appraiser/<int:pk>/<int:mnth>/<int:yr>', views.sales_by_appraiser, name='sales_by_appraiser'),
    path('sales_by_client/<str:name>/<int:mnth>/<int:yr>', views.sales_by_client, name='sales_by_client'),
   

]

