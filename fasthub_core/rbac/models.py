"""
Modele RBAC — Role, Permission, powiązania.

Struktura:
  Organization --has many--> Roles --has many--> Permissions
  User --has many--> UserRoles --belongs to--> Role

Każda organizacja ma SWOJE role (oprócz systemowych).
Permissions są globalne — wspólne dla wszystkich organizacji.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


class Permission(BaseModel):
    """
    Pojedyncze uprawnienie, np. "team.view_members" lub "billing.change_plan".
    Permissions są GLOBALNE — nie per organizacja.
    Aplikacja (AutoFlow, CRM) rejestruje swoje permissions przy starcie.
    """
    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)


class Role(BaseModel):
    """
    Rola w organizacji, np. "Admin", "Księgowy", "Kierownik Projektu".
    Każda organizacja może mieć własne role + role systemowe (wspólne).
    """
    __tablename__ = "roles"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)

    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class RolePermission(BaseModel):
    """Powiązanie Role <-> Permission (many-to-many)"""
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission")


class UserRole(BaseModel):
    """Powiązanie User <-> Role w kontekście organizacji"""
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    role = relationship("Role", back_populates="user_roles")
