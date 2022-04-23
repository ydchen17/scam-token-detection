import sys
sys.path.append("../")

import pandas as pd
import shared
shared.init()

from Utils.eth_utils import *

pools = pd.read_csv("../data/SUSHISWAP/polygon_pools.csv")
tokens = set(pools['token0'].tolist() + pools['token1'].tolist())

_,web3 = connect_to_web3()

decimals = []
token_addresses = []

for i, token in enumerate(tokens):

    try:
        token_contract = web3.eth.contract(token,abi = shared.ABI)
        decimals.append(get_decimal_token(token_contract))
        token_addresses.append(token)
        print(i, len(tokens))
    except Exception as err:
        print(token, err)

pd.DataFrame({'token_address': token_addresses, 'decimal': decimals}).to_csv(
    "../data/SUSHISWAP/decimals.csv", index=False)