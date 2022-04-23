import os
import pandas as pd
import requests
import shared
from Utils.eth_utils import obtain_hash_event, connect_to_web3
shared.init()
import json
from hexbytes import HexBytes
from web3.datastructures import AttributeDict

def get_response(pool, from_block):
    endpoint = "https://api.polygonscan.com/api?module=logs" \
               "&action=getLogs" \
               f"&fromBlock={from_block}" \
               f"&toBlock={shared.BLOCKSTUDY}" \
               f"&address={pool}" \
               f"&topic0={sync_hash}" \
               f"&apikey={apikey}"

    return json.loads(requests.get(endpoint).text)['result']

def clean_response(response):
    receipts = []
    for event in response:
        receipts.append(AttributeDict({
            'blockNumber': int(event['blockNumber'], 16),
            'contractAddress': event['address'],
            'topics': [HexBytes(topic) for topic in event['topics']],
            'transactionHash': HexBytes(event['transactionHash']),
            'data': event['data'],
            'logIndex': 0,
            'transactionIndex': event['transactionIndex'],
            'address': event['address'],
            'blockHash': HexBytes(event['transactionHash'])
        }))

    log_dict = {'logs': receipts}
    return contract.events.Swap().processReceipt(log_dict)


sync_hash = obtain_hash_event('Swap(address,uint256,uint256,uint256,uint256,address)')
_, web3 = connect_to_web3()
apikey = "P6Z71M2VBHAHHBFMM91YT5YWENGJYTJT81"
tokens_and_pools = pd.read_csv("../data/QUICKSWAP/polygon_pools.csv", index_col='pair')
pools = tokens_and_pools.index.tolist()

contract = web3.eth.contract(shared.EXCHANGES['quickswap'], abi=shared.ABI_POOL)
done_pools = [pool.split(".csv")[0] for pool in os.listdir("../data/QUICKSWAP/swaps")]

for i, pool in enumerate(pools):
    if pool in done_pools:
        continue
    response = [0] * 1000

    print(pool, i, len(pools))
    timestamps, block_numbers, amount0In, amount0Out, amount1In, amount1Out, from_, to = [], [], [], [], [], [], [], []
    from_block, first_timestamp, current_timestamp = 0, 0, 0
    cont = 0

    while len(response) >= 1000 and current_timestamp - first_timestamp < shared.WEEK:
        response = get_response(pool, from_block)
        if len(response) == 0:
            continue
        decoded_logs = clean_response(response)
        for k, log in enumerate(decoded_logs):
            block_numbers.append(log['blockNumber'])
            amount0In.append(log['args']["amount0In"])
            amount0Out.append(log['args']["amount0Out"])
            amount1In.append(log['args']["amount1In"])
            amount1Out.append(log['args']["amount1Out"])
            from_.append(log['args']["sender"])
            to.append(log['args']["to"])
            timestamps.append(int(response[k]["timeStamp"], 16))
        from_block = int(response[-1]['blockNumber'], 16) + 1
        current_timestamp = int(response[-1]['timeStamp'], 16)

    pd.DataFrame({'block_number': block_numbers, 'amount0In': amount0In, 'amount0Out': amount0Out,'amount1In': amount1In,
                  'amount1Out': amount1Out, 'timestamps': timestamps, 'from_': from_, 'to': to}
                 ).to_csv(f"../data/QUICKSWAP/swaps/{pool}.csv", index=False)

