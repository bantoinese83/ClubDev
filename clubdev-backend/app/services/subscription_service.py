from datetime import datetime, timedelta
from functools import lru_cache
from uuid import UUID

import stripe
from fastapi import HTTPException, status
from sqlmodel import Session, select
import logging

from ..core.config import settings
from ..db.models import Subscription, SubscriptionPlan, User

stripe.api_key = settings.stripe_secret_key

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def create_subscription(self, user_id: UUID, plan_id: UUID) -> Subscription:
        # Retrieve the user and plan
        user = self.db.get(User, user_id)
        plan = self.db.get(SubscriptionPlan, plan_id)

        if not user:
            logger.error(f"User with ID {user_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not plan:
            logger.error(f"Subscription plan with ID {plan_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")

        # Create a Stripe customer if not already created
        if not user.stripe_customer_id:
            try:
                customer = stripe.Customer.create(email=user.email)
                user.stripe_customer_id = customer.id
                self.db.commit()
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error while creating customer: {str(e)}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating Stripe customer")

        # Create a Stripe subscription
        try:
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{"price": plan.stripe_price_id}],
                trial_period_days=3 if plan.name == "Free" else None
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while creating subscription: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating Stripe subscription")

        # Create a subscription record in the database
        new_subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status="Active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=3) if plan.name == "Free" else None,
            stripe_subscription_id=subscription.id
        )
        self.db.add(new_subscription)
        self.db.commit()
        self.db.refresh(new_subscription)

        logger.info(f"Subscription created for user ID {user_id} with plan ID {plan_id}")
        return new_subscription

    def cancel_subscription(self, user_id: UUID) -> None:
        # Retrieve the active subscription
        statement = select(Subscription).where(Subscription.user_id == user_id, Subscription.status == "Active")
        subscription = self.db.exec(statement).first()

        if not subscription:
            logger.error(f"Active subscription for user ID {user_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active subscription not found")

        # Cancel the Stripe subscription
        try:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error while canceling subscription: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error canceling Stripe subscription")

        # Update the subscription status in the database
        subscription.status = "Cancelled"
        subscription.end_date = datetime.now()
        self.db.commit()

        logger.info(f"Subscription for user ID {user_id} canceled")

    @lru_cache(maxsize=128)
    def get_subscription(self, user_id: UUID) -> Subscription:
        statement = select(Subscription).where(Subscription.user_id == user_id, Subscription.status == "Active")
        subscription = self.db.exec(statement).first()

        if not subscription:
            logger.error(f"Active subscription for user ID {user_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active subscription not found")

        return subscription

    @lru_cache(maxsize=128)
    def is_trial_period_over(self, user_id: UUID) -> bool:
        statement = select(Subscription).where(Subscription.user_id == user_id, Subscription.status == "Active")
        subscription = self.db.exec(statement).first()

        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active subscription not found")

        if subscription.end_date and subscription.end_date < datetime.now():
            return True
        return False