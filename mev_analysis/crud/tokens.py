from typing import List, Optional

from sqlalchemy.dialects.postgresql import insert

from mev_analysis.models.tokens import TokenModel
from mev_analysis.schemas.prices import Token


def write_tokens(db_session, tokens: List[Token]) -> None:
    insert_statement = (
        insert(TokenModel.__table__)
        .values([token.model_dump() for token in tokens])
        .on_conflict_do_nothing()
    )

    db_session.execute(insert_statement)
    db_session.commit()


def write_token(db_session, token: Token) -> None:
    insert_statement = (
        insert(TokenModel.__table__)
        .values(token.model_dump())
        .on_conflict_do_nothing()
    )

    db_session.execute(insert_statement)
    db_session.commit()


def find_token(db_session, token_address: str) -> Optional[Token]:
    return db_session.get(TokenModel, token_address.lower())
