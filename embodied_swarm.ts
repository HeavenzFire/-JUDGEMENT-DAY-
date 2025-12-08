import * as fs from 'fs';

// --- EMBODIED SWARM CONSTANTS ---
const NUM_BOTS = 50;
const WORLD_SIZE = 1000; // 1000x1000 unit world
const BOT_RADIUS = 15;
const OBJECT_RADIUS = 50;
const RESONANCE_RANGE = 100; // Bots can resonate within this distance
const COUPLING_STRENGTH = 0.1;
const MAX_FORCE = 5.0;
const DT = 0.016; // ~60 FPS

// --- BOT AGENT ---
interface Bot {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  phase: number; // Resonance phase
  frequency: number; // Natural frequency
  target_x: number; // Where this bot wants to go
  target_y: number;
  energy: number; // 0-1, affects performance
}

// --- HEAVY OBJECT ---
interface HeavyObject {
  x: number;
  y: number;
  vx: number;
  vy: number;
  mass: number;
  radius: number;
}

// --- RESONANCE PHYSICS (Adapted from Toroidal Manifold) ---
class ResonanceEngine {
  private bots: Bot[] = [];
  private object: HeavyObject;

  constructor() {
    this.initialize_bots();
    this.initialize_object();
  }

  private initialize_bots() {
    for (let i = 0; i < NUM_BOTS; i++) {
      this.bots.push({
        id: i,
        x: Math.random() * WORLD_SIZE,
        y: Math.random() * WORLD_SIZE,
        vx: 0,
        vy: 0,
        phase: Math.random() * 2 * Math.PI,
        frequency: 1.0 + (Math.random() - 0.5) * 0.2, // Slight variation
        target_x: WORLD_SIZE / 2, // All bots target center initially
        target_y: WORLD_SIZE / 2,
        energy: 0.8 + Math.random() * 0.4
      });
    }
  }

  private initialize_object() {
    this.object = {
      x: WORLD_SIZE / 2,
      y: WORLD_SIZE / 2,
      vx: 0,
      vy: 0,
      mass: 1000, // Very heavy
      radius: OBJECT_RADIUS
    };
  }

  // Calculate resonance coupling between two bots
  private get_resonance_coupling(bot1: Bot, bot2: Bot): number {
    const dx = bot1.x - bot2.x;
    const dy = bot1.y - bot2.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > RESONANCE_RANGE) return 0;

    // Phase difference affects coupling strength
    const phase_diff = Math.abs(bot1.phase - bot2.phase);
    const phase_factor = Math.cos(phase_diff); // Max when in phase

    // Distance attenuation
    const distance_factor = 1 - (distance / RESONANCE_RANGE);

