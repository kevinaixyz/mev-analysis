from sqlalchemy import Column, Numeric, String, Integer

from mev_analysis.models.base import Base


class BlockTimestampModel(Base):
    __tablename__ = "block_timestamps"

    block_number = Column(Numeric, primary_key=True)
    block_timestamp = Column(Integer, nullable=False)