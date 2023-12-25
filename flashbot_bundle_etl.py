import pandas as pd
from pathlib import Path
import json
from typing import List
from datetime import datetime, date
import logging

bundle_path = '/Users/kevin/PolyU-COMP-MScIT/5933-Project/datasets/flashbot'
parsed_block_path = f'{bundle_path}/blocks/'
parsed_tx_path = f'{bundle_path}/transactions/'
logger = logger = logging.getLogger(__file__)


def read_parse_flashbot(filename: str = None):
    files = Path(bundle_path).glob('*.json')
    file_index = 0
    total_blocks = 0
    total_tx = 0
    blocks_file = Path(parsed_block_path) / 'blocks.csv'
    if not blocks_file.exists():
        blocks_file.touch()

    for i, file in enumerate(files):
        if (filename is not None):
            if (file.name == filename):
                file_index = i
            else:
                continue

        if i >= file_index:
            with open(file, 'r', encoding='utf8') as json_file:
                data = json.load(json_file)
                no_blocks = parse_block(data, blocks_file)
                print(f'Total number of blocks: {no_blocks}')
     

def parse_block(data: dict, block_file: Path):
    blocks = data['blocks']
    counter = 0
    block_list = []
    tx_list = []

    with block_file.open('a', encoding='utf-8') as file:
        for b in blocks:
            line = '{},{},{}\n'.format(b['block_number'], b['gas_used'], b['gas_price'])
            file.write(line)
            counter+=1
    return counter

def parse_tx(block: dict):
    tx_list = []
    transactions = block['transactions']
    for t in transactions:
        tx = {
            'transaction_hash': t['transaction_hash'], 
            'block_no': t['block_number'], 
            'tx_index': t['tx_index'],
            'bundle_type': t['bundle_type'], 
            'bundle_index': t['bundle_index'], 
            'eoa_address': t['eoa_address'], 
            'to_address': t['to_address'], 
            'gas_used': t['gas_used'],
            'gas_price': t['gas_price'], 
            'coinbase_transfer': t['coinbase_transfer'],
            'eth_sent_to_fee_recipient': t['eth_sent_to_fee_recipient'], 
            'total_miner_reward': t['total_miner_reward'],
            'fee_recipient_eth_diff': t['fee_recipient_eth_diff'],
        }
        tx_list.append(tx)
    
    return tx_list
        

def save_blocks(block_list: List[dict]):
    block_df = pd.DataFrame(block_list)
    ts = datetime.now().timestamp()
    block_df.to_csv(f'{parsed_block_path}{ts}_blocks.csv', index=False)

def save_tx(tx_list: List[dict]):
    tx_df = pd.DataFrame(tx_list)
    ts = datetime.now().timestamp()
    tx_df.to_csv(f'{parsed_tx_path}{ts}_tx.csv', index=False)

def main():
    read_parse_flashbot()


if __name__ == '__main__': 
    main()
