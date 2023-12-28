from typing import List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from mev_analysis.models.prices import PriceModel
from mev_analysis.schemas.prices import Price


def find_price_by_token_address(db_session, token_address: str) -> Price:
    price = db_session.query(PriceModel).filter(PriceModel.token_address == token_address.lower()).first()
    return price


def write_prices(db_session, prices: List[Price]) -> None:
    insert_statement = (
        insert(PriceModel.__table__)
        .values([price.dict() for price in prices])
        .on_conflict_do_nothing()
    )

    db_session.execute(insert_statement)
    db_session.commit()


def write_price(db_session, prices: List[Price]) -> None:
    insert_statement = (
        insert(PriceModel.__table__)
        .values([price.model_dump() for price in prices])
        .on_conflict_do_nothing()
    )

    db_session.execute(insert_statement)
    db_session.commit()
