from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from ...db.database import get_db
from ...db.schemas import ProjectCreate, ProjectUpdate, ProjectRead, ProjectMemberCreate, ProjectScriptCreate, ProjectRoleAssignmentCreate, ProjectRolePermissionCreate
from ...services.project_service import ProjectService
from ...core.exceptions import ItemNotFoundError, DatabaseError
import logging

project_router = APIRouter()
logger = logging.getLogger(__name__)

@project_router.post("/projects/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.create_project(project_in)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.get("/projects/{project_id}", response_model=ProjectRead, tags=["Projects"])
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.get_project(project_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.get("/users/{user_id}/projects", response_model=list[ProjectRead], tags=["Projects"])
def list_user_projects(user_id: UUID, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.list_user_projects(user_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.put("/projects/{project_id}", response_model=ProjectRead, tags=["Projects"])
def update_project(project_id: UUID,user_id: UUID, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.update_project(project_id, project_in, user_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def delete_project(project_id: UUID,user_id: UUID, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        project_service.delete_project(project_id, user_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.post("/projects/{project_id}/members", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def add_user_to_project(project_id: UUID,user_id: UUID, member_in: ProjectMemberCreate, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.add_user_to_project(project_id, member_in, user_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.delete("/projects/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def remove_user_from_project(project_id: UUID, user_id: UUID,requester_id: UUID, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        project_service.remove_user_from_project(project_id, user_id, requester_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.post("/projects/{project_id}/scripts", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def add_script_to_project(project_id: UUID,user_id: UUID, script_in: ProjectScriptCreate, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.add_script_to_project(project_id, script_in, user_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.delete("/projects/{project_id}/scripts/{script_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def remove_script_from_project(project_id: UUID, script_id: UUID,user_id: UUID, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        project_service.remove_script_from_project(project_id, script_id, user_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.post("/projects/{project_id}/roles", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def assign_role_to_user(project_id: UUID,user_id: UUID, role_assignment_in: ProjectRoleAssignmentCreate, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.assign_role_to_user(project_id, role_assignment_in, user_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.delete("/projects/{project_id}/roles/{role_assignment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def remove_role_from_user(project_id: UUID, role_assignment_id: UUID,user_id: UUID, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        project_service.remove_role_from_user(project_id, role_assignment_id, user_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.post("/projects/{project_id}/permissions", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def assign_permission_to_role(project_id: UUID,user_id: UUID, permission_in: ProjectRolePermissionCreate, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        return project_service.assign_permission_to_role(project_id, permission_in, user_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@project_router.delete("/projects/{project_id}/permissions/{role_permission_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def remove_permission_from_role(project_id: UUID, role_permission_id: UUID,user_id: UUID, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    try:
        project_service.remove_permission_from_role(project_id, role_permission_id, user_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")