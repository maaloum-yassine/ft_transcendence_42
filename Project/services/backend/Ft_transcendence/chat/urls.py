# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    # path("", views.index, name="index"),
	# path("<str:room_name>/", views.room, name="room"),
	path("", views.chathome, name="chathome"),
	path('is_friend_blocked/<int:friend_id>/', views.is_friend_blocked_view, name='is_friend_blocked'),
	path('fetch_non_friends/', views.list_non_friends, name='fetch-non-friends'),
	path("block_friend/<int:friend_id>/", views.block_friend, name="block_friend"),
	path('check_block_status/', views.check_block_status, name='check_block_status'),
	path('blocked-users/', views.get_blocked_users, name='blocked-users'),
	path('unblock_user/', views.unblock_friend, name='blocked-users')
	# path("users/", views.UserListView.as_view(), name="user-list"),
]

# export $(cat .env | xargs)
# path('send_friend_request/', views.send_friend_request, name='add_friend'),
# path('accept_friend_request/', views.accept_friend_request, name='accept_friend_request'),
# path('list_friends/', views.list_friends, name='list_friends'),
# path('list_requst_friend/', views.list_requst_friend, name='list_requst_friend'),
# path('remove_friend/', views.remove_friend, name='remove_friend'),



# end point login 
# http://localhost:8000/oauth/login/ -->google
# http://localhost:8000/authorize/ -> 42
# http://localhost:8000/login/