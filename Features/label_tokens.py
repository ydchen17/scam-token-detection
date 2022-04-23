import pandas as pd
import shared
shared.init()

pools = pd.read_csv("../data/polygon_pools.csv")
pools = pools.loc[(pools.token0 == shared.WMATIC) | (pools.token1 == shared.WMATIC)]
day = 60 * 60 * 24
tokens = set(pools['token0'].tolist() + pools['token1'].tolist())
malicious_tokens = []
for token in tokens:
    pair = pools.loc[(pools.token0 == token) | (pools.token1 == token)]['pair'].iloc[0]
    mints = pd.read_csv(f"../data/mints/{pair}.csv")
    burns = pd.read_csv(f"../data/Burns/{pair}.csv")
    swaps = pd.read_csv(f"../data/swaps/{pair}.csv")

    if len(mints) > 0:
        last_mint_timestamp = mints['timestamps'].iloc[-1]
    else:
        last_mint_timestamp = 0
    if len(burns) > 0:
        last_burns_timestamp = burns['timestamps'].iloc[-1]
    else:
        last_burns_timestamp = 0
    if len(swaps) > 0:
        last_swaps_timestamp = swaps['timestamps'].iloc[-1]
    else:
        last_swaps_timestamp = 0

    if last_swaps_timestamp > last_burns_timestamp or last_mint_timestamp > last_burns_timestamp:
        continue
    elif shared.timestamp_study - last_burns_timestamp > 60 * 60 * 7 * 24:
        malicious_tokens.append(token)

pd.DataFrame(malicious_tokens).to_csv("../PolygonScan/malicious_tokens.csv", index=False)

