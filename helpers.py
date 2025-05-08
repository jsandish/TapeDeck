from flask import abort
from models import User

def get_user_by_email(email):
    """Find a user by email"""
    return User.query.filter_by(email=email).first()

def check_playlist_permission(playlist, user_id, required_permission_level=1):
    """
    Check if a user has the required permission level for a playlist
    Permission levels:
    1 - Read only
    2 - Edit
    3 - Admin
    
    Returns True if user has sufficient permissions, False otherwise
    """
    for user_entry in playlist.users:
        if user_entry.user_id == user_id:
            # Get the permission from the relationship
            for user_permission in playlist.users.filter_by(user_id=user_id).all():
                permission = user_permission.permissions
                if permission >= required_permission_level:
                    return True
    return False