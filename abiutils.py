from web3 import Web3
import json
import requests
from pathlib import Path
from config import *
from utils import is_valid_abi, is_json

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# Return contract addresses for the protocols
def load_contact_addresses():
    address_map_path = Path('./contract_addresses.json')
    
    with address_map_path.open('r') as f:
        protocol_address_map = json.load(f)
    
    return protocol_address_map    

# Download the contract's abi to local filesystem
# Save as .abi file
def download_contract_abi() -> dict:
    ETHERSCAN_API_KEY = get_key('Etherscan', 'API_KEY')
    root_abi_path = Path(config['paths']['ABI'])
    protocol_address_map = load_contact_addresses()
    for protocol in protocol_address_map:
        protocol_path = root_abi_path / f'{protocol}'
        if not protocol_path.exists():
            protocol_path.mkdir()
        for (address, label) in protocol_address_map[protocol].items():
            abi_path = protocol_path / f'{address}.abi'
            if abi_path.exists():
                continue
            abi_endpoint = f'https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_API_KEY}'
            abi = json.loads(requests.get(abi_endpoint).text)
            #  check if return is valid
            if is_json(abi['result']):
                save_abi(abi['result'], abi_path)
                logger.info(f'{label} ({address}) is downloaded.')
            else:
                logger.error(f'Invalid ABI for contract: {address}')

# Save the abi to file
def save_abi(abi:dict, save_path:Path):
    if save_path.exists():
        return
    
    with open(save_path, 'w') as f:
        json.dump(abi, f)

# Load all abis and return a list
def load_abis(protocol: str = None, abi_type: str = 'event') -> list:
    all_abis = {}
    if protocol is not None:
        paths = (Path(config['paths']['ABI']) / f'{protocol}').glob('*.abi')
    else:    
        paths = Path(config['paths']['ABI']).rglob('*.abi')
        
    for abi_file_path in paths:
        with abi_file_path.open('r') as f:
            abi = json.load(f)
            if type(abi) != list:
                abi = json.loads(abi)
            for item in abi:
                if item['type']==abi_type:
                    inputs, sign = gen_signature(item)
                    if sign in all_abis:
                        continue
                    all_abis[sign] = item
    return list(all_abis.values())

def extract_abi(contract_address: str, data: dict, to_file, abi_type: str ='event'):
    hex_abi_map = {}
    for item in data:
        if item['type'] == abi_type:
            event_name = item['name']
            
            input_types, signature = gen_signature(item)

            if signature in hex_abi_map:
                hex_abi_map[signature]['contracts'].append(contract_address)
            else:
                hex_abi_map[signature] = {
                    'event_name': event_name,
                    'input_types': input_types,
                    'contracts':[contract_address]
                }

    save_abi_map(to_file, hex_abi_map)

def gen_signature(abi_item):
    input_types = []

    for input in abi_item['inputs']:
        input_types.append(input['type'])
    
    event_name = abi_item['name']
    signature = f"{event_name}({','.join(input_types)})"
    event_hash = w3.keccak(text=signature).hex()

    return input_types, event_hash

def save_abi_map(filename, data):
    json_text = json.dumps(data)
    with open(filename, 'a') as f:
        f.write(json_text+'\n')

def load_abi_sign_map():
    with open(config['paths']['hex_abi_map'], 'r') as file:
        return json.load(file)

def gen_abi_sign_map():
    to_file = config['paths']['temp_abi_map']
    abi_path = Path(config['paths']['ABI'])
    for file in abi_path.rglob('*.abi'):
        filename = file.name
        with open(file, 'r') as f:
            abi = json.load(f, strict=False)
            if not is_valid_abi(abi):
                abi = json.loads(abi)
            extract_abi(filename, abi, to_file=to_file)
    
    abi_list = {}

    with open(to_file, 'r') as f:
        for line in f.readlines():
            abi_list.update(json.loads(line))

    final_file_json = Path(to_file).with_suffix('.json')

    if not final_file_json.exists():
        final_file_json.touch()
    else:
        final_file_json.unlink()
        final_file_json.touch()

    with open(final_file_json, 'w') as f:
        json.dump(abi_list, f)

def list_all_events():
    event_names = []
    abi_map_path = Path(config['paths']['hex_abi_map'])
    with abi_map_path.open('r') as f:
        abi_map = json.load(f)
    
    for v in abi_map.values():
        event_names.append(v['event_name'])

    return event_names

if __name__ == '__main__':
    # step 1
    # download_contract_abi()
    # step 2
    # gen_abi_sign_map()
    # test: list all event names
    print(list_all_events())