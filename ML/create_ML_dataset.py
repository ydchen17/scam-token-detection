import warnings
warnings.filterwarnings(f"ignore")

import pandas as pd
from tqdm import tqdm

import shared
shared.init()
from Features.compute_curve import get_curve
from Features.compute_transfer_features import get_transfer_features

hours_since_creation = 24

pools = pd.read_csv(f"../data/polygon_pools.csv")
pools = pools.loc[(pools.token0 == shared.WMATIC) | (pools.token1 == shared.WMATIC)]

tokens = pd.read_csv(f"../data/labeled_tokens.csv")
time_elapsed = 60*60*hours_since_creation

total_features = {}
total_transfers = pd.DataFrame(columns=['token', 'address', 'price_rev'])

for token_info in tqdm(tokens.values):
    token_address, label = token_info[0], token_info[1]
    pool = pools.loc[(pools.token0 == token_address) | (pools.token1 == token_address)].values[0]
    pool_address, token0, token1, block_number, pool_creation_timestamp = pool[0], pool[1], pool[2], pool[4], pool[5]
    total_features[pool_address] = {'token_address': token_address, 'label': label}

    position = 1 if token1 == shared.WMATIC else 0
    token = token0 if position == 1 else token1
    limit_timestamp = pool_creation_timestamp + time_elapsed

    transfers = pd.read_csv(f"../data/transfers/{token}.csv")
    mints = pd.read_csv(f"../data/mints/{pool_address}.csv")
    burns = pd.read_csv(f"../data/Burns/{pool_address}.csv")
    swaps = pd.read_csv(f"../data/swaps/{pool_address}.csv")

    transfers = transfers.loc[transfers.timestamps < limit_timestamp]
    mints = mints.loc[mints.timestamps < limit_timestamp]
    burns = burns.loc[burns.timestamps < limit_timestamp]
    swaps = swaps.loc[swaps.timestamps < limit_timestamp]

    total_features[pool_address].update({'num_mints': len(mints), 'num_burns': len(burns), 'num_swaps': len(swaps)})

    if 0 in [len(transfers)]:
        continue

    # Pool features
    total_supply = + sum(transfers.loc[(transfers['from'] == shared.ETH_ADDRESS)]['value'].astype(float))\
                   - sum(transfers.loc[(transfers['to'] == shared.ETH_ADDRESS)]['value'].astype(float))
    if total_supply == 0:
        continue

    # Transfer features
    tx_curve = get_curve(transfers.values, type_='tx')
    total_features[pool_address].update(tx_curve)
    transfer_features = get_transfer_features(transfers, total_supply)
    total_features[pool_address].update(transfer_features)
    total_features[pool_address].update({'difference_token_pool': + pool_creation_timestamp
                                                                  - transfers.iloc[0]['timestamps']})

pd.DataFrame(total_features).transpose().to_csv(f"features{hours_since_creation}h.csv", index_label="pool_address")
