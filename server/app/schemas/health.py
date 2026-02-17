from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str

    class Config:
        frozen = True