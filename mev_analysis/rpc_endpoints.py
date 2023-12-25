from enum import Enum


class EthereumRpcEndpoint(Enum):
    trace_block = 'trace_block'
    fee_history = ''


class AvalancheRpcEndpoint(Enum):
    trace_block = 'debug_traceBlockByNumber'
    fee_history = ''


