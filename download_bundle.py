import requests
import json
import pandas as pd
import time

# start block number: 16308190
# end block number: 18541697

def main():
    start_block_no = 16308190
    end_block_no = 18541697

    counter = 5 # seconds

    url = 'https://blocks.flashbots.net/v1/blocks'

    limit = 50

    block_no = 16386429

    while block_no >= start_block_no:
        print(f'block no: {block_no}')
        counter = 0
        params = {
            'before': block_no,
            'limit': limit
        }

        r = requests.get(url, params=params)

        if r.status_code!= 200:
            print(r.status_code)
            if counter < 150:
                time.sleep(counter)
                counter += 5
                continue
            else:
                break
        
        data = r.json()

        large_block_no = data['blocks'][0]['block_number']
        small_block_no = data['blocks'][-1]['block_number']

        with open(f'./flashbot/{small_block_no}-{large_block_no}.json', 'w', encoding ='utf8') as json_file: 
            json.dump(data, json_file)
        
        block_no = small_block_no
        if block_no - start_block_no < limit:
            limit = block_no - start_block_no

        time.sleep(0.5)

if __name__ == '__main__':
    main()