import sys
import pandas as pd
import json
from collections import defaultdict
import os
import shared
shared.init()


def distribution_metric(balances, total_supply):
    g1 = sum([(value/total_supply)**2 for holder,value in balances.items() if holder not in [shared.ETH_ADDRESS,
                                                                                             shared.DEAD_ADDRESS]])
    return g1

def get_curve(transfers, type_):
    balances = defaultdict(lambda: 0)
    from_, to_, values, timestamp = 1, 2, 3, 4
    total_supply, total_supply_ans = 0, 0
    i = 0
    while i < len(transfers):
        balances[transfers[i][from_]] -= float(transfers[i][values])
        balances[transfers[i][to_]] += float(transfers[i][values])
        if transfers[i][from_] == shared.ETH_ADDRESS:
            total_supply += float(transfers[i][values])
            balances[transfers[i][from_]] = 0
        if transfers[i][to_] == shared.ETH_ADDRESS:
            total_supply -= float(transfers[i][values])
            balances[transfers[i][to_]] = 0
        i += 1
    if total_supply != 0:
        curve = distribution_metric(balances, total_supply)
    else:
        curve = 1

    return {f'{type_}_curve': curve}



