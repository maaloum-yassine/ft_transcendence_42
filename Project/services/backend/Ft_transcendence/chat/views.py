from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth.models import User
# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from user_managemanet.models import Friendship,CustomUser
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.conf import settings

@api_view(['GET'])
def chathome(request):

    # print(f"USER ------------>  {request.user}")
    return Response("Welcome To chat 1337  page")



@api_view(['GET'])
def get_blocked_users(request):
    """
    Fetch all users blocked by the authenticated user or where the friend has blocked them.
    """
    # Get the authenticated user
    authenticated_user = request.user

    if authenticated_user.is_anonymous:
        return Response({"error": "Authentication required."}, status=401)

    # Query Friendship to find blocked relationships
    blocked_users = Friendship.objects.filter(
        blocked=True,
        blocked_by=authenticated_user  # Ensure we only check blocks initiated by the authenticated user
    ).select_related('user', 'friend')

    # Format the data to include user details, ensuring the friend is returned
    blocked_users_data = []
    for friendship in blocked_users:
        # Determine who the friend is
        if friendship.user == authenticated_user:
            friend = friendship.friend
        elif friendship.friend == authenticated_user:
            friend = friendship.user
        else:
            continue  # Skip invalid data

        avatar_url = (
            request.build_absolute_uri(settings.MEDIA_URL + friend.avatar).replace('http://', 'https://')
            if friend.avatar
            else request.build_absolute_uri(settings.MEDIA_URL + 'avatars/default_avatar.png').replace('http://', 'https://')
        )

        # Append friend details
        blocked_users_data.append({
            'id': friend.id,
            'username': friend.username,
            'avatar': avatar_url,
        })

    return Response({'blocked_users': blocked_users_data}, status=200)








