from sqlalchemy import Column, String

from .base import Base


class FunctionSignaturesModel(Base):
    __tablename__ = "function_signatures"

    function_signature = Column(String, nullable=False, primary_key=True)
    bytes_signature = Column(String, nullable=False, primary_key=True)
    function_name = Column(String, nullable=False)