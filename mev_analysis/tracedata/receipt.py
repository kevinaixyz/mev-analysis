from sqlalchemy import JSON, Column, Numeric, String

from mev_analysis.models.base import Base


class ReceiptModel(Base):
    __tablename__ = "block_receipts"

    block_number = Column(Numeric, primary_key=True)
    raw_receipts = Column(JSON, nullable=False)
