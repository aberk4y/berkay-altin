from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid

class PortfolioItemCreate(BaseModel):
    type: Literal['gold', 'currency']
    name: str
    nameEn: str
    quantity: float
    buyPrice: float

class PortfolioItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str = "default"
    type: Literal['gold', 'currency']
    name: str
    nameEn: str
    quantity: float
    buyPrice: float
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class PortfolioItemUpdate(BaseModel):
    quantity: Optional[float] = None
    buyPrice: Optional[float] = None