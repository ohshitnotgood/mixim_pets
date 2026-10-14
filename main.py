from Simulation import Simulation
import time
from multiprocessing import Pool
from util import generate_weights
import configparser


def load_and_parse_config(n_mix_per_layer=None, config_path="ConfigFile.ini"):
    """Return Simulation keyword arguments, optionally overriding the network width."""
    config = configparser.ConfigParser()
    with open(config_path) as config_file:
        config.read_file(config_file)

    topology_vars = config["TOPOLOGY"]
    topology = topology_vars["type"]
    fully_connected = topology_vars.getboolean("fully_connected")
    routing = topology_vars["routing"]
    mix_type = config["MIXING"]["mix_type"]

    # Clients
    n_clients = int(config["DEFAULT"]["n_clients"])
    lambda_c = float(config["DEFAULT"]["lambda_c"])

    # For Stratified Topology
    n_layer = int(config["TOPOLOGY"]["n_layers"])
    if n_mix_per_layer is None:
        n_mix_per_layer = topology_vars.getint("l_mixes_per_layer")

    mu = (float(config["TOPOLOGY"]["E2E"]) - (n_layer + 1) * 0.05) / n_layer

    # Threat Model
    corrupt_mixes = config["THREATMODEL"].getint("corrupt_mixes")
    balanced_corruption = config["THREATMODEL"].getboolean("balanced_corruption")
    
    # Propagation delays
    type = config["PROPAGATION"]["type"]
    
    # Dummies
    dummies_vars = config["DUMMIES"]
    client_dummies = dummies_vars.getboolean("client_dummies")
    rate_client_dummies = float(dummies_vars["rate_client_dummies"])
    link_dummies = dummies_vars.getboolean("link_based_dummies")
    multiple_hops_dummies = dummies_vars.getboolean("multiple_hop_dummies")
    rate_mix_dummies = float(dummies_vars["rate_mix_dummies"])

    routing_type = config["NODES_SELETION"]["routing_weights"]
    if routing_type == "uniform":
        weights = generate_weights(n_layer, n_mix_per_layer)
    elif routing_type == "biased":
        weights = []
        w_mix_l1 = [
            0.4,
            0.6 / 9,
            0.6 / 9,
            0.6 / 9,
            0.6 / 9,
            0.6 / 9,
            0.6 / 9,
            0.6 / 9,
            0.6 / 9,
            0.6 / 9,
        ]
        weights.append(w_mix_l1)
        weights.append(w_mix_l1)
        weights.append(w_mix_l1)
    else:
        weights = []
        print("error typing routing type. Please check ConfigFile.ini")
    return dict(
        mix_type=mix_type,
        sim_duration=20,
        rate_client=1 / lambda_c,
        mu=mu,
        logging=False,
        topology=topology,
        fully_connected=fully_connected,
        n_clients=n_clients,
        printing=True,
        routing=routing,
        n_layers=n_layer,
        n_mixes_per_layer=n_mix_per_layer,
        corrupt=corrupt_mixes,
        propagation=type,
        unifrom_corruption=balanced_corruption,
        probability_dist_mixes=weights,
        client_dummies=client_dummies,
        rate_client_dummies=rate_client_dummies,
        link_based_dummies=link_dummies,
        multiple_hops_dummies=multiple_hops_dummies,
        rate_mix_dummies=rate_mix_dummies,
        network_template=None,
    )

def main(simulation_kwargs):
    """Run one simulation using the parsed Simulation keyword arguments."""
    simulation = Simulation(**simulation_kwargs)

    now = time.time()
    entropy, entropy_mean, entropy_median, entropy_q25 = simulation.run()
    if simulation.printing:
        print("Simulation runtime: {}".format(time.time() - now))

    return [entropy, entropy_mean, entropy_median, entropy_q25]


if __name__ == "__main__":
    param = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    configurations = [load_and_parse_config(width) for width in param]
    with Pool(processes=10, maxtasksperchild=1) as pool:
        result = pool.map(main, configurations, chunksize=1)
    table_entropy = []
    for item in result:
        table_entropy.append(item[1])
    width = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    print("Width", width)
    print("Mean Entropy", table_entropy)
