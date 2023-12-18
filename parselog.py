from web3 import Web3
import json
from pathlib import Path
import requests
from mev_analysis.config import config, logger
import abiutils

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
all_abis = abiutils.load_abis()
abi_sign_map = abiutils.load_abi_sign_map()

def test():
    tx_hash = '0xfce9f1222536ee7aa2406efec4c7fd57960f072ed948ba9851496181b597bbfd'
    test_contract_address = '0xDef1C0ded9bec7F1a1670819833240f027b25EfF'
    # with open('./ABIs/Uniswap_0xDef1C0ded9bec7F1a1670819833240f027b25EfF.json', 'r') as f:
    #     contract_abi = json.load(f)
    decode_log_by_tx(tx_hash)

def get_contract_info(address: str):
    endpoint = f'https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={address}&apikey={ETHERSCAN_API_KEY}'
    token = requests.get(endpoint).json()
    return {'symbol': token['symbol'], 'name': token['tokenName'], 'decimals': token['divisor']}

def get_wanted_events():
    return config['filter-events']

def parse_log_args(log):
    args = log['args']
    argstr = ''
    for (key, value) in args.items():
        argstr += f'{key}:{value},'
    argstr = argstr[0:-1]    
    return f'{log["blockNumber"]},{log["transactionIndex"]},{log["address"]},{log["logIndex"]}, {log["event"]}, {argstr}'

def save_decoded_logs(decode_logs):
    decoded_file = Path(config['paths']['decoded_logs'])
    if not decoded_file.exists():
        decoded_file.touch()
    with open(decoded_file, 'a') as f:
        for log in decode_logs:
            log_str = parse_log_args(log)
            f.write(f'{log_str}\n')

def filter_decode_events(contract, receipt):
    events = contract.events
    events_in_contract = [e.event_name for e in events]
    for w in get_wanted_events():
        for e in events_in_contract:
            if w.lower() == e.lower():
                decoded_logs = contract.events[w]().process_receipt(receipt)
                save_decoded_logs(decoded_logs)

def decode_log_by_tx(tx_hash):
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    abi_path = Path(config['paths']['ABI'])
    # loop logs
    for log in receipt['logs']:
        contract_address = log['address']
        
        log_event_signature = log['topics'][0].hex()
        if log_event_signature in abi_sign_map:
            abi_filename = abi_sign_map[log_event_signature]['contracts'][0]
            file_path = next(abi_path.glob(f'**/{abi_filename}.abi'))
            with file_path.open('r') as f:
                contract_abi = json.load(f)
            contract = w3.eth.contract(address=contract_address, abi=contract_abi)
            filter_decode_events(contract, receipt)
        # print(signature)
        # event['name'] = Swap
        # abi_events = [abi for abi in contract.abi if abi['type'] == 'event']
        # for abi_event in all_abis:
        #     # filter event by name
        #     if abi_event['name'].lower() in get_wanted_events():
        #         decoded_logs = contract.events[abi_event['name']]().process_receipt(receipt)
        #         print(decoded_logs)

# for abi_file in abi_path.glob('*.json'):
#     filename = abi_file.name
#     with open(abi_file, 'r') as f:
#         abi = json.load(f)
#         contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
#         receipt = w3.eth.get_transaction_receipt(tx_hash)

#         for log in receipt['logs']:
#             contract_address = log['address']
#             # contract_abi = get_contract_abi(contract_address)
#             # contract = w3.eth.contract(address=contract_address, abi=contract_abi)
#             signature = log['topics'][0].hex()
#             # print(signature)
#             # event['name'] = Swap
#             # abi_events = [abi for abi in contract.abi if abi['type'] == 'event']
#             # for abi_event in abi_events:
#             decoded_logs = contract.events['Swap']().process_receipt(receipt)
#             print(decoded_logs)



# contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# # Transaction Receipt
# tx_hash = '0xfce9f1222536ee7aa2406efec4c7fd57960f072ed948ba9851496181b597bbfd'
# receipt = w3.eth.get_transaction_receipt(tx_hash)

# log = contract.events.Swap().process_receipt(receipt)
# print(log)

def main():
    test()

if __name__ == '__main__':
    main()