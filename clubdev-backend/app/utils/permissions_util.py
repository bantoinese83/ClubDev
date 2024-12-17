from uuid import UUID
from sqlmodel import Session, select
from ..db.models import ProjectRoleAssignment, ProjectRolePermission

def has_permission(user_id: UUID, project_id: UUID, permission_name: str, db: Session) -> bool:
    role_assignment = db.exec(select(ProjectRoleAssignment).where(
        ProjectRoleAssignment.user_id == user_id,
        ProjectRoleAssignment.project_id == project_id
    )).first()

    if not role_assignment:
        return False

    permission = db.exec(select(ProjectRolePermission).where(
        ProjectRolePermission.role_id == role_assignment.role_id,
        ProjectRolePermission.permission_name == permission_name
    )).first()

    return permission is not None