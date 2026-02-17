from fastapi import APIRouter
from app.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="UP",
        service="ClinicalTrials Change Monitoring System"
    )


api_router = router