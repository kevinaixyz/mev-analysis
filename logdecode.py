from web3 import Web3
import json

class LogDecoder:
    # Initialize a web3 instance with an Ethereum node
    w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
    
    with open('event_sign.json', 'r') as f:
        event_signatures = json.load(f)
    

    def __init__(self, contract, tx_hash):
        # Get contract ABI
        # contract_address = '0xDef1C0ded9bec7F1a1670819833240f027b25EfF'
        # self.contract_address = contract_address
        self.contract = contract
        self.receipt = w3.eth.get_transaction_receipt(tx_hash)

    @classmethod
    def query_topic_sign(hex_sign):
        url = f'https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_sign}'
        data = requests.get(url).json()
        return data['results'][0]
    
    def get_event_signature(self, logs):
        # Iterate over each log
        for log in logs:
            # Get the event signature
            event_signature = None
            for name, types in event_signatures.items():
                # e.g. {"Swap": ["uint256", "uint256", "uint256", "uint256"]}
                signature = f"{name}({','.join(types)})"
                event_hash = w3.keccak(text=signature).hex()
                if log['topics'][0] == event_hash:
                    event_signature = signature
                    break

            # If the event signature matches, decode the log
            if event_signature:
                # Get the event ABI
                event_abi = self.contract.events[event_signature].abi
                event_abi = {
                    'anonymous': False,
                    'inputs': [{'type': t} for t in event_signatures[event_signature]],
                    'name': event_signature,
                    'type': 'event'
                }

                # Decode the log
                decoded_log = w3.codec.decode_log(event_abi, log['tracedata'], log['topics'])

                # Print the decoded log
                print(decoded_log)



with open('./ABIs/Uniswap.json', 'r') as f:
    contract_abi = json.load(f)  # You can get it from the Ethereum explorer for the contract

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Transaction Receipt
tx_hash = '0xfce9f1222536ee7aa2406efec4c7fd57960f072ed948ba9851496181b597bbfd'
receipt = w3.eth.get_transaction_receipt(tx_hash)

log = contract.events.Swap().process_receipt(receipt)
print(log)
    



# # Parse logs
# logs = contract.logs.getFunctionImplementation().processReceipt(receipt)

# for log in logs:
#     print(log.args)  # This will print readable text (arguments of the event) from the log tracedata
