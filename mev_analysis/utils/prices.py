from datetime import datetime
from typing import List

from pycoingecko import CoinGeckoAPI

from mev_analysis.schemas.prices import COINGECKO_ID_BY_ADDRESS, TOKEN_ADDRESSES, STABLE_COINS, Price
from mev_analysis.crud.prices import find_price_by_token_address, write_price

def fetch_prices() -> List[Price]:
    coingecko_api = CoinGeckoAPI()
    prices = []

    for token_address in TOKEN_ADDRESSES:
        coingecko_price_data = coingecko_api.get_coin_market_chart_by_id(
            id=COINGECKO_ID_BY_ADDRESS[token_address],
            vs_currency="usd",
            days="max",
            interval="daily",
        )
        prices += _build_token_prices(coingecko_price_data, token_address)

    return prices


def fetch_and_save_prices_range(db_session, after: datetime, before: datetime) -> List[Price]:
    coingecko_api = CoinGeckoAPI()
    prices = []
    after_unix = int(after.timestamp())
    before_unix = int(before.timestamp())

    for token_address in TOKEN_ADDRESSES:
        if token_address.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
            continue

        if token_address in STABLE_COINS:
            continue

        try:
            p = find_price_by_token_address(db_session, token_address)
            if p is None:
                coingecko_price_data = coingecko_api.get_coin_market_chart_range_from_contract_address_by_id(
                    'ethereum', token_address, "usd", after_unix, before_unix
                )

                price = _build_token_prices(coingecko_price_data, token_address)
                write_price(db_session, price)

        except ValueError as e:
            print(e)
            continue

    return prices


def _build_token_prices(coingecko_price_data, token_address) -> List[Price]:
    time_series = coingecko_price_data["prices"]
    prices = []
    for entry in time_series:
        timestamp = datetime.fromtimestamp(entry[0] / 1000)
        token_price = entry[1]
        prices.append(
            Price(
                timestamp=timestamp,
                usd_price=token_price,
                token_address=token_address.lower(),
            )
        )
    return prices
