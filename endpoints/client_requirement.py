from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from sqlmodel import select
from models.product import (
    ClientRequirement,
    CreateClientRequirement,
    ClientRequirementProducts,
    RequirementProducts,
    Product,
)

router = APIRouter()


@router.post("/clientrequirement")
async def create_client_requirement(
    new_client_requirement_data: CreateClientRequirement,
    session: AsyncSession = Depends(get_session),
):
    try:
        # Create a new entry in the ClientRequirement table
        encoded_data = jsonable_encoder(new_client_requirement_data)
        new_client_requirement = ClientRequirement(**encoded_data)
        session.add(new_client_requirement)
        await session.commit()
        await session.refresh(new_client_requirement)
        # Fetch the list of Products in the Requirement table
        statement = (
            select(
                RequirementProducts.prod_id,
                RequirementProducts.prod_quantity,
                Product.description,
                Product.prod_name,
                Product.prd_price,
            )
            .join(Product, Product.prd_id == RequirementProducts.prod_id)
            .where(RequirementProducts.req_id == new_client_requirement_data.req_id)
        )

        requirement_products = (await session.exec(statement)).all()
        if not requirement_products:
            raise HTTPException(
                status_code=400, detail="No Requirement Found in this ID"
            )

        # With the ID create a new entry in the ClientRequirementProducts table
        new_client_requirement_products_list = []
        for requirement_product in requirement_products:
            requirement_product = requirement_product._asdict()
            new_client_requirement_product = ClientRequirementProducts(
                creq_id=new_client_requirement.creq_id,
                prd_id=requirement_product.get("prod_id"),
                quantity=requirement_product.get("prod_quantity"),
                description=requirement_product.get("description"),
            )
            new_client_requirement_products_list.append(new_client_requirement_product)

        session.add_all(new_client_requirement_products_list)
        await session.commit()

        return {"status": "ok"}

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))
