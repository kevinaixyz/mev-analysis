import pandas as pd
from pathlib import Path
import json
from typing import List
from datetime import datetime, date
import logging

raw_file_path = './flashbot/'
parsed_block_path = './flashbot/blocks/'
parsed_tx_path = './flashbot/transactions/'
logger = None

def init():
    logging.basicConfig(
        level=logging.INFO,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(levelname)s - %(message)s',  # Set the log message format
        filename='app.log',  # Specify the log file name
        filemode='w'  # Set the file mode (w for write, a for append)
    )

    # Define a logger
    logger = logging.getLogger('etl')
    return logger

def read_parse_flashbot(parse_block: bool, parse_tx: bool, filename: str = None):
    files = Path(raw_file_path).glob('*.json')
    file_index = 0
    total_blocks = 0
    total_tx = 0

    for i, file in enumerate(files):
        if (filename is not None):
            if (file.name == filename):
                file_index = i
            else:
                continue

        if i >= file_index:
            with open(file, 'r', encoding ='utf8') as json_file:
                data = json.load(json_file)
                no_blocks, no_tx = parse_data(data, parse_tx)
                total_blocks += no_blocks
                total_tx += no_tx
                logger.info(f'File {file.name} is parsed.')
                logger.info(f'Total blocks: {total_blocks}')
                logger.info(f'Total tx: {total_tx}')

def parse_data(data: dict, handle_tx: bool):
    
    no_blocks, no_tx = parse_block(data, handle_tx)
    return no_blocks, no_tx
     

def parse_block(data: dict, handle_tx: bool):
    blocks = data['blocks']
    counter = 10000
    block_list = []
    tx_list = []
    for b in blocks:
        block = {
            'block_no': b['block_number'], 
            'miner_reward': b['miner_reward'], 
            'fee_recipient_eth_diff': b['fee_recipient_eth_diff'], 
            'miner': b['miner'], 
            'fee_recipient': b['fee_recipient'], 
            'coinbase_transfers': b['coinbase_transfers'],
            'eth_sent_to_fee_recipient': b['eth_sent_to_fee_recipient'], 
            'gas_used': b['gas_used'],
            'gas_price': b['gas_price'],
            'effective_priority_fee': b['effective_priority_fee']
        }
        block_list.append(block)

        if handle_tx:
            tx_list += parse_tx(b)

    save_blocks(block_list)
    save_tx(tx_list)

    return len(block_list), len(tx_list)

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
    read_parse_flashbot(True, True)


if __name__ == '__main__': 
    logger = init()
    main()
