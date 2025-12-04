const WebSocket = require('ws');
const crypto = require('crypto');

// Syntropic Mesh Node
// Implements distributed, self-healing network of meaning with proof-based consensus and multi-modal AI agents

class SyntropicNode {
    constructor(port, peers = []) {
        this.port = port;
        this.peers = peers; // Array of peer URLs
        this.facts = new Map(); // Local fact store: factId -> {fact, proof, scope, timestamp}
        this.agents = []; // Array of AI agents
        this.server = null;
        this.connections = new Map(); // ws -> peerUrl
    }

    start() {
        this.server = new WebSocket.Server({ port: this.port });
        console.log(`[*] Node started on port ${this.port}`);

        this.server.on('connection', (ws, req) => {
            const peerUrl = req.url;
            this.connections.set(ws, peerUrl);
            console.log(`[*] Connected to peer: ${peerUrl}`);

            ws.on('message', (data) => this.handleMessage(ws, data));
            ws.on('close', () => this.connections.delete(ws));
        });

        // Connect to known peers
        this.peers.forEach(peer => this.connectToPeer(peer));
    }

    connectToPeer(peerUrl) {
        const ws = new WebSocket(peerUrl);
        ws.on('open', () => {
            this.connections.set(ws, peerUrl);
            console.log(`[*] Connected to peer: ${peerUrl}`);
        });
        ws.on('message', (data) => this.handleMessage(ws, data));
        ws.on('close', () => this.connections.delete(ws));
    }

    handleMessage(ws, data) {
        try {
            const message = JSON.parse(data);
            switch (message.type) {
                case 'FACT_PROPAGATION':
                    this.receiveFact(message.fact);
                    break;
                case 'CONSENSUS_VOTE':
                    this.handleVote(message);
                    break;
                default:
                    console.log(`[!] Unknown message type: ${message.type}`);
            }
        } catch (e) {
            console.error(`[!] Error handling message: ${e}`);
        }
    }

    // Placeholder for fact model - to be implemented
    publishFact(fact, scope) {
        // Implement fact creation with proof
        console.log(`[*] Publishing fact: ${JSON.stringify(fact)}`);
    }

    receiveFact(fact) {
        // Implement fact validation and merging
        console.log(`[*] Received fact: ${JSON.stringify(fact)}`);
    }

    // Placeholder for consensus
    handleVote(vote) {
        console.log(`[*] Handling vote: ${JSON.stringify(vote)}`);
    }

    // Placeholder for AI agents
    addAgent(agent) {
        this.agents.push(agent);
        console.log(`[*] Added agent: ${agent.name}`);
    }

    stop() {
        if (this.server) {
            this.server.close();
        }
        this.connections.forEach(ws => ws.close());
    }
}

// Export for use
module.exports = SyntropicNode;

// Example usage
if (require.main === module) {
    const node = new SyntropicNode(8080, ['ws://localhost:8081']);
    node.start();

    // Graceful shutdown
    process.on('SIGINT', () => {
        node.stop();
        process.exit();
    });
}