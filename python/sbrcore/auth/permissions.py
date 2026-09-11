# ============================================================================
# Permission & Role Management System
# Fine-grained access control
# ============================================================================

from enum import Enum
from typing import List, Set
from dataclasses import dataclass
from ..logging import get_logger

logger = get_logger(__name__)

class Permission(Enum):
    """System permissions"""
    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Product Management (E-commerce)
    CREATE_PRODUCT = "create_product"
    READ_PRODUCT = "read_product"
    UPDATE_PRODUCT = "update_product"
    DELETE_PRODUCT = "delete_product"
    
    # Order Management
    CREATE_ORDER = "create_order"
    READ_ORDER = "read_order"
    UPDATE_ORDER = "update_order"
    CANCEL_ORDER = "cancel_order"
    
    # AI Services
    USE_AI = "use_ai"
    MANAGE_AI = "manage_ai"
    
    # Admin
    ADMIN_ACCESS = "admin_access"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SYSTEM = "manage_system"

class Role(Enum):
    """System roles with associated permissions"""
    
    # Anonymous user (no permissions)
    ANONYMOUS = "anonymous"
    
    # Regular user
    USER = "user"
    
    # Vendor/Seller
    VENDOR = "vendor"
    
    # Moderator
    MODERATOR = "moderator"
    
    # Administrator
    ADMIN = "admin"
    
    # Super Administrator
    SUPERADMIN = "superadmin"

@dataclass
class RolePermissionMap:
    """Maps roles to their permissions"""
    
    ROLE_PERMISSIONS = {
        Role.ANONYMOUS: set(),
        
        Role.USER: {
            Permission.READ_PRODUCT,
            Permission.CREATE_ORDER,
            Permission.READ_ORDER,
            Permission.USE_AI,
            Permission.READ_USER,
            Permission.UPDATE_USER,
        },
        
        Role.VENDOR: {
            Permission.READ_PRODUCT,
            Permission.CREATE_PRODUCT,
            Permission.UPDATE_PRODUCT,
            Permission.DELETE_PRODUCT,
            Permission.CREATE_ORDER,
            Permission.READ_ORDER,
            Permission.UPDATE_ORDER,
            Permission.USE_AI,
            Permission.READ_USER,
            Permission.UPDATE_USER,
        },
        
        Role.MODERATOR: {
            Permission.READ_PRODUCT,
            Permission.CREATE_PRODUCT,
            Permission.UPDATE_PRODUCT,
            Permission.DELETE_PRODUCT,
            Permission.CREATE_ORDER,
            Permission.READ_ORDER,
            Permission.UPDATE_ORDER,
            Permission.CANCEL_ORDER,
            Permission.USE_AI,
            Permission.READ_USER,
            Permission.UPDATE_USER,
            Permission.VIEW_ANALYTICS,
        },
        
        Role.ADMIN: {
            Permission.CREATE_USER,
            Permission.READ_USER,
            Permission.UPDATE_USER,
            Permission.DELETE_USER,
            Permission.CREATE_PRODUCT,
            Permission.READ_PRODUCT,
            Permission.UPDATE_PRODUCT,
            Permission.DELETE_PRODUCT,
            Permission.CREATE_ORDER,
            Permission.READ_ORDER,
            Permission.UPDATE_ORDER,
            Permission.CANCEL_ORDER,
            Permission.USE_AI,
            Permission.MANAGE_AI,
            Permission.ADMIN_ACCESS,
            Permission.VIEW_ANALYTICS,
        },
        
        Role.SUPERADMIN: {
            Permission.CREATE_USER,
            Permission.READ_USER,
            Permission.UPDATE_USER,
            Permission.DELETE_USER,
            Permission.CREATE_PRODUCT,
            Permission.READ_PRODUCT,
            Permission.UPDATE_PRODUCT,
            Permission.DELETE_PRODUCT,
            Permission.CREATE_ORDER,
            Permission.READ_ORDER,
            Permission.UPDATE_ORDER,
            Permission.CANCEL_ORDER,
            Permission.USE_AI,
            Permission.MANAGE_AI,
            Permission.ADMIN_ACCESS,
            Permission.VIEW_ANALYTICS,
            Permission.MANAGE_SYSTEM,
        }
    }

class PermissionManager:
    """
    Manages user permissions based on roles
    """
    
    @staticmethod
    def get_permissions(roles: List[str]) -> Set[str]:
        """
        Get all permissions for a list of roles
        
        Args:
            roles: List of role names
        
        Returns:
            Set of permission strings
        """
        permissions = set()
        
        for role_name in roles:
            try:
                role = Role[role_name.upper()]
                role_perms = RolePermissionMap.ROLE_PERMISSIONS.get(role, set())
                permissions.update(perm.value for perm in role_perms)
            except KeyError:
                logger.warning(f"Unknown role: {role_name}")
        
        return permissions
    
    @staticmethod
    def has_permission(roles: List[str], permission: str) -> bool:
        """
        Check if user with given roles has specific permission
        
        Args:
            roles: List of role names
            permission: Permission string to check
        
        Returns:
            True if user has permission
        """
        permissions = PermissionManager.get_permissions(roles)
        return permission in permissions
    
    @staticmethod
    def has_any_permission(roles: List[str], permissions: List[str]) -> bool:
        """
        Check if user has any of the given permissions
        
        Args:
            roles: List of role names
            permissions: List of permission strings
        
        Returns:
            True if user has any permission
        """
        user_permissions = PermissionManager.get_permissions(roles)
        return any(perm in user_permissions for perm in permissions)
    
    @staticmethod
    def has_all_permissions(roles: List[str], permissions: List[str]) -> bool:
        """
        Check if user has all given permissions
        
        Args:
            roles: List of role names
            permissions: List of permission strings
        
        Returns:
            True if user has all permissions
        """
        user_permissions = PermissionManager.get_permissions(roles)
        return all(perm in user_permissions for perm in permissions)
