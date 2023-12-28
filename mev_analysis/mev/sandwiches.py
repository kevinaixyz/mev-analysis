from typing import List, Optional

from mev_analysis.schemas.sandwiches import Sandwich
from mev_analysis.schemas.swaps import Swap

UNISWAP_V2_ROUTER = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
UNISWAP_V3_ROUTER = "0xe592427a0aece92de3edee1f18e0157c05861564"
UNISWAP_V3_ROUTER_2 = "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45"


def get_sandwiches(swaps: List[Swap]) -> List[Sandwich]:
    ordered_swaps = list(
        sorted(
            swaps,
            key=lambda swap: (swap.transaction_position, swap.trace_address),
        )
    )

    sandwiches: List[Sandwich] = []

    for index, swap in enumerate(ordered_swaps):
        rest_swaps = ordered_swaps[index + 1 :]
        sandwich = _get_sandwich_starting_with_swap(swap, rest_swaps)

        if sandwich is not None:
            sandwiches.append(sandwich)

    return sandwiches


def _get_sandwich_starting_with_swap(
    front_swap: Swap,
    rest_swaps: List[Swap],
) -> Optional[Sandwich]:
    sandwicher_address = front_swap.to_address.lower()
    sandwiched_swaps = []

    if sandwicher_address in [
        UNISWAP_V2_ROUTER.lower(),
        UNISWAP_V3_ROUTER.lower(),
        UNISWAP_V3_ROUTER_2.lower(),
    ]:
        return None

    for other_swap in rest_swaps:
        if other_swap.transaction_hash == front_swap.transaction_hash:
            continue

        if other_swap.contract_address.lower() == front_swap.contract_address.lower():
            if (
                other_swap.token_in_address.lower() == front_swap.token_in_address.lower()
                and other_swap.token_out_address.lower() == front_swap.token_out_address.lower()
                and other_swap.from_address.lower() != sandwicher_address.lower()
            ):
                sandwiched_swaps.append(other_swap)
            elif (
                other_swap.token_out_address.lower() == front_swap.token_in_address.lower()
                and other_swap.token_in_address.lower() == front_swap.token_out_address.lower()
                and other_swap.from_address.lower() == sandwicher_address.lower()
            ):
                if len(sandwiched_swaps) > 0:
                    return Sandwich(
                        block_number=front_swap.block_number,
                        sandwicher_address=sandwicher_address.lower(),
                        frontrun_swap=front_swap,
                        backrun_swap=other_swap,
                        sandwiched_swaps=sandwiched_swaps,
                        profit_token_address=front_swap.token_in_address.lower(),
                        profit_amount=other_swap.token_out_amount
                        - front_swap.token_in_amount,
                    )

    return None
