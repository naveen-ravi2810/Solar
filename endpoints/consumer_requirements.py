from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.db import get_session
from uuid import UUID
from models.product import (
    CreateConsumerRequirement,
    Requirement,
    RequirementProducts,
    ConsumerRequirement,
    ClientConsumer,
    ConsumerRequirementProduct,
    Product,
)
from sqlalchemy.orm import selectinload, joinedload
from schema.CosnumerRequirementProduct import ConsumerRequirementRead

router = APIRouter()


@router.post("/consumer_requirement")
async def create_consumer_requirement(
    create_consumer_requirement_data: CreateConsumerRequirement,
    session: AsyncSession = Depends(get_session),
):
    try:
        # Step 1: Fetch all products linked to the requirement
        products_stmt = select(RequirementProducts).where(
            RequirementProducts.req_id == create_consumer_requirement_data.req_id
        )
        products = (await session.exec(products_stmt)).all()

        if not products:
            raise HTTPException(
                status_code=404, detail="No products found for this requirement"
            )

        # Step 2: Fetch the consumer description
        consumer_stmt = select(ClientConsumer).where(
            ClientConsumer.ccm_id == create_consumer_requirement_data.ccm_id
        )
        consumer = (await session.exec(consumer_stmt)).one_or_none()
        if not consumer:
            raise HTTPException(status_code=404, detail="Consumer not found")

        # Step 3: Create a new ConsumerRequirement entry
        new_consumer_requirement = ConsumerRequirement(
            ccm_id=create_consumer_requirement_data.ccm_id,
            creq_name=create_consumer_requirement_data.creq_name,
            consumer_requirement_descriptin=consumer.clinet_consumer_requirement,
        )
        session.add(new_consumer_requirement)
        await session.commit()
        await session.refresh(new_consumer_requirement)

        # Step 4: Create ConsumerRequirementProduct entries
        for product in products:
            consumer_req_product = ConsumerRequirementProduct(
                con_req_id=new_consumer_requirement.con_req_id,
                prd_id=product.prod_id,
                quantity=product.prod_quantity,  # assuming RequirementProducts has `quantity`
            )
            session.add(consumer_req_product)

        await session.commit()
        await session.refresh(new_consumer_requirement)

        return new_consumer_requirement

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/consumer_requirement/{con_req_id}", response_model=ConsumerRequirementRead
)
async def get_consumer_requirement_details_by_id(
    con_req_id: UUID, session: AsyncSession = Depends(get_session)
):
    try:
        stmt = (
            select(ConsumerRequirement)
            .where(ConsumerRequirement.con_req_id == con_req_id)
            .join(ConsumerRequirement.consumer_requirement_products)
            .join(ConsumerRequirementProduct.product_details)
            .options(
                joinedload(
                    ConsumerRequirement.consumer_requirement_products
                ).joinedload(ConsumerRequirementProduct.product_details)
            )
            .order_by(Product.prod_name)  # ✅ use actual column
        )
        result = (await session.exec(stmt)).unique().one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="No requirement found")
        return result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
