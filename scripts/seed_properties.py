import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.mongodb import connect_mongodb, close_mongodb, get_database
from app.utils.common import utcnow

SAMPLES = [
    {
        'title': 'Modern Villa with Ocean View', 'listing_type': 'sale', 'property_class': 'residential', 'property_type': 'villa',
        'price': {'amount': 4500000000, 'currency': 'IDR'}, 'location': {'province': 'Bali', 'city': 'Denpasar', 'area': 'Jimbaran'},
        'specifications': {'bedrooms': 4, 'bathrooms': 3, 'size_m2': 320, 'lot_size_m2': 500, 'building_size_m2': 320, 'facing_direction': 'South'},
        'legal': {'certificate_type': 'SHM'},
        'utilities': {'electricity_watt': 2200},
        'agent': {'name': 'Demo Agent', 'whatsapp': '+6281234567890'},
        'calling': {'inbound_number': '+6280000000001'},
        'amenities': ['pool', 'garden', 'parking'],
        'status': 'active', 'description': 'Modern villa with ocean view.', 'created_at': utcnow()
    },
    {
        'title': 'Cozy Apartment in Business District', 'listing_type': 'sale', 'property_class': 'residential', 'property_type': 'apartment',
        'price': {'amount': 850000000, 'currency': 'IDR'}, 'location': {'province': 'DKI Jakarta', 'city': 'Jakarta Selatan', 'area': 'SCBD'},
        'specifications': {'bedrooms': 2, 'bathrooms': 2, 'size_m2': 85, 'building_size_m2': 85, 'facing_direction': 'East'},
        'legal': {'certificate_type': 'HGB'},
        'utilities': {'electricity_watt': 1300},
        'agent': {'name': 'Demo Agent', 'whatsapp': '+6281234567890'},
        'calling': {'inbound_number': '+6280000000002'},
        'amenities': ['gym', 'security'],
        'status': 'active', 'description': 'City apartment in SCBD.', 'created_at': utcnow()
    },
]

async def main():
    await connect_mongodb()
    db = get_database()
    if await db.properties.count_documents({}) == 0:
        await db.properties.insert_many(SAMPLES)
        print('Seeded sample properties')
    else:
        print('Properties already exist; skipping seed')
    await close_mongodb()

if __name__ == '__main__':
    asyncio.run(main())
