"""
Authentication service.

Handles JWT token generation, validation, login, logout, and refresh.

Reference:
- cool-admin-midway/src/modules/base/service/sys/login.ts
- Wiki: 后端服务/Python后端服务/后端架构补充/服务层架构/用户服务模块.md
"""

import hashlib
import logging
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BusinessException, UnauthorizedException
from app.core.redis import CacheManager, redis_client
from app.models.sys import (
    BaseSysDepartment,
    BaseSysMenu,
    BaseSysRole,
    BaseSysUser,
    BaseSysUserRole,
)
from app.schemas.auth import (
    CaptchaResponse,
    LoginResponse,
    PermsResponse,
    TokenPayload,
    UserInfoResponse,
)

logger = logging.getLogger("work_assistant.auth")


def md5_hash(password: str) -> str:
    """Hash password using MD5 (for compatibility with existing system)."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against MD5 hash."""
    return md5_hash(plain_password) == hashed_password


class AuthService:
    """Authentication service for login, token management, and permissions."""

    # Cache key prefixes
    CACHE_PREFIX_TOKEN = "admin:token"
    CACHE_PREFIX_REFRESH_TOKEN = "admin:token:refresh"
    CACHE_PREFIX_PERMS = "admin:perms"
    CACHE_PREFIX_DEPARTMENT = "admin:department"
    CACHE_PREFIX_DEPARTMENT_ID = "admin:departmentId"
    CACHE_PREFIX_PASSWORD_VERSION = "admin:passwordVersion"
    CACHE_PREFIX_CAPTCHA = "verify:img"

    # Token expiration (in seconds)
    ACCESS_TOKEN_EXPIRE = settings.jwt.access_token_expire_minutes * 60
    REFRESH_TOKEN_EXPIRE = settings.jwt.refresh_token_expire_days * 24 * 60 * 60

    async def generate_captcha(self, captcha_type: str = "base64") -> CaptchaResponse:
        """
        Generate captcha image.

        Args:
            captcha_type: Type of captcha (base64, svg)

        Returns:
            CaptchaResponse with captcha ID and image data
        """
        # Generate random 4-digit code (numbers only for simplicity)
        code = "".join(random.choices(string.digits, k=4))
        captcha_id = str(uuid.uuid4())

        # Store captcha in Redis (30 minutes TTL)
        await CacheManager.set(
            self.CACHE_PREFIX_CAPTCHA,
            captcha_id,
            code.lower(),
            ttl=1800,
        )

        # Generate simple text-based captcha (in production, use svg-captcha or similar)
        # For now, return the code directly (should be replaced with actual image generation)
        data = f"data:text/plain;base64,{code}"  # Placeholder - implement actual captcha

        logger.debug(f"Generated captcha: {captcha_id}")
        return CaptchaResponse(captchaId=captcha_id, data=data)

    async def verify_captcha(self, captcha_id: str, code: str) -> bool:
        """
        Verify captcha code.

        Args:
            captcha_id: Captcha ID
            code: User input code

        Returns:
            True if valid, False otherwise
        """
        stored_code = await CacheManager.get(self.CACHE_PREFIX_CAPTCHA, captcha_id)
        if not stored_code or not code:
            return False

        if code.lower() != stored_code:
            return False

        # Delete captcha after successful verification
        await CacheManager.delete(self.CACHE_PREFIX_CAPTCHA, captcha_id)
        return True

    async def login(
        self,
        username: str,
        password: str,
        captcha_id: str,
        verify_code: str,
        db: AsyncSession,
    ) -> LoginResponse:
        """
        User login.

        Args:
            username: Username
            password: Plain text password
            captcha_id: Captcha ID
            verify_code: Captcha verification code
            db: Database session

        Returns:
            LoginResponse with tokens

        Raises:
            BusinessException: If login fails
        """
        # Verify captcha
        if not await self.verify_captcha(captcha_id, verify_code):
            raise BusinessException(message="验证码不正确")

        # Get user by username
        stmt = select(BaseSysUser).where(BaseSysUser.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise BusinessException(message="账户或密码不正确")

        # Check user status and password
        if user.status == 0 or not verify_password(password, user.password):
            raise BusinessException(message="账户或密码不正确")

        # Get user roles
        role_ids = await self._get_user_role_ids(user.id, db)
        if not role_ids:
            raise BusinessException(message="该用户未设置任何角色，无法登录")

        # Get child department IDs
        child_dept_ids = await self._get_child_department_ids(user.departmentId, db)

        # Get dynamic permissions (for admin, grant all)
        dynamic_info = ["all"] if user.username == "admin" else await self._get_dynamic_info(role_ids, db)

        # Generate tokens
        access_token = await self._generate_token(
            user=user,
            role_ids=role_ids,
            child_dept_ids=child_dept_ids,
            dynamic_info=dynamic_info,
            expire_seconds=self.ACCESS_TOKEN_EXPIRE,
            is_refresh=False,
        )
        refresh_token = await self._generate_token(
            user=user,
            role_ids=role_ids,
            child_dept_ids=child_dept_ids,
            dynamic_info=dynamic_info,
            expire_seconds=self.REFRESH_TOKEN_EXPIRE,
            is_refresh=True,
        )

        # Cache user info
        perms = await self._get_user_perms(role_ids, db)
        departments = await self._get_role_departments(role_ids, user.username == "admin", db)

        await CacheManager.set(f"{self.CACHE_PREFIX_DEPARTMENT}", str(user.id), departments)
        await CacheManager.set(f"{self.CACHE_PREFIX_DEPARTMENT_ID}", str(user.id), user.departmentId)
        await CacheManager.set(f"{self.CACHE_PREFIX_PERMS}", str(user.id), perms)
        await CacheManager.set(f"{self.CACHE_PREFIX_TOKEN}", str(user.id), access_token)
        await CacheManager.set(f"{self.CACHE_PREFIX_REFRESH_TOKEN}", str(user.id), refresh_token)
        await CacheManager.set(f"{self.CACHE_PREFIX_PASSWORD_VERSION}", str(user.id), user.passwordV)

        logger.info(f"User logged in: {username}")

        return LoginResponse(
            token=access_token,
            expire=self.ACCESS_TOKEN_EXPIRE,
            refreshToken=refresh_token,
            refreshExpire=self.REFRESH_TOKEN_EXPIRE,
        )

    async def logout(self, user_id: int) -> None:
        """
        User logout - clear all cached tokens and permissions.

        Args:
            user_id: User ID
        """
        await CacheManager.delete(self.CACHE_PREFIX_DEPARTMENT, str(user_id))
        await CacheManager.delete(self.CACHE_PREFIX_DEPARTMENT_ID, str(user_id))
        await CacheManager.delete(self.CACHE_PREFIX_PERMS, str(user_id))
        await CacheManager.delete(self.CACHE_PREFIX_TOKEN, str(user_id))
        await CacheManager.delete(self.CACHE_PREFIX_REFRESH_TOKEN, str(user_id))
        await CacheManager.delete(self.CACHE_PREFIX_PASSWORD_VERSION, str(user_id))

        logger.info(f"User logged out: {user_id}")

    async def refresh_token(self, refresh_token: str) -> LoginResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            LoginResponse with new tokens

        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
            )
        except JWTError:
            raise UnauthorizedException(message="登录失效")

        # Verify it's a refresh token
        if not payload.get("isRefresh"):
            raise UnauthorizedException(message="登录失效")

        user_id = payload.get("userId")
        if not user_id:
            raise UnauthorizedException(message="登录失效")

        # Verify password version
        cached_pw_version = await CacheManager.get(self.CACHE_PREFIX_PASSWORD_VERSION, str(user_id))
        if cached_pw_version and cached_pw_version != payload.get("passwordVersion"):
            raise UnauthorizedException(message="登录失效")

        # Generate new tokens (reuse existing payload data)
        new_payload = {
            "userId": payload.get("userId"),
            "username": payload.get("username"),
            "roleIds": payload.get("roleIds", []),
            "departmentId": payload.get("departmentId"),
            "childDepartmentIds": payload.get("childDepartmentIds", []),
            "passwordVersion": payload.get("passwordVersion"),
            "nickName": payload.get("nickName"),
            "dynamicInfo": payload.get("dynamicInfo", []),
        }

        # Generate access token
        access_token = self._create_jwt_token(
            data={**new_payload, "isRefresh": False},
            expire_seconds=self.ACCESS_TOKEN_EXPIRE,
        )

        # Generate new refresh token
        new_refresh_token = self._create_jwt_token(
            data={**new_payload, "isRefresh": True},
            expire_seconds=self.REFRESH_TOKEN_EXPIRE,
        )

        # Update cached tokens
        await CacheManager.set(self.CACHE_PREFIX_TOKEN, str(user_id), access_token)
        await CacheManager.set(self.CACHE_PREFIX_REFRESH_TOKEN, str(user_id), new_refresh_token)

        return LoginResponse(
            token=access_token,
            expire=self.ACCESS_TOKEN_EXPIRE,
            refreshToken=new_refresh_token,
            refreshExpire=self.REFRESH_TOKEN_EXPIRE,
        )

    async def verify_token(self, token: str) -> TokenPayload:
        """
        Verify JWT token and return payload.

        Args:
            token: JWT token

        Returns:
            TokenPayload

        Raises:
            UnauthorizedException: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
            )
        except JWTError:
            raise UnauthorizedException(message="登录失效")

        # Check if it's a refresh token (not allowed for API access)
        if payload.get("isRefresh"):
            raise UnauthorizedException(message="登录失效")

        user_id = payload.get("userId")
        if not user_id:
            raise UnauthorizedException(message="登录失效")

        # Verify password version
        cached_pw_version = await CacheManager.get(self.CACHE_PREFIX_PASSWORD_VERSION, str(user_id))
        if cached_pw_version and cached_pw_version != payload.get("passwordVersion"):
            raise UnauthorizedException(message="登录失效")

        return TokenPayload(
            userId=payload.get("userId"),
            username=payload.get("username", ""),
            roleIds=payload.get("roleIds", []),
            departmentId=payload.get("departmentId"),
            childDepartmentIds=payload.get("childDepartmentIds", []),
            passwordVersion=payload.get("passwordVersion", 1),
            nickName=payload.get("nickName"),
            isRefresh=payload.get("isRefresh", False),
            dynamicInfo=payload.get("dynamicInfo", []),
        )

    async def get_user_info(self, user_id: int, db: AsyncSession) -> UserInfoResponse:
        """
        Get user information.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            UserInfoResponse
        """
        stmt = select(BaseSysUser).where(BaseSysUser.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise BusinessException(message="用户不存在")

        # Get department name
        dept_name = None
        if user.department:
            dept_name = user.department.name

        # Get role IDs
        role_ids = await self._get_user_role_ids(user_id, db)

        return UserInfoResponse(
            id=user.id,
            username=user.username,
            name=user.name,
            nickName=user.nickName,
            headImg=user.headImg,
            email=user.email,
            phone=user.phone,
            departmentId=user.departmentId,
            departmentName=dept_name,
            roleIds=role_ids,
            status=user.status,
        )

    async def get_user_perms_and_menus(
        self, user_id: int, role_ids: list[int], is_admin: bool, db: AsyncSession
    ) -> PermsResponse:
        """
        Get user permissions and menu tree.

        Args:
            user_id: User ID
            role_ids: Role IDs
            is_admin: Whether user is admin
            db: Database session

        Returns:
            PermsResponse with menus and perms
        """
        # Get permissions
        perms = await self._get_user_perms(role_ids, db)

        # Get menus (admin gets all, others get based on role)
        if is_admin:
            stmt = select(BaseSysMenu).where(BaseSysMenu.type.in_([0, 1])).order_by(BaseSysMenu.orderNum)
        else:
            # Get menu IDs from roles
            menu_ids = set()
            stmt = select(BaseSysRole).where(BaseSysRole.id.in_(role_ids))
            result = await db.execute(stmt)
            roles = result.scalars().all()
            for role in roles:
                if role.menuIdList:
                    menu_ids.update(role.menuIdList)

            if not menu_ids:
                return PermsResponse(menus=[], perms=perms)

            stmt = (
                select(BaseSysMenu)
                .where(BaseSysMenu.id.in_(menu_ids), BaseSysMenu.type.in_([0, 1]))
                .order_by(BaseSysMenu.orderNum)
            )

        result = await db.execute(stmt)
        menus = result.scalars().all()

        # Build menu tree
        menu_tree = self._build_menu_tree(menus)

        return PermsResponse(menus=menu_tree, perms=perms)

    # ==================== Private Methods ====================

    async def _generate_token(
        self,
        user: BaseSysUser,
        role_ids: list[int],
        child_dept_ids: list[int],
        dynamic_info: list[str],
        expire_seconds: int,
        is_refresh: bool,
    ) -> str:
        """Generate JWT token."""
        data = {
            "userId": user.id,
            "username": user.username,
            "roleIds": role_ids,
            "departmentId": user.departmentId,
            "childDepartmentIds": child_dept_ids,
            "passwordVersion": user.passwordV,
            "nickName": user.nickName,
            "isRefresh": is_refresh,
            "dynamicInfo": dynamic_info,
        }
        return self._create_jwt_token(data, expire_seconds)

    def _create_jwt_token(self, data: dict[str, Any], expire_seconds: int) -> str:
        """Create JWT token with expiration."""
        expire = datetime.utcnow() + timedelta(seconds=expire_seconds)
        to_encode = data.copy()
        to_encode["exp"] = expire
        return jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)

    async def _get_user_role_ids(self, user_id: int, db: AsyncSession) -> list[int]:
        """Get role IDs for a user."""
        stmt = select(BaseSysUserRole.roleId).where(BaseSysUserRole.userId == user_id)
        result = await db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def _get_child_department_ids(
        self, department_id: int | None, db: AsyncSession
    ) -> list[int]:
        """Recursively get all child department IDs."""
        if not department_id:
            return []

        child_ids: list[int] = []
        stmt = select(BaseSysDepartment.id).where(BaseSysDepartment.parentId == department_id)
        result = await db.execute(stmt)
        direct_children = [row[0] for row in result.fetchall()]

        for child_id in direct_children:
            child_ids.append(child_id)
            # Recursively get children
            grandchildren = await self._get_child_department_ids(child_id, db)
            child_ids.extend(grandchildren)

        return child_ids

    async def _get_dynamic_info(self, role_ids: list[int], db: AsyncSession) -> list[str]:
        """Get dynamic column permissions from roles."""
        if not role_ids:
            return []

        # Get menu IDs from roles
        stmt = select(BaseSysRole.menuIdList).where(BaseSysRole.id.in_(role_ids))
        result = await db.execute(stmt)
        menu_ids = set()
        for row in result.fetchall():
            if row[0]:
                menu_ids.update(row[0])

        if not menu_ids:
            return []

        # Get menus with dynamic info permissions
        stmt = select(BaseSysMenu.perms).where(
            BaseSysMenu.id.in_(menu_ids),
            BaseSysMenu.perms.isnot(None),
        )
        result = await db.execute(stmt)
        dynamic_info = []
        for row in result.fetchall():
            perms = row[0]
            if perms and perms.startswith("rk:") and perms.endswith(":dynamicInfo"):
                dynamic_info.append(perms)

        return dynamic_info

    async def _get_user_perms(self, role_ids: list[int], db: AsyncSession) -> list[str]:
        """Get permission codes for roles."""
        if not role_ids:
            return []

        # Get menu IDs from roles
        stmt = select(BaseSysRole.menuIdList).where(BaseSysRole.id.in_(role_ids))
        result = await db.execute(stmt)
        menu_ids = set()
        for row in result.fetchall():
            if row[0]:
                menu_ids.update(row[0])

        if not menu_ids:
            return []

        # Get permission codes from menus
        stmt = select(BaseSysMenu.perms).where(
            BaseSysMenu.id.in_(menu_ids),
            BaseSysMenu.perms.isnot(None),
            BaseSysMenu.perms != "",
        )
        result = await db.execute(stmt)
        return [row[0] for row in result.fetchall() if row[0]]

    async def _get_role_departments(
        self, role_ids: list[int], is_admin: bool, db: AsyncSession
    ) -> list[int]:
        """Get department IDs accessible by roles."""
        if is_admin:
            # Admin gets all departments
            stmt = select(BaseSysDepartment.id)
            result = await db.execute(stmt)
            return [row[0] for row in result.fetchall()]

        if not role_ids:
            return []

        # Get department IDs from roles
        stmt = select(BaseSysRole.departmentIdList).where(BaseSysRole.id.in_(role_ids))
        result = await db.execute(stmt)
        dept_ids = set()
        for row in result.fetchall():
            if row[0]:
                dept_ids.update(row[0])

        return list(dept_ids)

    def _build_menu_tree(self, menus: list[BaseSysMenu]) -> list[dict]:
        """Build menu tree from flat list."""
        menu_dict = {}
        for menu in menus:
            menu_dict[menu.id] = {
                "id": menu.id,
                "parentId": menu.parentId,
                "name": menu.name,
                "router": menu.router,
                "perms": menu.perms,
                "type": menu.type,
                "icon": menu.icon,
                "orderNum": menu.orderNum,
                "viewPath": menu.viewPath,
                "keepAlive": menu.keepAlive,
                "isShow": menu.isShow,
                "children": [],
            }

        # Build tree structure
        tree = []
        for menu_id, menu_data in menu_dict.items():
            parent_id = menu_data["parentId"]
            if parent_id and parent_id in menu_dict:
                menu_dict[parent_id]["children"].append(menu_data)
            else:
                tree.append(menu_data)

        return tree


# Singleton instance
auth_service = AuthService()
