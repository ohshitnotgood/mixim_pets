from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from Client import Client
    from PoissonMix import PoissonMix


MessageType = Literal["real", "dummy", "client_dummy"]


class Message:
    def __init__(
        self,
        id: int,
        message_type: MessageType,
        sender: Client | PoissonMix,
        route: list[Client | PoissonMix | None],
        delays: list[float],
        pr_target: list[float],
        target_bool: bool,
    ) -> None:
        """
        Comment author: Praanto Samadder
        
        Initialize a message and its routing and target-tracking state.

        Args:
            id: Sender-local sequence number. Combined with ``sender.id`` to
                form the message identifier ``<sender_id>_<sequence_number>``.
            message_type: Packet type, such as ``"real"``, ``"dummy"``, or
                ``"client_dummy"``.
            sender: Client or mix originating the message.
            route: Sender, intermediate mixes, and destination client in
                traversal order. Unselected hops may be ``None``.
            delays: Delays indexed by route position, including entries for
                the sender and destination.
            pr_target: Probability of this message being each tracked target,
                with one entry per target.
            target_bool: Whether the adversary selected this message as a target.

        The route, delays, and probabilities are stored without copying.
        Departure time starts at zero, and the next-hop index starts at one,
        pointing to the first mix in a client-generated route.
        """
        self.id = "%d_%d" % (sender.id, id)
        self.type: MessageType = message_type
        self.sender = sender
        self.route = route
        self.delays = delays
        self.pr_target = pr_target
        self.target_bool = target_bool
        self.time_left = 0
        self.next_hop_index = 1