@api_view(['GET'])
def check_block_status(request):
    # Get the target user ID from the request parameters
    user_id = request.GET.get('id')

    # Validate user ID is provided
    if not user_id:
        return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Get the authenticated user
    current_user = request.user
    if current_user.is_anonymous:
        return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    # Validate the target user exists
    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "Target user not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if either user has blocked the other
    is_blocked = Friendship.objects.filter(
        Q(user=current_user, friend=target_user, blocked=True) |
        Q(user=target_user, friend=current_user, blocked=True)
    ).exists()

    # Return the block status
    return Response({
        "is_blocked": is_blocked
    }, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def unblock_friend(request):
    """
    View to unblock a specific friend.
    """
    # Retrieve `friend_id` from the query parameters
    friend_id = request.query_params.get('friend_id')

    if not friend_id:
        return Response({"detail": "Friend ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Get the authenticated user
    user = request.user

    # Ensure the friend exists
    friend = get_object_or_404(CustomUser, id=friend_id)

    # Find the friendship record where the current user is involved with the friend
    friendship = Friendship.objects.filter(
        user=user, friend=friend
    ).first() or Friendship.objects.filter(
        user=friend, friend=user
    ).first()

    if not friendship:
        return Response({"detail": "Friendship not found"}, status=status.HTTP_404_NOT_FOUND)

    # If friendship exists, update the blocked status to False (unblock)
    friendship.blocked = False
    friendship.save()

    return Response({"detail": "Friend successfully unblocked."}, status=status.HTTP_200_OK)




















@api_view(['PATCH'])
def block_friend(request, friend_id):
    """
    View to block a specific friend.
    The user must be the one initiating the block request.
    """
    # Get the authenticated user
    user = request.user

    # Ensure the friend exists
    friend = get_object_or_404(CustomUser, id=friend_id)

    # Find the friendship record where the current user is involved with the friend
    friendship = Friendship.objects.filter(
        user=user, friend=friend
    ).first() or Friendship.objects.filter(
        user=friend, friend=user
    ).first()

    if not friendship:
        return Response({"detail": "Friendship not found"}, status=status.HTTP_404_NOT_FOUND)

    # If friendship exists, update the blocked status and the blocked_by field
    friendship.blocked = True
    friendship.blocked_by = user  # Save the authenticated user as the blocker
    friendship.save()

    return Response({"detail": "Friend successfully blocked."}, status=status.HTTP_200_OK)


def get_non_friends(authenticated_user):
    friends = Friendship.objects.filter(
        Q(user=authenticated_user) | Q(friend=authenticated_user),
        accepted=True
    ).values_list('user', 'friend')

    friend_ids = set(
        user_id for friend_pair in friends for user_id in friend_pair if user_id != authenticated_user.id
    )

    non_friends = CustomUser.objects.exclude(
        Q(pk=authenticated_user.pk) | Q(pk__in=friend_ids)
    )

    return non_friends



















def is_friend_blocked_view(request, friend_id):
    """
    Checks if the authenticated user is blocked by or has blocked a specific friend.

    Args:
        request: The HTTP request object.
        friend_id (int): The ID of the friend to check.

    Returns:
        JsonResponse: Indicates if the friend is blocked or has blocked the user.
    """
    authenticated_user = request.user  # The logged-in user

    try:
        # Fetch the friend user by ID or return 404 if not found
        friend_user = get_object_or_404(CustomUser, id=friend_id)

        # Check if the authenticated user has blocked the friend
        friendship_from_user = Friendship.objects.filter(user=authenticated_user, friend=friend_user).first()

        # Check if the friend has blocked the authenticated user
        friendship_from_friend = Friendship.objects.filter(user=friend_user, friend=authenticated_user).first()

        # Determine blocking statuses
        user_blocked_friend = friendship_from_user.blocked if friendship_from_user else False
        friend_blocked_user = friendship_from_friend.blocked if friendship_from_friend else False

        # Consolidated blocked status
        blocked = user_blocked_friend or friend_blocked_user

        return JsonResponse({
            'authenticated_user_id': authenticated_user.id,
            'friend_id': friend_id,
            'blocked': blocked,  # Consolidated status
        })

    except CustomUser.DoesNotExist:
        return JsonResponse({
            'error': 'Friend user not found.'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }, status=500)


















def get_non_friends(authenticated_user):
    # Get all accepted friendships involving the authenticated user
    friends = Friendship.objects.filter(
        Q(user=authenticated_user) | Q(friend=authenticated_user),
        accepted=True
    ).values_list('user', 'friend')

    # Extract the IDs of friends
    friend_ids = set(
        user_id for friend_pair in friends for user_id in friend_pair if user_id != authenticated_user.id
    )

    # Exclude the authenticated user and their friends from the list of all users
    non_friends = CustomUser.objects.exclude(
        Q(pk=authenticated_user.pk) | Q(pk__in=friend_ids)
    )

    return non_friends


@api_view(['GET'])
def list_non_friends(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=404)

    authenticated_user = request.user
    non_friends = get_non_friends(authenticated_user)

    # Serialize the data with details about invitations
    data = []
    for user in non_friends:
        # Check if there is a pending invitation in either direction
        has_invitation = Friendship.objects.filter(
            Q(user=authenticated_user, friend=user, accepted=False) |
            Q(user=user, friend=authenticated_user, accepted=False)
        ).exists()

        # Directly use avatar if it's already a URL or path
        avatar = user.avatar if user.avatar else None

        data.append({
            "id": user.id,
            "username": user.username,
            "avatar": avatar,
            "invitation_sent": has_invitation  # True if an invitation exists in either direction
        })

    return Response({"non_friends": data}, status=200)
# def index(request):
#     return render(request, "index.html")

# def room(request, room    _name):
#     return render(request, "room.html", {"room_name": room_name})


# class UserListView(APIView):
#     def get(self, request, *args, **kwargs):
#         # Fetch all users from the database
#         users = User.objects.all()

#         # Define the serializer inline
#         class UserSerializer(serializers.ModelSerializer):
#             class Meta:
#                 model = User
#                 fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']

#         # Serialize the user data
#         serializer = UserSerializer(users, many=True)

#         # Get the ID and username of the authenticated user
#         authenticated_user_id = request.user.id if request.user.is_authenticated else None
#         authenticated_user_name = request.user.username if request.user.is_authenticated else None

#         # Return the serialized data along with the authenticated user's ID and name
#         response_data = {
#             'authenticated_user_id': authenticated_user_id,
#             'authenticated_user_name': authenticated_user_name,
#             'users': serializer.data
#         }

#         return Response(response_data, status=status.HTTP_200_OK)
