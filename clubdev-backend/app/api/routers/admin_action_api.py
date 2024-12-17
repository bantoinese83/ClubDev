from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from ...db.database import get_session
from ...db.models import User
from ...db.schemas import AdminActionCreate, AdminActionRead, AdminActionUpdate
from ...services.admin_action_service import AdminActionService
from ..deps import get_current_admin_user

admin_action_router = APIRouter()

@admin_action_router.post(
    "/admin-actions/",
    response_model=AdminActionRead,
    tags=["Admin Actions 🛠️"],
    description="Create a new admin action."
)
def create_admin_action(
        admin_action: AdminActionCreate,
        db: Session = Depends(get_session),
        current_admin: User = Depends(get_current_admin_user)
):
    service = AdminActionService(db)
    return service.create_admin_action(admin_action)

@admin_action_router.get(
    "/admin-actions/{admin_action_id}",
    response_model=AdminActionRead,
    tags=["Admin Actions 🛠️"],
    description="Retrieve an admin action by its ID."
)
def read_admin_action(admin_action_id: UUID, db: Session = Depends(get_session),
                      current_admin: User = Depends(get_current_admin_user)):
    service = AdminActionService(db)
    admin_action = service.get_admin_action(admin_action_id)
    if not admin_action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin action not found")
    return admin_action

@admin_action_router.put(
    "/admin-actions/{admin_action_id}",
    response_model=AdminActionRead,
    tags=["Admin Actions 🛠️"],
    description="Update an existing admin action by its ID."
)
def update_admin_action(
        admin_action_id: UUID,
        admin_action: AdminActionUpdate,
        db: Session = Depends(get_session),
        current_admin: User = Depends(get_current_admin_user)
):
    service = AdminActionService(db)
    updated_admin_action = service.update_admin_action(admin_action_id, admin_action)
    if not updated_admin_action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin action not found")
    return updated_admin_action

@admin_action_router.delete(
    "/admin-actions/{admin_action_id}",
    response_model=AdminActionRead,
    tags=["Admin Actions 🛠️"],
    description="Delete an admin action by its ID."
)
def delete_admin_action(admin_action_id: UUID, db: Session = Depends(get_session),
                        current_admin: User = Depends(get_current_admin_user)):
    service = AdminActionService(db)
    admin_action = service.get_admin_action(admin_action_id)
    if not admin_action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin action not found")
    service.delete_admin_action(admin_action_id)
    return admin_action