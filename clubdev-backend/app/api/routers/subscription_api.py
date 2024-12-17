from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
import logging

from ...db.database import get_db
from ...db.schemas import SubscriptionCreate, SubscriptionRead
from ...services.subscription_service import SubscriptionService

subscription_router = APIRouter()
logger = logging.getLogger(__name__)

@subscription_router.post("/subscriptions/", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED, tags=["Subscriptions 📅"])
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    try:
        new_subscription = service.create_subscription(subscription.user_id, subscription.plan_id)
        logger.info(f"Subscription created for user ID {subscription.user_id} with plan ID {subscription.plan_id}")
        return new_subscription
    except HTTPException as e:
        logger.error(f"Error creating subscription: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating subscription: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@subscription_router.delete("/subscriptions/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Subscriptions 📅"])
def cancel_subscription(user_id: UUID, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    try:
        service.cancel_subscription(user_id)
        logger.info(f"Subscription for user ID {user_id} canceled")
        return {"message": "Subscription canceled successfully"}
    except HTTPException as e:
        logger.error(f"Error canceling subscription: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error canceling subscription: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@subscription_router.get("/subscriptions/{user_id}", response_model=SubscriptionRead, tags=["Subscriptions 📅"])
def get_subscription(user_id: UUID, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    try:
        subscription = service.get_subscription(user_id)
        if not subscription:
            logger.warning(f"Active subscription for user ID {user_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active subscription not found")
        return subscription
    except HTTPException as e:
        logger.error(f"Error retrieving subscription: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error retrieving subscription: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")