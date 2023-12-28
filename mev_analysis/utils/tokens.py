from typing import List

from sqlalchemy import orm
from web3 import Web3
from web3.eth import AsyncEth

from mev_analysis.mevanalysis import get_base_provider
from mev_analysis.models.tokens import TokenModel
from mev_analysis.schemas.prices import TOKEN_ADDRESSES, Token

from mev_analysis.crud.tokens import write_token, find_token


class TokenLoader:
    def __init__(self, db_session: orm.session, rpc: str, request_timeout: int = 300):
        self.db_session = db_session
        base_provider = get_base_provider(rpc, request_timeout)
        self.w3 = Web3(base_provider, modules={"eth": (AsyncEth,)}, middlewares=[])

    async def fetch_and_save_tokens(self) -> None:
        tokens = []
        for token_address in TOKEN_ADDRESSES:

            if find_token(self.db_session, token_address) is not None:
                continue

            if token_address.lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
                continue

            resp = await self.w3.provider.make_request('qn_getTokenMetadataByContractAddress', [{
                "contract": token_address
            }])

            if (resp is not None) and (resp['result'] is not None):
                write_token(self.db_session, Token(
                    token_address=token_address.lower(),
                    symbol=resp['result']['symbol'],
                    name=resp['result']['name'],
                    decimals=resp['result']['decimals'],
                ))
