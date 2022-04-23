import networkx as nx


def get_transfer_features(hour_transfers, total_supply):
    num_transactions_list = len(hour_transfers)
    n_unique_addresses = len(set(hour_transfers['from'].tolist() + hour_transfers['to'].tolist()))
    avg_transaction_value = sum(hour_transfers['value'].astype(float))/num_transactions_list
    G = nx.Graph()
    for From, To, Value in \
            zip(hour_transfers['from'].to_numpy(), hour_transfers['to'].to_numpy(), hour_transfers['value'].to_numpy()):
        G.add_edge(From, To, weight=Value)

    try:
        avg_cluster_coeff = nx.average_clustering(G)
    except:
        avg_cluster_coeff = 0

    features = {
        'num_transactions': num_transactions_list,
        'n_unique_addresses': n_unique_addresses,
        'avg_cluster_coeff': avg_cluster_coeff,
        'avg_transaction_value': avg_transaction_value/total_supply
    }
    return features

