from sqlalchemy import Column, Numeric, String, INTEGER

from .base import Base


class TokenModel(Base):
    __tablename__ = "tokens"

    token_address = Column(String, nullable=False, primary_key=True)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    decimals = Column(INTEGER, nullable=False)

