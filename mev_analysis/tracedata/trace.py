from sqlalchemy import ARRAY, JSON, Column, Integer, Numeric, String

from mev_analysis.models.base import Base


class TraceModel(Base):
    __tablename__ = "block_traces"

    block_number = Column(Numeric, primary_key=True)
    raw_traces = Column(JSON, nullable=False)
