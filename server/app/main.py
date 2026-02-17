from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_router
from app.core.config import settings

tags_metadata = [
    {
        "name": "Health",
        "description": "Service health and readiness checks"
    }
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ClinicalTrials.gov Change Monitoring System",
    openapi_tags=tags_metadata
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.include_router(api_router, prefix="/api/v1")