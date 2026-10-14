from PoissonMix import PoissonMix


import random


class Network:
    all_mixes = []
    network_dict = {}  # 1:[list of mixes in layer 1], 2:[list of mixes in layer 2], ...

    def __init__(
        self,
        mix_type,
        num_layers,
        nbr_mixes_layers,
        corrupt,
        unifrom_corruption,
        simulation,
        topology,
        fully_connected,
        probability_dist_mixes,
        link_based_dummies,
        multiple_hop_dummies,
        rate_mix_dummies,
        network_template,
        number_targets,
    ):

        self.simulation = simulation
        self.num_layers = num_layers
        self.mix_type = mix_type
        self.mixes_per_layer = nbr_mixes_layers
        self.corrupt = corrupt
        self.unifrom_corruption = unifrom_corruption
        self.env = simulation.env
        self.topology = topology
        self.fully_connected = fully_connected
        self.link_based_dummies = link_based_dummies
        self.multiple_hop_dummies = multiple_hop_dummies
        self.rate_mix_dummies = rate_mix_dummies
        self.probability_dist_mixes = probability_dist_mixes
        self.network_template = network_template
        self.number_targets = number_targets
        self.list_cascades = {}
        self.n_cascades = 6
        self.create_network()

    def create_network(self):
        mixnb = 1
        self.all_mixes = set()
        if self.topology == "stratified":
            nbr_corruption = 0
            for layer in range(1, self.num_layers + 1):
                c = 0
                self.network_dict[layer] = []
                for _ in range(self.mixes_per_layer):
                    if self.unifrom_corruption:
                        if c < self.corrupt / self.simulation.n_layers:
                            var_corrupt = True
                            c += 1
                        else:
                            var_corrupt = False
                    else:
                        if nbr_corruption < self.corrupt:
                            var_corrupt = random.choice([True, False])
                            if var_corrupt:
                                nbr_corruption += 1
                        else:
                            var_corrupt = False
                    mix = self.get_mixnode(
                        self.mix_type,
                        mixnb,
                        layer,
                        self.number_targets,
                        var_corrupt,
                        self.probability_dist_mixes[layer - 1][_],
                    )
                    self.all_mixes.add(mix)
                    self.network_dict[layer] += [mix]
                    mixnb += 1

            for mix in self.all_mixes:
                if self.fully_connected:
                    if (
                        mix.layer + 1 in self.network_dict
                    ):  # last mix doesn't need neighbors
                        mix.neighbors = self.network_dict[mix.layer + 1]
                    if mix.layer == self.simulation.n_layers:
                        mix.neighbors = self.network_dict[1]
                else:
                    pass

    def get_mixnode(self, mix_type, id, position, number_targets, corrupt, weight_mix):
        if mix_type == "poisson":
            return PoissonMix(
                id,
                self.simulation,
                position,
                self.link_based_dummies,
                self.multiple_hop_dummies,
                self.rate_mix_dummies,
                number_targets,
                corrupt,
                weight_mix,
            )
