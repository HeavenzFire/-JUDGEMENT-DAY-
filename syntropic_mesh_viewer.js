// Syntropic Mesh Viewer Module
// Web interface for monitoring and controlling the multi-node semantic mesh

import { BRYER_RESURRECTION, createTonePlayer } from './syntropic_supernova.js';

// Mock mesh data (in real implementation, this would connect to backend)
let meshData = {
  nodes: [],
  facts: [],
  coherence: 0.85,
  negotiationLog: []
};

let meshRunning = false;
let tonePlayer = null;

// Initialize the viewer
export function initMeshViewer() {
  // Get DOM elements
  const nodesEl = document.getElementById('nodes');
  const factsEl = document.getElementById('facts');
  const coherenceEl = document.getElementById('coherence');
  const freqEl = document.getElementById('freq');
  const vowEl = document.getElementById('vow');
  const actionEl = document.getElementById('action');
  const meshStatusEl = document.getElementById('meshStatus');
  const jsonEl = document.getElementById('json');
  const negotiationLogEl = document.getElementById('negotiationLog');
  const factInputEl = document.getElementById('factInput');

  const startMeshBtn = document.getElementById('startMesh');
  const stopMeshBtn = document.getElementById('stopMesh');
  const publishFactBtn = document.getElementById('publishFact');
  const negotiateBtn = document.getElementById('negotiate');
  const playBtn = document.getElementById('play');
  const stopBtn = document.getElementById('stop');
  const copyBtn = document.getElementById('copy');

  // Initialize BRYER data
  freqEl.textContent = `Frequency: ${BRYER_RESURRECTION.frequency} Hz`;
  vowEl.textContent = `Vow: ${BRYER_RESURRECTION.vow}`;
  actionEl.textContent = `Action: ${BRYER_RESURRECTION.action}`;
  jsonEl.textContent = JSON.stringify(BRYER_RESURRECTION, null, 2);

  // Initialize mesh data
  updateDisplay();

  // Event listeners
  startMeshBtn.addEventListener('click', startMesh);
  stopMeshBtn.addEventListener('click', stopMesh);
  publishFactBtn.addEventListener('click', publishFact);
  negotiateBtn.addEventListener('click', triggerNegotiation);

  playBtn.addEventListener('click', async () => {
    try {
      tonePlayer = createTonePlayer(BRYER_RESURRECTION.frequency);
      await tonePlayer.start();
      playBtn.disabled = true;
      stopBtn.disabled = false;
    } catch (err) {
      console.error(err);
      alert('Unable to start audio: ' + err.message);
    }
  });

  stopBtn.addEventListener('click', () => {
    if (tonePlayer) {
      tonePlayer.stop();
      tonePlayer = null;
    }
    playBtn.disabled = false;
    stopBtn.disabled = true;
  });

  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(BRYER_RESURRECTION, null, 2));
      copyBtn.textContent = 'Copied ✓';
      setTimeout(() => copyBtn.textContent = 'Copy JSON', 1200);
    } catch (err) {
      alert('Copy failed: ' + err.message);
    }
  });

  // Functions
  function updateDisplay() {
    nodesEl.textContent = `Nodes: ${meshData.nodes.length}`;
    factsEl.textContent = `Facts: ${meshData.facts.length}`;
    coherenceEl.textContent = `Coherence: ${(meshData.coherence * 100).toFixed(1)}%`;

    meshStatusEl.textContent = JSON.stringify({
      running: meshRunning,
      nodes: meshData.nodes.length,
      facts: meshData.facts.length,
      coherence: meshData.coherence,
      lastUpdate: new Date().toISOString()
    }, null, 2);

    negotiationLogEl.textContent = meshData.negotiationLog.slice(-10).join('\n');
  }

  function startMesh() {
    meshRunning = true;
    // Mock starting mesh
    meshData.nodes = [
      { id: 'node_1', host: 'localhost', port: 5000, status: 'active' },
      { id: 'node_2', host: 'localhost', port: 5001, status: 'active' },
      { id: 'node_3', host: 'localhost', port: 5002, status: 'active' }
    ];
    meshData.negotiationLog.push(`[${new Date().toLocaleTimeString()}] Mesh started with ${meshData.nodes.length} nodes`);
    updateDisplay();
    startMeshBtn.disabled = true;
    stopMeshBtn.disabled = false;
  }

  function stopMesh() {
    meshRunning = false;
    meshData.nodes = [];
    meshData.negotiationLog.push(`[${new Date().toLocaleTimeString()}] Mesh stopped`);
    updateDisplay();
    startMeshBtn.disabled = false;
    stopMeshBtn.disabled = true;
  }

  function publishFact() {
    const factContent = factInputEl.value.trim();
    if (!factContent) {
      alert('Please enter fact content');
      return;
    }

    if (!meshRunning) {
      alert('Mesh is not running');
      return;
    }

    // Mock publishing fact
    const fact = {
      id: `fact_${Date.now()}`,
      content: factContent,
      timestamp: new Date().toISOString(),
      origin: 'web_interface'
    };

    meshData.facts.push(fact);
    meshData.negotiationLog.push(`[${new Date().toLocaleTimeString()}] Published fact: ${factContent}`);
    factInputEl.value = '';
    updateDisplay();
  }

  function triggerNegotiation() {
    if (!meshRunning) {
      alert('Mesh is not running');
      return;
    }

    // Mock negotiation
    const proposals = [
      'New fact: The void is a womb of unspoken names.',
      'Script modification: Align with 779.572416 Hz harmonic',
      'Hold request: Emotional entropy detected'
    ];

    const proposal = proposals[Math.floor(Math.random() * proposals.length)];
    const consensus = Math.random() > 0.3; // 70% consensus rate

    meshData.negotiationLog.push(`[${new Date().toLocaleTimeString()}] Proposal: ${proposal}`);
    meshData.negotiationLog.push(`[${new Date().toLocaleTimeString()}] Consensus: ${consensus ? 'REACHED' : 'FAILED'}`);

    if (consensus) {
      meshData.coherence += 0.05;
      if (meshData.coherence > 1.0) meshData.coherence = 1.0;
    }

    updateDisplay();
  }

  // Real-time updates simulation
  setInterval(() => {
    if (meshRunning) {
      // Simulate real-time mesh activity
      if (Math.random() < 0.2) { // 20% chance per interval
        const autoFacts = [
          'Weather update: Sunny skies ahead',
          'System health: All nodes operational',
          'Coherence pulse: Torsion field active',
          'Negotiation: Consensus reached on new pattern',
          'Alert: Emotional entropy stabilized'
        ];
        const fact = autoFacts[Math.floor(Math.random() * autoFacts.length)];
        meshData.facts.push({
          id: `auto_${Date.now()}`,
          content: fact,
          timestamp: new Date().toISOString(),
          origin: 'mesh_auto'
        });
        meshData.negotiationLog.push(`[${new Date().toLocaleTimeString()}] ${fact}`);
      }

      // Simulate coherence fluctuations
      meshData.coherence += (Math.random() - 0.5) * 0.02; // Small random changes
      meshData.coherence = Math.max(0.5, Math.min(1.0, meshData.coherence)); // Clamp between 0.5 and 1.0

      updateDisplay();
    }
  }, 3000); // Update every 3 seconds
}