# from sqlmodel import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from uuid import UUID
# from models.product import *

# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML


# async def get_quotation_data(session: AsyncSession, req_id: UUID):
#     # Fetch quotation for this requirement
#     quotation =(await session.exec(
#         select(Quotation).where(Quotation.req_id == req_id)
#     )).first()

#     if not quotation:
#         raise ValueError("Quotation not found for given req_id")

#     # Fetch products for this requirement
#     results = (
#         await session.exec(
#             select(RequirementProducts, Product)
#             .where(RequirementProducts.req_id == req_id)
#             .join(Product, Product.prd_id == RequirementProducts.prod_id)
#         )
#     ).all()

#     products = []

#     # For total cose
#     sub_total = 0
#     total_cgst = 0
#     total_sgst = 0

#     for rp, product in results:
#         base_total = product.prd_price * rp.prod_quantity
#         gst_amount = base_total * (product.prd_gst / 100)
#         cgst_amount = gst_amount / 2
#         sgst_amount = gst_amount / 2

#         # final product cost including gst (if you need per-row total with GST)
#         final_total = base_total + gst_amount

#         products.append(
#             {
#                 "description": product.description,
#                 "name": product.prod_name,
#                 "capacity": product.prd_capacity,
#                 "qty": rp.prod_quantity,
#                 "price": product.prd_price,
#                 "base_total": base_total,
#                 "total": final_total,  # optional, if you want to display GST-included cost
#             }
#         )

#         sub_total += base_total
#         total_cgst += cgst_amount
#         total_sgst += sgst_amount
#     return quotation, products, sub_total, cgst_amount, sgst_amount, final_total


# async def generate_pdf(
#     quotation,
#     products,
#     sub_total,
#     cgst_amount,
#     sgst_amount,
#     final_total,
#     output_file="quotation.pdf",
# ):
#     env = Environment(loader=FileSystemLoader("template/quotation"))
#     template = env.get_template("2025_9_9_1.html")

#     html_content = template.render(
#         quotation=quotation,
#         products=products,
#         sub_total=sub_total,
#         cgst=cgst_amount,
#         sgst=sgst_amount,
#         total=final_total,
#     )

#     HTML(string=html_content).write_pdf(output_file)
#     return output_file
