from Message import Message
from random import choice, sample
from numpy.random import exponential
import random

global id_dummies


class PoissonMix:
    def __init__(
        self,
        mix_id,
        simulation,
        position,
        link_based_dummies,
        multiple_hop_dummies,
        rate_mix_dummies,
        n_targets,
        corrupt,
        pr_mix,
    ):
        """Initialize a mix with exponential delays and optional dummy traffic."""
        self.n_targets = n_targets
        self.id = mix_id
        self.env = simulation.env
        self.simulation = simulation
        self.layer = position
        self.corrupt = corrupt
        self.p_mix = [0.0 for _ in range(n_targets)]
        self.pool = []  # Pool
        self.neighbors = set()
        self.link_based_dummies = link_based_dummies
        self.multiple_hop_dummies = multiple_hop_dummies
        self.rate_mix_dummies = rate_mix_dummies
        self.pr_mix = pr_mix
        self.pool_dummies = []
        if (
            (self.link_based_dummies or self.multiple_hop_dummies)
            and (self.rate_mix_dummies is not None)
            and (not self.corrupt)
            and self.layer != self.simulation.n_layers
        ):
            self.env.process(self.send_dummies())

    def receive_message(self, msg: Message):
        if (
            not self.simulation.start_attack
        ):  # if a mix reaches a poolsize of 5 percent higher than the average,
            # the GPA can monitor the network and choose a target message
            clients = self.simulation.n_clients
            lambda_client = self.simulation.rate_client
            average = (clients * lambda_client * self.simulation.mu) * self.pr_mix
            var1 = len(self.pool) >= average
            if self.simulation.topology == "stratified":
                if var1 and self.layer == 1:
                    self.env.process(self.simulation.set_stable_mix(self.id - 1))
                # if all(self.simulation.stable_mix_l1):
                # for i in range(len(self.simulation.stable_mix_l1)):
                # self.simulation.set_stable_mix(i)
            elif self.simulation.topology == "XRD":
                if var1:
                    self.env.process(self.simulation.set_stable_chain(self.n_chain))
                if all(self.simulation.stable_chains):
                    for i in range(len(self.simulation.stable_chains)):
                        self.simulation.set_stable_chain(i)
        for i in range(0, self.n_targets):
            self.p_mix[i] += msg.pr_target[i]
        if msg.target_bool and self.simulation.printing:
            print(
                f"Target message arrived at mix {self.id} at time {self.env.now} and Number of messages inside "
                f"the pool {len(self.pool)}"
            )
        msg.next_hop_index += 1
        if msg.route[msg.next_hop_index] == None:
            msg.route[msg.next_hop_index] = random.choice(self.neighbors)
        if msg.type == "real":
            self.pool.append(msg)
            self.env.process(self.send_msg(msg))
        elif msg.type == "dummy":
            if self.link_based_dummies:
                self.drop_dummies(msg)
            elif self.multiple_hop_dummies:
                if self.layer == self.simulation.n_layers:
                    self.drop_dummies(msg)
                elif self.layer != self.simulation.n_layers:
                    self.pool.append(msg)
                    self.env.process(self.send_msg(msg))

    def send_msg(self, msg):
        yield self.env.timeout(msg.delays[self.layer])
        self.update_probabilities(msg, len(self.pool))
        next_hop_index = msg.route[msg.next_hop_index]
        self.pool.remove(msg)
        self.env.process(self.simulation.attacker.relay(msg, next_hop_index))

    def update_probabilities(self, msg, pool_size):
        if not self.corrupt:
            for j in range(0, self.n_targets):
                msg.pr_target[j] = self.p_mix[j] / pool_size
                self.p_mix[j] = self.p_mix[j] - msg.pr_target[j]

    def drop_dummies(self, msg):
        if self.layer == self.simulation.n_layers:
            self.simulation.log.dummies_dropped_end_link(msg, self.id)

    def send_dummies(self):
        dummy_id = 1
        while True:
            new_message = self.create_dummies(dummy_id)
            new_message.creator = self.id
            self.pool.append(new_message)
            yield self.env.timeout(exponential(self.rate_mix_dummies))
            dummy_id += 1
            self.env.process(self.send_msg(new_message))

    def create_dummies(self, dummy_id):
        """
        Comment author: Praanto Samadder

        Create a dummy message originating at this mix without sending it.

        Args:
            dummy_id: Sequence number used with this mix's ID to form the
                message identifier ``d_<mix_id>_<dummy_id>``.

        Returns:
            Message: A non-target message with type ``"dummy"``, this mix as
            its sender, and the generated route, delays, and probabilities.
        """
        network_dict = self.simulation.network.network_dict
        route = [None]
        delays = [0]
        for layer in range(1, self.simulation.n_layers + 1):
            if self.layer > layer:
                route.append(None)
                delays.append(0)
            elif self.layer == layer:
                route.append(self)
                delays.append(exponential(self.simulation.mu))
            else:
                route.append(choice(network_dict[layer]))
                delays.append(exponential(self.simulation.mu))
        delays += [0]
        newstop = sample(self.simulation.clients_set, k=1)[0]
        route += [newstop]
        pr_target = []
        for _ in range(0, self.n_targets):
            pr_target.append(float(0.0))
        new_dummy = Message(dummy_id, "dummy", self, route, delays, pr_target, False)

        new_dummy.next_hop_index = self.layer + 1
        new_dummy.id = f"d_{self.id}_{dummy_id}"
        return new_dummy

    def __str__(self):
        return f"( id: {self.id}, corrupt: {self.corrupt} )"

    def __repr__(self):
        return self.__str__()
