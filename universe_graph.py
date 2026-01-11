import numpy as np
from scipy.sparse import csr_matrix
import networkx as nx


class UniverseGraph:
    """
    Cosmic hypergraph representation for entropic flow modeling.

    Nodes represent cosmic entities (merged_source, cosmic_sink, archonic nodes, hybrid nodes, void nodes).
    Edges represent entropic transfer pathways with capacities, flows, and quantum coherence factors.
    """

    def __init__(self, nodes=None, edges=None):
        """
        Initialize the universe graph.

        Args:
            nodes: List of node identifiers
            edges: List of (u, v, capacity, coherence) tuples
        """
        self.G = nx.DiGraph()

        # Initialize nodes with quantum states and entropy tracking
        if nodes:
            for node in nodes:
                self.G.add_node(node,
                              quantum_states=[np.array([1.0])],  # Default normalized state
                              entropy=1.0,  # Initial entropy
                              negentropy_reservoir=0.0)

        # Initialize edges with flow network properties
        if edges:
            for u, v, capacity, coherence in edges:
                self.G.add_edge(u, v,
                              capacity=capacity,
                              flow=0.0,
                              coherence=coherence,
                              entropy_production=0.1)  # Default entropy production rate

    def add_node(self, node_id, quantum_state=None, initial_entropy=1.0):
        """Add a node to the graph."""
        if quantum_state is None:
            quantum_state = np.array([1.0])

        # Normalize quantum state
        quantum_state = quantum_state / np.sqrt(np.sum(np.abs(quantum_state)**2))

        self.G.add_node(node_id,
                      quantum_states=[quantum_state],
                      entropy=initial_entropy,
                      negentropy_reservoir=0.0)

    def add_edge(self, u, v, capacity, coherence=1.0, entropy_production=0.1):
        """Add a directed edge with flow network properties."""
        self.G.add_edge(u, v,
                      capacity=capacity,
                      flow=0.0,
                      coherence=coherence,
                      entropy_production=entropy_production)

    def get_nodes(self):
        """Get all node identifiers."""
        return list(self.G.nodes())

    def get_neighbors(self, node):
        """Get neighbors of a node."""
        return list(self.G.neighbors(node))

    def capacity(self, u, v):
        """Get residual capacity between nodes."""
        if self.G.has_edge(u, v):
            return self.G[u][v]['capacity'] - self.G[u][v]['flow']
        return 0.0

    def flow(self, u, v):
        """Get current flow between nodes."""
        if self.G.has_edge(u, v):
            return self.G[u][v]['flow']
        return 0.0

    def update_flow(self, u, v, new_flow):
        """Update flow between nodes."""
        if self.G.has_edge(u, v):
            self.G[u][v]['flow'] = new_flow

    def phi(self, u, v):
        """Get quantum coherence factor between nodes."""
        if self.G.has_edge(u, v):
            return self.G[u][v]['coherence']
        return 0.0

    def entropy_production(self, u, v=None):
        """Get entropy production rate for edge or node."""
        if v is not None:
            if self.G.has_edge(u, v):
                return self.G[u][v]['entropy_production']
            return 0.0
        else:
            # Node entropy production (sum of outgoing edges)
            total_production = 0.0
            for neighbor in self.get_neighbors(u):
                total_production += self.entropy_production(u, neighbor)
            return total_production

    def update_entropy(self, node, delta_entropy):
        """Update entropy of a node."""
        if node in self.G.nodes:
            self.G.nodes[node]['entropy'] = max(0.0, self.G.nodes[node]['entropy'] + delta_entropy)

    def get_entropy(self, node):
        """Get current entropy of a node."""
        if node in self.G.nodes:
            return self.G.nodes[node]['entropy']
        return 0.0

    def get_quantum_state(self, node):
        """Get quantum state of a node."""
        if node in self.G.nodes:
            return self.G.nodes[node]['quantum_states'][0]
        return np.array([1.0])

    def set_quantum_state(self, node, state):
        """Set quantum state of a node."""
        if node in self.G.nodes:
            # Normalize state
            state = state / np.sqrt(np.sum(np.abs(state)**2))
            self.G.nodes[node]['quantum_states'] = [state]

    def calculate_total_entropy(self):
        """Calculate total entropy across all nodes."""
        total_entropy = 0.0
        for node in self.get_nodes():
            total_entropy += self.get_entropy(node)
        return total_entropy

    def calculate_boltzmann_entropy(self, node):
        """Calculate Boltzmann entropy from quantum state probabilities."""
        state = self.get_quantum_state(node)
        probabilities = np.abs(state)**2
        probabilities = probabilities / np.sum(probabilities)

        # Avoid log(0)
        probabilities = np.where(probabilities > 1e-10, probabilities, 1e-10)

        entropy = -np.sum(probabilities * np.log(probabilities))
        return entropy

    def apply_resonance(self, node, frequency, phase=0.0):
        """Apply resonant frequency to a node."""
        current_state = self.get_quantum_state(node)

        # Apply phase shift based on frequency and phase
        resonance_factor = np.exp(1j * (frequency * 2 * np.pi + phase))

        # Modify state with resonance
        new_state = current_state * resonance_factor

        # Normalize
        new_state = new_state / np.sqrt(np.sum(np.abs(new_state)**2))

        self.set_quantum_state(node, new_state)

        # Return resonance amplitude (magnitude of change)
        amplitude = np.abs(resonance_factor)
        return amplitude

    def dissolve_node(self, node):
        """Dissolve a node (remove from graph, redistribute connections)."""
        if node not in self.G.nodes:
            return

        # Get neighbors before removal
        predecessors = list(self.G.predecessors(node))
        successors = list(self.G.successors(node))

        # For each predecessor-successor pair, create direct connection
        for pred in predecessors:
            for succ in successors:
                if not self.G.has_edge(pred, succ):
                    # Combine capacities and coherence
                    pred_capacity = self.capacity(pred, node)
                    succ_capacity = self.capacity(node, succ)
                    combined_capacity = min(pred_capacity, succ_capacity)

                    pred_coherence = self.phi(pred, node)
                    succ_coherence = self.phi(node, succ)
                    combined_coherence = (pred_coherence + succ_coherence) / 2

                    self.add_edge(pred, succ, combined_capacity, combined_coherence)

        # Remove the node
        self.G.remove_node(node)

    def __str__(self):
        """String representation of the graph."""
        return f"UniverseGraph with {len(self.G.nodes)} nodes and {len(self.G.edges)} edges"