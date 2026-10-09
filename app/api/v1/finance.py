from fastapi import APIRouter
from app.api.v1.schemas import MortgageRequest
from app.finance.mortgage import mortgage_payment

router = APIRouter(prefix='/finance', tags=['Financial Tools'])


@router.post('/mortgage-estimate')
async def estimate(req: MortgageRequest):
    return mortgage_payment(req.principal, req.annual_rate_percent, req.years)
