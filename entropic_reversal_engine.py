import numpy as np
from universe_graph import UniverseGraph


class EntropicReversalEngine:
    """
    Quantum Push-Relabel Engine for Entropic Reversal.

    Extends push-relabel max flow to operate on entropy potentials rather than
    simple capacities, using quantum superposition for relabeling operations.
    """

    def __init__(self, universe_graph, merged_source_frequency):
        """
        Initialize the entropic reversal engine.

        Args:
            universe_graph: UniverseGraph instance representing the cosmic flow network
            merged_source_frequency: Oscillation rate of the merged source (Hz)
        """
        self.G = universe_graph
        self.omega = merged_source_frequency
        self.neg_entropy_reservoir = float('inf')  # Infinite reservoir from merged source
        self.entropy_potentials = self._initialize_potentials()

        # Track convergence metrics
        self.iteration_count = 0
        self.total_entropy_destroyed = 0.0

    def _initialize_potentials(self):
        """Initialize entropy potentials for all nodes."""
        potentials = {}

        for node in self.G.get_nodes():
            if node == 'merged_source':
                potentials[node] = float('inf')
            elif node == 'cosmic_sink':
                potentials[node] = 0.0
            else:
                # Potential inversely related to local entropy
                local_entropy = self.G.calculate_boltzmann_entropy(node)
                potentials[node] = 1.0 / (local_entropy + 1e-10)  # Avoid division by zero

        return potentials

    def _calculate_local_entropy(self, node):
        """Calculate local entropy for a node."""
        return self.G.calculate_boltzmann_entropy(node)

    def entropic_push(self, u, v):
        """
        Push negentropy from high-potential to low-potential nodes.

        Returns the amount of negentropy pushed.
        """
        # Check potential gradient (must flow downhill)
        if self.entropy_potentials[u] <= self.entropy_potentials[v]:
            return 0.0

        # Calculate maximum pushable negentropy
        residual_capacity = self.G.capacity(u, v)
        coherence_factor = self.G.phi(u, v)

        # Entropy destruction rate limited by merged source frequency
        potential_gradient = self.entropy_potentials[u] - self.entropy_potentials[v]
        max_push = min(
            residual_capacity,
            self.neg_entropy_reservoir * coherence_factor,
            self.omega * potential_gradient
        )

        if max_push <= 0:
            return 0.0

        # Perform the push
        old_flow = self.G.flow(u, v)
        self.G.update_flow(u, v, old_flow + max_push)

        # Entropy reduction in target node (negentropy injection)
        current_entropy = self.G.get_entropy(v)
        entropy_reduction = -max_push * np.exp(-current_entropy)
        self.G.update_entropy(v, entropy_reduction)

        # Update potentials (slight adjustments)
        self.entropy_potentials[v] += max_push * 0.01  # Small increase
        self.entropy_potentials[u] -= max_push * 0.005  # Small decrease

        # Track total entropy destroyed
        self.total_entropy_destroyed += abs(entropy_reduction)

        return max_push

    def quantum_relabel(self, u):
        """
        Elevate node's potential using quantum superposition of neighboring states.
        """
        if u == 'merged_source' or u == 'cosmic_sink':
            return

        # Collect quantum states from neighboring nodes
        neighbor_states = []
        neighbor_weights = []

        for v in self.G.get_neighbors(u):
            neighbor_states.append(self.G.get_quantum_state(v))
            # Weight by coherence and inverse distance in potential
            coherence = self.G.phi(u, v)
            potential_diff = abs(self.entropy_potentials[u] - self.entropy_potentials[v])
            weight = coherence / (potential_diff + 1e-10)
            neighbor_weights.append(weight)

        if not neighbor_states:
            return

        # Create weighted superposition
        total_weight = sum(neighbor_weights)
        if total_weight == 0:
            return

        superposition = np.zeros_like(neighbor_states[0])
        for state, weight in zip(neighbor_states, neighbor_weights):
            superposition += state * (weight / total_weight) * np.exp(1j * self.omega * 0.1)

        # Normalize the superposition
        superposition = superposition / np.sqrt(np.sum(np.abs(superposition)**2))

        # Update node's quantum state
        self.G.set_quantum_state(u, superposition)

        # Calculate new potential from superposition's entropy
        new_entropy = self._calculate_local_entropy(u)
        self.entropy_potentials[u] = 1.0 / (new_entropy + 1e-10)

    def _has_excess_entropy(self, node):
        """Check if node has excess entropy that needs to be discharged."""
        if node == 'merged_source' or node == 'cosmic_sink':
            return False

        # Node has excess if its entropy is above average
        node_entropy = self.G.get_entropy(node)
        total_entropy = self.G.calculate_total_entropy()
        avg_entropy = total_entropy / len(self.G.get_nodes())

        return node_entropy > avg_entropy

    def _calculate_total_entropy(self):
        """Calculate total entropy across the universe."""
        return self.G.calculate_total_entropy()

    def execute_entropic_reversal(self, max_iterations=1000, convergence_threshold=1e-10):
        """
        Execute the main entropic reversal algorithm.

        Returns:
            success: Boolean indicating if entropy was reduced to near zero
            total_entropy_destroyed: Total negentropy injected
        """
        self.iteration_count = 0
        self.total_entropy_destroyed = 0.0

        for iteration in range(max_iterations):
            self.iteration_count = iteration + 1

            # Phase 1: Push negentropy through all possible edges
            total_pushed = 0.0
            for u in self.G.get_nodes():
                for v in self.G.get_neighbors(u):
                    pushed = self.entropic_push(u, v)
                    total_pushed += pushed

            # Phase 2: Relabel nodes with excess entropy
            for u in self.G.get_nodes():
                if self._has_excess_entropy(u):
                    self.quantum_relabel(u)

            # Phase 3: Check termination condition
            total_universe_entropy = self._calculate_total_entropy()

            if total_universe_entropy <= convergence_threshold:
                print(f"ENTROPY REVERSED AFTER {self.iteration_count} ITERATIONS")
                return True, self.total_entropy_destroyed

            # Phase 4: Periodic frequency boost for convergence acceleration
            if iteration % 100 == 0 and iteration > 0:
                self.omega *= 1.1  # 10% frequency increase
                print(f"Frequency boosted to {self.omega:.2e} Hz at iteration {iteration}")

            # Early termination if no progress
            if total_pushed < convergence_threshold:
                print(f"Convergence stalled at iteration {iteration}")
                break

        return False, self.total_entropy_destroyed

    def get_status(self):
        """Get current status of the reversal process."""
        return {
            'iterations': self.iteration_count,
            'total_entropy_destroyed': self.total_entropy_destroyed,
            'current_total_entropy': self._calculate_total_entropy(),
            'merged_source_frequency': self.omega,
            'entropy_potentials': self.entropy_potentials.copy()
        }