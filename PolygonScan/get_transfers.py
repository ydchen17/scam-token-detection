import os
import pandas as pd
import requests
import shared
from Utils.eth_utils import obtain_hash_event, connect_to_web3
shared.init()
import json
from hexbytes import HexBytes
from web3.datastructures import AttributeDict

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

huge_tokens = ['0x0000000000000000000000000000000000001010', '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
               '0x692597b009d13C4049a947CAB2239b7d6517875F', '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
               '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', '0x3BA4c387f786bFEE076A58914F5Bd38d668B42c3',
               '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619']

contract = web3.eth.contract(shared.WMATIC, abi=shared.ABI)
done_transfers = [transfer.split(".csv")[0] for transfer in os.listdir("../data/transfers")]
pools = pd.read_csv("../data/polygon_pools.csv")
pools = pools.loc[(pools.token0 == shared.WMATIC) | (pools.token1 == shared.WMATIC)]
day = 60 * 60 * 24
tokens = set(pools['token0'].tolist() + pools['token1'].tolist())

for i, token in enumerate(tokens):
    print(token, i, len(tokens))
    if token in done_transfers or token in huge_tokens:
        continue

    first_timestamp = pools.loc[(pools.token0 == token) | (pools.token1 == token)]['timestamp'].iloc[0]
    response = [0] * 1000
    timestamps, block_numbers, from_, to_, value_ = [], [], [], [], []

    from_block, current_timestamp = 0, 0
    cont = 0

    while len(response) >= 1000 and current_timestamp - first_timestamp < day:
        cont += 1
        response = get_response(token, from_block)
        if len(response) == 0:
            break

        decoded_logs = clean_response(response)
        if len(decoded_logs) == 0:
            break

        for k, log in enumerate(decoded_logs):
            block_numbers.append(log['blockNumber'])
            from_.append(log['args']["from"])
            to_.append(log['args']["to"])
            value_.append(log['args']["value"])
            timestamps.append(int(response[k]["timeStamp"], 16))

        if cont == 1:
            first_timestamp = timestamps[0]
        from_block = int(response[-1]['blockNumber'], 16) + 1
        current_timestamp = int(response[-1]['timeStamp'], 16)

    pd.DataFrame({'block_number': block_numbers, 'from': from_, 'to': to_, 'value': value_, 'timestamps': timestamps}).to_csv(
        f"../data/transfers/{token}.csv", index=False)

