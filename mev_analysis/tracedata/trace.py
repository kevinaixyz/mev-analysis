from sqlalchemy import JSON, Column, Numeric

from mev_analysis.models.base import Base


class BlockTraceModel(Base):
    __tablename__ = "block_traces"

    block_number = Column(Numeric, primary_key=True)
    raw_traces = Column(JSON, nullable=False)
