from core.db import async_session
from models.product import Appliances
from sqlmodel import select


list_of_appliances = [
    {"appliance_name": "Ceiling Fan", "appliance_volt": 75},
    {"appliance_name": "Table Fan", "appliance_volt": 60},
    {"appliance_name": "Pedestal Fan", "appliance_volt": 70},
    {"appliance_name": "Exhaust Fan", "appliance_volt": 50},
    {"appliance_name": "LED Tube Light", "appliance_volt": 30},
    {"appliance_name": "CFL Bulb", "appliance_volt": 15},
    {"appliance_name": "LED Bulb", "appliance_volt": 10},
    {"appliance_name": "Refrigerator (200 L)", "appliance_volt": 180},
    {"appliance_name": "Refrigerator (300 L)", "appliance_volt": 220},
    {"appliance_name": "Washing Machine (Top Load)", "appliance_volt": 400},
    {"appliance_name": "Washing Machine (Front Load)", "appliance_volt": 600},
    {"appliance_name": "Microwave Oven", "appliance_volt": 1000},
    {"appliance_name": "Induction Cooktop", "appliance_volt": 1500},
    {"appliance_name": "Electric Kettle", "appliance_volt": 1200},
    {"appliance_name": "Water Heater (15 L)", "appliance_volt": 1800},
    {"appliance_name": "Water Heater (25 L)", "appliance_volt": 2200},
    {"appliance_name": "Mixer Grinder", "appliance_volt": 600},
    {"appliance_name": "Food Processor", "appliance_volt": 700},
    {"appliance_name": "Toaster", "appliance_volt": 1000},
    {"appliance_name": "Rice Cooker", "appliance_volt": 500},
    {"appliance_name": "Coffee Maker", "appliance_volt": 800},
    {"appliance_name": "Iron", "appliance_volt": 1200},
    {"appliance_name": "Hair Dryer", "appliance_volt": 1000},
    {"appliance_name": "Vacuum Cleaner", "appliance_volt": 750},
    {"appliance_name": "Air Conditioner (1 Ton)", "appliance_volt": 1200},
    {"appliance_name": "Air Conditioner (1.5 Ton)", "appliance_volt": 1800},
    {"appliance_name": "Room Heater (Oil-filled)", "appliance_volt": 1500},
    {"appliance_name": "Room Heater (Fan)", "appliance_volt": 1200},
    {"appliance_name": "Water Pump", "appliance_volt": 500},
    {"appliance_name": "LED TV (32 inch)", "appliance_volt": 50},
    {"appliance_name": "LED TV (50 inch)", "appliance_volt": 120},
    {"appliance_name": "Home Theatre System", "appliance_volt": 200},
    {"appliance_name": "Electric Iron Box", "appliance_volt": 1100},
    {"appliance_name": "Electric Stove", "appliance_volt": 1500},
    {"appliance_name": "Induction Rice Cooker", "appliance_volt": 400},
    {"appliance_name": "Electric Chimney", "appliance_volt": 200},
    {"appliance_name": "Electric Oven", "appliance_volt": 1200},
    {"appliance_name": "Dishwasher", "appliance_volt": 1300},
    {"appliance_name": "Sump Pump", "appliance_volt": 400},
    {"appliance_name": "Ceiling Lights", "appliance_volt": 25},
]


async def create_default_appliances():
    try:
        async with async_session() as session:
            appliances = []
            for i in list_of_appliances:
                appliances.append(i.get("appliance_name"))
            statement = select(Appliances.appliance_name).where(
                Appliances.appliance_name.in_(appliances)
            )
            result = (await session.exec(statement)).all()
            existing_appliances = set(result)

            new_appliances = [
                Appliances(**a)
                for a in list_of_appliances
                if a["appliance_name"] not in existing_appliances
            ]
            if new_appliances:
                session.add_all(new_appliances)
                await session.commit()
                print("Newly added appliances", len(new_appliances))
            else:
                print("Nothing to add")

    except Exception as e:
        print(e)
        return str(e)


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_default_appliances())
