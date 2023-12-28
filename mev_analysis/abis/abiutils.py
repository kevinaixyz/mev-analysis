from web3 import Web3
import json
import requests
from mev_analysis.config import *
from mev_analysis.utils.utils import is_valid_abi, is_json
from sqlalchemy import orm, text
from typing import List, Dict, Optional
from mev_analysis.models.function_signatures import FunctionSignaturesModel
import logging

logger = logging.getLogger(__name__)

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))


# Return contract addresses for the protocols
def load_contact_addresses():
    address_map_path = Path('../../contract_addresses.json')

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
                # save_abi(abi['result'], abi_path)
                logger.info(f'{label} ({address}) is downloaded.')
            else:
                logger.error(f'Invalid ABI for contract: {address}')


def query_function_signature(
        function_signature: str,
        bytes_signature: str,
        db_session: orm.session) -> Optional[FunctionSignaturesModel]:
    result = db_session.get(
        FunctionSignaturesModel,
        {"function_signature": function_signature, "bytes_signature": bytes_signature}
    )

    return result


# Save the abi to file
def write_abi_to_db(
        abis: List[dict],
        db_session: orm.session,
        abi_type: str = 'function'
) -> None:
    for abi in abis:
        if abi['type'] != abi_type:
            continue

        function_name = abi['name']
        text_signature, bytes_signature = gen_signatures(abi)

        db_session.add(
            FunctionSignaturesModel(
                function_name=function_name,
                function_signature=text_signature,
                bytes_signature=bytes_signature,
            )
        )

    db_session.commit()


# Load all abis and return a list
def load_abis_from_file(protocol: str = None, abi_type: str = 'function') -> list:
    abis = []
    if protocol is not None:
        paths = (Path(config['paths']['ABI']) / config['chain'] / f'{protocol}').glob('*.json')
    else:
        paths = (Path(config['paths']['ABI']) / config['chain']).rglob('*.abi')

    for path in paths:
        with path.open('r') as f:
            abi = json.load(f)
            if type(abi) != list:
                abi = json.loads(abi)
            for item in abi:
                if item['type'] == abi_type:
                    abi.append(item)
    return abis


def load_signatures_from_file(path: Path, db_session: orm.session) -> None:
    with path.open('r') as f:
        signatures = json.load(f)

    bytes_signature = '0x8aaea6dd'
    keys_list = list(signatures.keys())
    begin_index = keys_list.index(bytes_signature) + 1
    for i in range(begin_index, len(keys_list)):
        bytes_signature = keys_list[i]
        text_signature = signatures[bytes_signature]
    # for bytes_signature, text_signature in signatures.items():
        if not query_function_signature(text_signature, bytes_signature, db_session):
            function_name = text_signature[: text_signature.index('(')]
            db_session.add(
                FunctionSignaturesModel(
                    function_name=function_name,
                    function_signature=text_signature,
                    bytes_signature=bytes_signature,
                )
            )
            db_session.commit()


def extract_abi(contract_address: str, data: dict, to_file, abi_type: str = 'function'):
    hex_abi_map = {}
    for item in data:
        if item['type'] == abi_type:
            event_name = item['name']

            input_types, signature = gen_signatures(item)

            if signature in hex_abi_map:
                hex_abi_map[signature]['contracts'].append(contract_address)
            else:
                hex_abi_map[signature] = {
                    'event_name': event_name,
                    'input_types': input_types,
                    'contracts': [contract_address]
                }

    save_abi_map(to_file, hex_abi_map)


def gen_signatures(abi_item):
    input_types = []

    for input in abi_item['inputs']:
        input_types.append(input['type'])

    event_name = abi_item['name']
    text_signature = f"{event_name}({','.join(input_types)})"
    hash_ = w3.keccak(text=text_signature).hex()
    byte_signature = hash_[:10]

    return text_signature, byte_signature


def save_abi_map(filename, data):
    json_text = json.dumps(data)
    with open(filename, 'a') as f:
        f.write(json_text + '\n')


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


from mev_analysis.db import get_inspect_session

if __name__ == '__main__':
    path = Path(__file__).parent / 'function_signatures.json'
    db_session = get_inspect_session()
    load_signatures_from_file(path, db_session)
