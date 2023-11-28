import json
from utils import is_json
from config import *
import requests
from pathlib import Path

def load_contact_addresses():
    address_map_path = Path('./contract_addresses.json')
    
    with address_map_path.open('r') as f:
        protocol_address_map = json.load(f)
    
    return protocol_address_map    

def download_contract_abi() -> dict:
    ETHERSCAN_API_KEY = get_key('Etherscan', 'API_KEY')
    root_abi_path = Path(config['paths']['ABI'])
    protocol_address_map = load_contact_addresses()
    for protocol in protocol_address_map:
        protocol_path = root_abi_path / f'{protocol}'
        if not protocol_path.exists():
            protocol_path.mkdir()
        for (address, label) in protocol_address_map[protocol].items():
            abi_path = protocol_path / f'{label}.abi'
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
    
def save_abi(abi:dict, save_path:Path):
        
    if save_path.exists():
        return
    
    with open(save_path, 'w') as f:
        json.dump(abi, f)

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
                    all_abis.append(item)

    return all_abis           

if __name__== '__main__':
    download_contract_abi()                    