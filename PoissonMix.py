from Mix import Mix
from numpy.random import exponential
import random

global id_dummies


class PoissonMix(Mix):
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
        super().__init__(mix_id, simulation, position, n_targets, corrupt)
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

    def receive_message(self, msg):
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
        if msg.type == "Real":
            self.pool.append(msg)
            self.env.process(self.send_msg(msg))
        elif msg.type == "Dummy":
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
