from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import Row, RowMapping
from sqlmodel import Session, select
from ..db.models import Project, ProjectMember, ProjectScript, ProjectRoleAssignment, ProjectRolePermission
from ..db.schemas import ProjectCreate, ProjectUpdate, ProjectMemberCreate, ProjectScriptCreate, ProjectRoleAssignmentCreate, ProjectRolePermissionCreate
from ..core.exceptions import ItemNotFoundError, DatabaseError, PermissionDeniedError
from ..utils.permissions_util import has_permission

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, project_in: ProjectCreate) -> Project:
        try:
            project = Project(**project_in.model_dump())
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            return project
        except Exception as e:
            raise DatabaseError(f"Error creating project: {e}")

    def get_project(self, project_id: UUID) -> Project:
        statement = select(Project).where(Project.id == project_id)
        project = self.db.exec(statement).first()
        if not project:
            raise ItemNotFoundError(f"Project with ID {project_id} not found")
        return project

    def list_user_projects(self, user_id: UUID) -> Sequence[Row[Any] | RowMapping | Any]:
        statement = select(Project).join(ProjectMember).where(ProjectMember.user_id == user_id)
        projects = self.db.exec(statement).all()
        return projects

    def update_project(self, project_id: UUID, project_in: ProjectUpdate, user_id: UUID) -> Project:
        if not has_permission(user_id, project_id, "update_project", self.db):
            raise PermissionDeniedError("You do not have permission to update this project")
        project = self.get_project(project_id)
        for key, value in project_in.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: UUID, user_id: UUID):
        if not has_permission(user_id, project_id, "delete_project", self.db):
            raise PermissionDeniedError("You do not have permission to delete this project")
        project = self.get_project(project_id)
        self.db.delete(project)
        self.db.commit()

    def add_user_to_project(self, project_id: UUID, member_in: ProjectMemberCreate, user_id: UUID) -> Project:
        if not has_permission(user_id, project_id, "add_user_to_project", self.db):
            raise PermissionDeniedError("You do not have permission to add users to this project")
        project = self.get_project(project_id)
        member = ProjectMember(project_id=project_id, **member_in.model_dump())
        self.db.add(member)
        self.db.commit()
        self.db.refresh(project)
        return project

    def remove_user_from_project(self, project_id: UUID, user_id: UUID, requester_id: UUID):
        if not has_permission(requester_id, project_id, "remove_user_from_project", self.db):
            raise PermissionDeniedError("You do not have permission to remove users from this project")
        statement = select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        member = self.db.exec(statement).first()
        if not member:
            raise ItemNotFoundError(f"User with ID {user_id} not found in project {project_id}")
        self.db.delete(member)
        self.db.commit()

    def add_script_to_project(self, project_id: UUID, script_in: ProjectScriptCreate, user_id: UUID) -> Project:
        if not has_permission(user_id, project_id, "add_script_to_project", self.db):
            raise PermissionDeniedError("You do not have permission to add scripts to this project")
        project = self.get_project(project_id)
        script = ProjectScript(project_id=project_id, **script_in.model_dump())
        self.db.add(script)
        self.db.commit()
        self.db.refresh(project)
        return project

    def remove_script_from_project(self, project_id: UUID, script_id: UUID, user_id: UUID):
        if not has_permission(user_id, project_id, "remove_script_from_project", self.db):
            raise PermissionDeniedError("You do not have permission to remove scripts from this project")
        statement = select(ProjectScript).where(ProjectScript.project_id == project_id, ProjectScript.script_id == script_id)
        script = self.db.exec(statement).first()
        if not script:
            raise ItemNotFoundError(f"Script with ID {script_id} not found in project {project_id}")
        self.db.delete(script)
        self.db.commit()

    def assign_role_to_user(self, project_id: UUID, role_assignment_in: ProjectRoleAssignmentCreate, user_id: UUID) -> Project:
        if not has_permission(user_id, project_id, "assign_role_to_user", self.db):
            raise PermissionDeniedError("You do not have permission to assign roles in this project")
        project = self.get_project(project_id)
        role_assignment = ProjectRoleAssignment(project_id=project_id, **role_assignment_in.model_dump())
        self.db.add(role_assignment)
        self.db.commit()
        self.db.refresh(project)
        return project

    def remove_role_from_user(self, project_id: UUID, role_assignment_id: UUID, user_id: UUID):
        if not has_permission(user_id, project_id, "remove_role_from_user", self.db):
            raise PermissionDeniedError("You do not have permission to remove roles in this project")
        statement = select(ProjectRoleAssignment).where(ProjectRoleAssignment.project_id == project_id, ProjectRoleAssignment.id == role_assignment_id)
        role_assignment = self.db.exec(statement).first()
        if not role_assignment:
            raise ItemNotFoundError(f"Role assignment with ID {role_assignment_id} not found in project {project_id}")
        self.db.delete(role_assignment)
        self.db.commit()

    def assign_permission_to_role(self, project_id: UUID, permission_in: ProjectRolePermissionCreate, user_id: UUID) -> Project:
        if not has_permission(user_id, project_id, "assign_permission_to_role", self.db):
            raise PermissionDeniedError("You do not have permission to assign permissions in this project")
        project = self.get_project(project_id)
        role_permission = ProjectRolePermission(project_id=project_id, **permission_in.model_dump())
        self.db.add(role_permission)
        self.db.commit()
        self.db.refresh(project)
        return project

    def remove_permission_from_role(self, project_id: UUID, role_permission_id: UUID, user_id: UUID):
        if not has_permission(user_id, project_id, "remove_permission_from_role", self.db):
            raise PermissionDeniedError("You do not have permission to remove permissions in this project")
        statement = select(ProjectRolePermission).where(ProjectRolePermission.project_id == project_id, ProjectRolePermission.id == role_permission_id)
        role_permission = self.db.exec(statement).first()
        if not role_permission:
            raise ItemNotFoundError(f"Role permission with ID {role_permission_id} not found in project {project_id}")
        self.db.delete(role_permission)
        self.db.commit()