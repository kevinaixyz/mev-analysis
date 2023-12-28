from typing import Dict, Optional

import eth_utils.abi
from eth_abi import decode
from eth_abi.exceptions import InsufficientDataBytes, NonEmptyPaddingBytes
from hexbytes._utils import hexstr_to_bytes
from sqlalchemy import orm, select

from mev_analysis.models.function_signatures import FunctionSignaturesModel
from mev_analysis.schemas.abi import ABI, ABIFunctionDescription
from mev_analysis.schemas.call_data import CallData
from mev_analysis.schemas.traces import Classification

# 0x + 8 characters
SELECTOR_LENGTH = 10


class ABIDecoder:
    def __init__(self, abi: ABI):
        self._functions_by_selector: Dict[str, ABIFunctionDescription] = {
            description.get_selector(): description
            for description in abi
            if isinstance(description, ABIFunctionDescription)
        }

    def decode(self, data: str) -> Optional[CallData]:
        selector, params = data[:SELECTOR_LENGTH], data[SELECTOR_LENGTH:]

        func = self._functions_by_selector.get(selector)

        if func is None:
            return None

        names = [input.name for input in func.inputs]
        types = [
            input.type
            if input.type != "tuple"
            else eth_utils.abi.collapse_if_tuple(input.dict())
            for input in func.inputs
        ]

        try:
            decoded = decode(types, hexstr_to_bytes(params))
        except (InsufficientDataBytes, NonEmptyPaddingBytes, OverflowError):
            return None

        return CallData(
            function_name=func.name,
            function_signature=func.get_signature(),
            inputs={name: value for name, value in zip(names, decoded)},
        )

    @classmethod
    def generalised_decode(cls, data: str, db_session: orm.session) -> Optional[CallData]:
        selector = data[:SELECTOR_LENGTH]
        function_signature = (db_session
                  .execute(select(FunctionSignaturesModel)
                           .filter_by(bytes_signature=selector))
                ).scalar_one_or_none()
        # if len(function_signatures) > 1:
        #     for fs in function_signatures:
        #         for type in Classification:
        #             if fs['function_name'].lower().index(type.value) >= 0:
        #                 function_signature = fs
        if function_signature is not None:
            return CallData(
                function_name=function_signature.function_name,
                function_signature=function_signature.function_signature,
            )
        return None