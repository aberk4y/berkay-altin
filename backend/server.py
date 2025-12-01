from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Load environment variables BEFORE importing services
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from models import PortfolioItem, PortfolioItemCreate, PortfolioItemUpdate
from harem_api_service import harem_api_service

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "Harem Altın API"}

# Get Gold & Currency Prices
@api_router.get("/prices")
async def get_prices(type: Optional[str] = "all"):
    """Get real-time gold and currency prices from Harem Altın API"""
    try:
        prices_data = harem_api_service.get_all_prices()
        
        result = {
            "lastUpdate": datetime.utcnow().isoformat()
        }
        
        if type in ["all", "gold"]:
            result["gold"] = prices_data.get("gold", [])
        
        if type in ["all", "currency"]:
            result["currency"] = prices_data.get("currency", [])
        
        return result
    except Exception as e:
        logging.error(f"Error fetching prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio Management
@api_router.post("/portfolio", response_model=PortfolioItem)
async def create_portfolio_item(item: PortfolioItemCreate):
    """Create new portfolio item"""
    try:
        portfolio_item = PortfolioItem(**item.dict())
        await db.portfolio.insert_one(portfolio_item.dict())
        return portfolio_item
    except Exception as e:
        logging.error(f"Error creating portfolio item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/portfolio", response_model=List[PortfolioItem])
async def get_portfolio():
    """Get all portfolio items"""
    try:
        items = await db.portfolio.find({"userId": "default"}).to_list(1000)
        return [PortfolioItem(**item) for item in items]
    except Exception as e:
        logging.error(f"Error fetching portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/portfolio/{item_id}", response_model=PortfolioItem)
async def update_portfolio_item(item_id: str, update: PortfolioItemUpdate):
    """Update portfolio item"""
    try:
        update_data = {k: v for k, v in update.dict().items() if v is not None}
        update_data["updatedAt"] = datetime.utcnow()
        
        result = await db.portfolio.find_one_and_update(
            {"id": item_id, "userId": "default"},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Portfolio item not found")
        
        return PortfolioItem(**result)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating portfolio item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/portfolio/{item_id}")
async def delete_portfolio_item(item_id: str):
    """Delete portfolio item"""
    try:
        result = await db.portfolio.delete_one({"id": item_id, "userId": "default"})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Portfolio item not found")
        
        return {"message": "Portfolio item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting portfolio item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()