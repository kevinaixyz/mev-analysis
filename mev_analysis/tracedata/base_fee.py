from sqlalchemy import ARRAY, JSON, Column, Integer, Numeric, String

from mev_analysis.models.base import Base


class BaseFeeModel(Base):
    __tablename__ = "base_fee"

    block_number = Column(Numeric, primary_key=True)
    base_fee_in_wei = Column(Numeric, nullable=False)
