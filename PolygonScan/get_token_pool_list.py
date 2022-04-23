import time
import pandas as pd
import requests
import shared
shared.init()
import json
from web3 import Web3, HTTPProvider
from hexbytes import HexBytes
from web3.datastructures import AttributeDict


def connect_to_web3():
    """
    Connect to Web3 server.
    Args:
    Returns:
      res: Boolean indicating that connection was succeed or not.
      web3: Web3 Object
    """
    web3 = Web3(HTTPProvider('https://polygon-mainnet.infura.io/v3/d6243bb783b44485ad6636b6c3411377'))
    res = web3.isConnected()
    return res, web3

from_block = 0
response = [0] * 1000
block_number = []
_, web3 = connect_to_web3()
contract = web3.eth.contract(shared.UNISWAP_V3_FACTORY, abi=shared.ABI_FACTORY)

topic = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118"

tokens0, tokens1, pools, block_numbers, timestamps, fees = [], [], [], [], [],[]
cont = 1000
while len(response) >= 1000:
    try:
        print("Pools trobades", cont)
        cont += 1000
        apikey = "P6Z71M2VBHAHHBFMM91YT5YWENGJYTJT81"
        endpoint = "https://api.polygonscan.com/api?module=logs" \
                   "&action=getLogs" \
                   f"&fromBlock={from_block}" \
                   f"&toBlock={shared.BLOCKSTUDY}" \
                   f"&address={shared.UNISWAP_V3_FACTORY}" \
                   f"&topic0={topic}" \
                   f"&apikey={apikey}"

        response = json.loads(requests.get(endpoint).text)['result']
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
        decoded_logs = contract.events.PoolCreated().processReceipt(log_dict)
        for k, log in enumerate(decoded_logs):
            block_numbers.append(log['blockNumber'])
            tokens0.append(log['args']["token0"])
            tokens1.append(log['args']['token1'])
            pools.append(log['args']['pool'])
            fees.append(log['args']['fee'])
            timestamps.append(int(response[k]['timeStamp'], 16))
        from_block = int(response[-1]['blockNumber'], 16) + 1

    except Exception as err:
        print(err)
        time.sleep(2)

pd.DataFrame({'pair': pools, 'token0': tokens0, 'token1': tokens1, 'fees': fees, 'block_number': block_numbers, 'timestamp': timestamps}).to_csv(
    "../data/polygon_pools.csv", index=False)
