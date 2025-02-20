from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from readme_ai.settings import get_settings
import stripe
from readme_ai.models.requests.payments import CheckoutRequest

settings = get_settings()
router = APIRouter(prefix="/payments", tags=["payments"])

stripe.api_key = settings.STRIPE_API_KEY


@router.post("/create-checkout-session")
async def create_checkout_session(checkout_data: CheckoutRequest):
    try:
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            line_items=[
                {
                    "price": item.price_id,
                    "quantity": item.quantity,
                }
                for item in checkout_data.items
            ],
            mode="payment",
            return_url=settings.APP_URL + "/return?session_id={CHECKOUT_SESSION_ID}",
        )
        return JSONResponse(content={"clientSecret": session.client_secret})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session-status")
async def get_session_status(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "status": session.status,
            "customer_email": (
                session.customer_details.email if session.customer_details else None
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