    return COUPLING_STRENGTH * phase_factor * distance_factor * bot1.energy * bot2.energy;
  }

  // Update bot positions and phases
  public update_bots() {
    // Update phases first
    this.bots.forEach(bot => {
      bot.phase += bot.frequency * DT;
      bot.phase %= 2 * Math.PI;
    });

    // Calculate consensus movement via resonance
    this.bots.forEach(bot => {
      let force_x = 0;
      let force_y = 0;
      let phase_influence = 0;

      // Interact with nearby bots
      this.bots.forEach(other => {
        if (bot.id === other.id) return;

        const coupling = this.get_resonance_coupling(bot, other);
        if (coupling === 0) return;

        // Consensus: Move toward average position of coupled bots
        const dx = other.x - bot.x;
        const dy = other.y - bot.y;

        force_x += coupling * dx * 0.01; // Small attraction
        force_y += coupling * dy * 0.01;

        // Phase synchronization (Kuramoto-like)
        phase_influence += coupling * Math.sin(other.phase - bot.phase);
      });

      // Update phase
      bot.phase += phase_influence * DT;

      // Add target attraction (bots want to move toward object)
      const obj_dx = this.object.x - bot.x;
      const obj_dy = this.object.y - bot.y;
      const obj_dist = Math.sqrt(obj_dx * obj_dx + obj_dy * obj_dy);

      if (obj_dist > 0) {
        force_x += (obj_dx / obj_dist) * 0.5; // Attraction to object
        force_y += (obj_dy / obj_dist) * 0.5;
      }

      // Collision avoidance with other bots
      this.bots.forEach(other => {
        if (bot.id === other.id) return;

        const dx = bot.x - other.x;
        const dy = bot.y - other.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const min_dist = BOT_RADIUS * 2;

        if (dist < min_dist && dist > 0) {
          const repel_force = (min_dist - dist) / min_dist;
          force_x += (dx / dist) * repel_force * 2;
          force_y += (dy / dist) * repel_force * 2;
        }
      });

      // Apply forces (with energy limitation)
      const force_magnitude = Math.sqrt(force_x * force_x + force_y * force_y);
      if (force_magnitude > MAX_FORCE) {
        force_x = (force_x / force_magnitude) * MAX_FORCE;
        force_y = (force_y / force_magnitude) * MAX_FORCE;
      }

      bot.vx += force_x * DT * bot.energy;
      bot.vy += force_y * DT * bot.energy;

      // Damping
      bot.vx *= 0.95;
      bot.vy *= 0.95;

      // Update position
      bot.x += bot.vx * DT;
      bot.y += bot.vy * DT;

      // World boundaries
      bot.x = Math.max(BOT_RADIUS, Math.min(WORLD_SIZE - BOT_RADIUS, bot.x));
      bot.y = Math.max(BOT_RADIUS, Math.min(WORLD_SIZE - BOT_RADIUS, bot.y));
    });
  }

  // Update heavy object based on bot interactions
  public update_object() {
    let total_force_x = 0;
    let total_force_y = 0;
    let interacting_bots = 0;

    this.bots.forEach(bot => {
      const dx = bot.x - this.object.x;
      const dy = bot.y - this.object.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      // Only bots close enough can push the object
      if (dist < OBJECT_RADIUS + BOT_RADIUS + 20) {
        // Force proportional to bot's velocity toward object
        const vel_toward_obj = (bot.vx * dx + bot.vy * dy) / dist;
        if (vel_toward_obj > 0) {
          total_force_x += vel_toward_obj * dx / dist * bot.energy;
          total_force_y += vel_toward_obj * dy / dist * bot.energy;
          interacting_bots++;
        }
      }
    });

    // Apply forces to object
    if (interacting_bots > 0) {
      this.object.vx += (total_force_x / this.object.mass) * DT;
      this.object.vy += (total_force_y / this.object.mass) * DT;
    }

    // Damping
    this.object.vx *= 0.98;
    this.object.vy *= 0.98;

    // Update position
    this.object.x += this.object.vx * DT;
    this.object.y += this.object.vy * DT;

    // World boundaries
    this.object.x = Math.max(OBJECT_RADIUS, Math.min(WORLD_SIZE - OBJECT_RADIUS, this.object.x));
    this.object.y = Math.max(OBJECT_RADIUS, Math.min(WORLD_SIZE - OBJECT_RADIUS, this.object.y));
  }

  // Calculate swarm coherence metrics
  public get_metrics() {
    // Average phase coherence
    let sum_cos = 0;
    let sum_sin = 0;

    this.bots.forEach(bot => {
      sum_cos += Math.cos(bot.phase);
      sum_sin += Math.sin(bot.phase);
    });

    const avg_cos = sum_cos / NUM_BOTS;
    const avg_sin = sum_sin / NUM_BOTS;
    const coherence = Math.sqrt(avg_cos * avg_cos + avg_sin * avg_sin);

    // Object movement efficiency
    const obj_speed = Math.sqrt(this.object.vx * this.object.vx + this.object.vy * this.object.vy);

    return {
      coherence: coherence,
      object_speed: obj_speed,
      object_position: { x: this.object.x, y: this.object.y },
      bot_positions: this.bots.map(bot => ({ x: bot.x, y: bot.y, phase: bot.phase }))
    };
  }

  public run_simulation(steps: number) {
    console.log(`[EMBODIED SWARM] Starting simulation with ${NUM_BOTS} bots...`);

    const results = [];

    for (let i = 0; i < steps; i++) {
      this.update_bots();
      this.update_object();

      if (i % 10 === 0) {
        const metrics = this.get_metrics();
        results.push(metrics);
        console.log(`Step ${i}: Coherence = ${metrics.coherence.toFixed(4)}, Object Speed = ${metrics.object_speed.toFixed(4)}`);
      }
    }

    // Save final state
    const final_state = {
      timestamp: Date.now(),
      final_metrics: this.get_metrics(),
      simulation_steps: steps
    };

    fs.writeFileSync('embodied_swarm_results.json', JSON.stringify(final_state, null, 2));
    console.log("[✓] Swarm simulation complete. Results saved to embodied_swarm_results.json");

    return results;
  }

  public get_state() {
    return {
      bots: this.bots,
      object: this.object
    };
  }
}

// --- MAIN EXECUTION ---
if (require.main === module) {
  const swarm = new ResonanceEngine();
  swarm.run_simulation(300); // 5 seconds at 60 FPS
}