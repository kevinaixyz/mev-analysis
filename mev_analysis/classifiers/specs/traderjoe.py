from typing import List, Optional

from mev_analysis.classifiers.helpers import create_swap_from_pool_transfers
from mev_analysis.schemas.classifiers import ClassifierSpec, SwapClassifier
from mev_analysis.schemas.swaps import Swap
from mev_analysis.schemas.traces import DecodedCallTrace, Protocol
from mev_analysis.schemas.transfers import Transfer

TRADERJOE_V2_LBPAIR_ABI_NAME = "LBPairV2"


class TraderjoeV21SwapClassifier(SwapClassifier):
    @staticmethod
    def parse_swap(
        trace: DecodedCallTrace,
        prior_transfers: List[Transfer],
        child_transfers: List[Transfer],
    ) -> Optional[Swap]:

        recipient_address = trace.inputs.get("recipient", trace.from_address)

        swap = create_swap_from_pool_transfers(
            trace, recipient_address, prior_transfers, child_transfers
        )
        return swap


class TraderjoeV2SwapClassifier(SwapClassifier):
    @staticmethod
    def parse_swap(
        trace: DecodedCallTrace,
        prior_transfers: List[Transfer],
        child_transfers: List[Transfer],
    ) -> Optional[Swap]:

        recipient_address = trace.inputs.get("to", trace.from_address)

        swap = create_swap_from_pool_transfers(
            trace, recipient_address, prior_transfers, child_transfers
        )
        return swap


TRADERJOE_V1_CONTRACT_SPECS = [
    ClassifierSpec(
        abi_name="FactoryV1",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10"],
    ),
    ClassifierSpec(
        abi_name="RouterV1",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0x60aE616a2155Ee3d9A68541Ba4544862310933d4"],
    ),
]

TRADERJOE_V20_CONTRACT_SPECS = [
    ClassifierSpec(
        abi_name="LBFactoryV20",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0x6E77932A92582f504FF6c4BdbCef7Da6c198aEEf"],
    ),
    ClassifierSpec(
        abi_name="LBQuoterV20",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0x9dbf1706577636941ab5f443d2aebe251ccd1648"],
    ),
    ClassifierSpec(
        abi_name="LBRouterV20",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0xE3Ffc583dC176575eEA7FD9dF2A7c65F7E23f4C3"],
    ),
]
TRADERJOE_V21_CONTRACT_SPECS = [
    ClassifierSpec(
        abi_name="Joetroller",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=[""],
    ),
    ClassifierSpec(
        abi_name="LBFactoryV21",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0x8e42f2F4101563bF679975178e880FD87d3eFd4e"],
    ),
    ClassifierSpec(
        abi_name="LBQuoterV21",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0xd76019A16606FDa4651f636D9751f500Ed776250"],
    ),
    ClassifierSpec(
        abi_name="LBRouterV21",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0xb4315e873dBcf96Ffd0acd8EA43f689D8c20fB30"],
    ),
    ClassifierSpec(
        abi_name="LimitOrderManager",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0x46bA84780f9a7b34C8B0E24Df07a260Fa952195D"],
    ),
    ClassifierSpec(
        abi_name="TransparentUpgradeableProxy",
        protocol=Protocol.traderjoe,
        valid_contract_addresses=["0xA3D87597fDAfC3b8F3AC6B68F90CD1f4c05Fa960"],
    ),
]

TRADERJOE_CLASSIFIER_SPECS: List = [
    *TRADERJOE_V1_CONTRACT_SPECS,
    *TRADERJOE_V20_CONTRACT_SPECS,
    *TRADERJOE_V21_CONTRACT_SPECS,
]
