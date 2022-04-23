import os

import pandas as pd
import requests
import json
from hexbytes import HexBytes
from web3.datastructures import AttributeDict

import shared
shared.init()
from Utils.eth_utils import obtain_hash_event, connect_to_web3


def get_response(token, from_block):
    endpoint = "https://api.polygonscan.com/api?module=logs" \
               "&action=getLogs" \
               f"&fromBlock={from_block}" \
               f"&toBlock={shared.BLOCKSTUDY}" \
               f"&address={token}" \
               f"&topic0={transfer_hash}" \
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
    return contract.events.Transfer().processReceipt(log_dict)

transfer_hash = obtain_hash_event('Transfer(address,address,uint256)')

_, web3 = connect_to_web3()
apikey = "P6Z71M2VBHAHHBFMM91YT5YWENGJYTJT81"

contract = web3.eth.contract(shared.WMATIC, abi=shared.ABI)
done_transfers = [transfer.split(".csv")[0] for transfer in os.listdir("../data/SUSHISWAP/lp_transfers")]
pools = pd.read_csv("../data/SUSHISWAP/polygon_pools.csv")
tokens = set(pools['token0'].tolist() + pools['token1'].tolist())


for i, pool_address in enumerate(pools['pair']):
    print(pool_address, i, len(pools['pair']))
    if pool_address in done_transfers:
        continue

    response = [0] * 1000
    timestamps, block_numbers, from_, to_, value_ = [], [], [], [], []
    day = 60 * 60 * 24
    from_block, first_timestamp, current_timestamp = 0, 0, 0
    cont = 0

    while len(response) >= 1000 and current_timestamp - first_timestamp < day and cont < 10:
        cont += 1
        response = get_response(pool_address, from_block)
        if len(response) == 0:
            break
        decoded_logs = clean_response(response)
        for k, log in enumerate(decoded_logs):
            block_numbers.append(log['blockNumber'])
            from_.append(log['args']["from"])
            to_.append(log['args']["to"])
            value_.append(log['args']["value"])
            timestamps.append(int(response[k]["timeStamp"], 16))
        from_block = int(response[-1]['blockNumber'], 16) + 1
        current_timestamp = int(response[-1]['timeStamp'], 16)
        if cont == 1:
            first_timestamp = timestamps[0]

    pd.DataFrame({'block_number': block_numbers, 'from': from_, 'to': to_, 'value': value_, 'timestamps': timestamps}).to_csv(
        f"../data/SUSHISWAP/lp_transfers/{pool_address}.csv", index=False)

