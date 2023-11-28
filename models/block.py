class Block:
    def __init__(
        self, 
        block_no: int, 
        miner_reward: str, 
        fee_recipient_eth_diff: str, 
        miner: str, 
        fee_recipient: str, 
        coinbase_transfers: str,
        eth_sent_to_fee_recipient: str, 
        gas_used: int,
        gas_price: str,
        effective_priority_fee: str
    ):
        self.block_no = block_no
        self.miner_reward = miner_reward
        self.fee_recipient_eth_diff = fee_recipient_eth_diff
        self.miner = miner
        self.fee_recipient = fee_recipient
        self.coinbase_transfers = coinbase_transfers
        self.eth_sent_to_fee_recipient = eth_sent_to_fee_recipient
        self.gas_used = gas_used
        self.gas_price = gas_price
        self.effective_priority_fee = effective_priority_fee
        self.timestamp = self.get_timestamp_by_blockno(block_no)

    @classmethod
    def get_timestamp_by_blockno(cls, block_no: int) -> int:
        pass

class Transaction:
    def __init__(
        self, 
        tx_hash: str, 
        block_no: int, 
        tx_index: int,
        bundle_type: str, 
        bundle_index: int, 
        eoa_address: str, 
        to_address: str, 
        gas_used: int,
        gas_price: str, 
        coinbase_transfer: str,
        eth_sent_to_fee_recipient: str, 
        total_miner_reward: str,
        fee_recipient_eth_diff: str
    ):
        self.tx_hash = tx_hash 
        self.block_no = block_no
        self.tx_index = tx_index
        self.bundle_type = bundle_type
        self.bundle_index = bundle_index
        self.eoa_address = eoa_address 
        self.to_address = to_address
        self.gas_used = gas_used
        self.gas_price = gas_price
        self.coinbase_transfer = coinbase_transfer
        self.eth_sent_to_fee_recipient = eth_sent_to_fee_recipient
        self.total_miner_reward = total_miner_reward
        self.fee_recipient_eth_diff = fee_recipient_eth_diff

