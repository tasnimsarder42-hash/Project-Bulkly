import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models import User, Organization, Lead, Campaign

async def seed():
    print("Starting database seed...")
    await init_db()
    
    async with SessionLocal() as db:
        # Create Org
        org_id = str(uuid.uuid4())
        org = Organization(
            id=org_id,
            name="Bulkly Demo Inc",
            slug="bulkly-demo",
        )
        db.add(org)

        # Create Admin User
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email="admin@bulkly.app",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role="org_admin",
            org_id=org_id,
            is_active=True,
            is_verified=True,
        )
        db.add(user)

        # Create Leads
        leads_data = [
            {"name": "Alex Johnson", "email": "alex.j@example.com", "phone": "+1 555-0192", "source": "Meta Ads", "status": "New", "score": 85},
            {"name": "Sarah Williams", "email": "swilliams@acme.co", "phone": "+1 555-0144", "source": "Organic Search", "status": "Contacted", "score": 92},
            {"name": "Michael Brown", "email": "michael.b@techstartup.io", "phone": "+44 7700 900077", "source": "LinkedIn", "status": "Qualified", "score": 78},
        ]
        
        for l in leads_data:
            lead = Lead(
                id=str(uuid.uuid4()),
                org_id=org_id,
                full_name=l["name"],
                email=l["email"],
                phone=l["phone"],
                source=l["source"],
                status=l["status"],
                score=l["score"]
            )
            db.add(lead)

        # Create Campaigns
        camps_data = [
            {"name": "Q3 Retargeting - All Visitors", "platform": "Meta", "status": "Active", "budget": 50.0},
            {"name": "Search - High Intent Keywords", "platform": "Google", "status": "Active", "budget": 100.0},
        ]
        
        for c in camps_data:
            camp = Campaign(
                id=str(uuid.uuid4()),
                org_id=org_id,
                name=c["name"],
                platform=c["platform"],
                status=c["status"],
                budget_daily=c["budget"],
            )
            db.add(camp)

        await db.commit()
        print(f"Seed complete! Log in with admin@bulkly.app / admin123")

if __name__ == "__main__":
    asyncio.run(seed())
