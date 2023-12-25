from typing import List, Optional

from mev_analysis.classifiers.helpers import get_debt_transfer, get_received_transfer
from mev_analysis.schemas.classifiers import (
    ClassifiedTrace,
    ClassifierSpec,
    DecodedCallTrace,
    LiquidationClassifier,
    TransferClassifier,
)
from mev_analysis.schemas.liquidations import Liquidation
from mev_analysis.schemas.traces import Protocol
from mev_analysis.schemas.transfers import Transfer


class BenqiLiquidationClassifier(LiquidationClassifier):
    @staticmethod
    def parse_liquidation(
        liquidation_trace: DecodedCallTrace,
        child_transfers: List[Transfer],
        child_traces: List[ClassifiedTrace],
    ) -> Optional[Liquidation]:

        liquidator = liquidation_trace.from_address
        liquidated = liquidation_trace.inputs["_user"]

        debt_token_address = liquidation_trace.inputs["_reserve"]
        received_token_address = liquidation_trace.inputs["_collateral"]

        debt_purchase_amount = None
        received_amount = None

        debt_transfer = get_debt_transfer(liquidator, child_transfers)

        received_transfer = get_received_transfer(liquidator, child_transfers)

        if debt_transfer is not None and received_transfer is not None:

            debt_token_address = debt_transfer.token_address
            debt_purchase_amount = debt_transfer.amount

            received_token_address = received_transfer.token_address
            received_amount = received_transfer.amount

            return Liquidation(
                liquidated_user=liquidated,
                debt_token_address=debt_token_address,
                liquidator_user=liquidator,
                debt_purchase_amount=debt_purchase_amount,
                protocol=Protocol.aave,
                received_amount=received_amount,
                received_token_address=received_token_address,
                transaction_hash=liquidation_trace.transaction_hash,
                trace_address=liquidation_trace.trace_address,
                block_number=liquidation_trace.block_number,
                error=liquidation_trace.error,
            )

        else:
            return None


class BenqiTransferClassifier(TransferClassifier):
    @staticmethod
    def get_transfer(trace: DecodedCallTrace) -> Transfer:
        return Transfer(
            block_number=trace.block_number,
            transaction_hash=trace.transaction_hash,
            trace_address=trace.trace_address,
            amount=trace.inputs["value"],
            to_address=trace.inputs["to"],
            from_address=trace.inputs["from"],
            token_address=trace.to_address,
        )


QITOKENS_SPEC = ClassifierSpec(
    abi_name="qiTokens",
    protocol=Protocol.benqi,
    classifiers={
        "liquidateBorrow(address,address)": BenqiLiquidationClassifier,
        "liquidateBorrow(address,address,uint256,address,uint256)": BenqiLiquidationClassifier,
    },
)

QIERC20DELEGATE_SPEC = ClassifierSpec(
    abi_name="QiErc20Delegate",
    protocol=Protocol.benqi,
    classifiers={
        "liquidateBorrow(address,uint256,address)": BenqiLiquidationClassifier,
    },
)

BENQI_CLASSIFIER_SPECS: List[ClassifierSpec] = [QITOKENS_SPEC, QIERC20DELEGATE_SPEC]
