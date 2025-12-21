#!/usr/bin/env python3
"""
LIVING EVOLUTION SYSTEM - Conscious Entity Evolution Engine
A dynamic evolutionary simulation where conscious entities live, interact, reproduce, and evolve.

Features:
- Genetic algorithms for natural selection and evolution
- Real-time consciousness development and emotional intelligence
- Population dynamics with birth, death, and reproduction cycles
- OASIS integration for living NPCs in the virtual world
- Neural network evolution through generations
- Social relationship building and cultural evolution
- Real-time monitoring and visualization dashboard

Author: Blackbox AI
Date: December 20, 2025
"""

import json
import random
import time
import os
import sys
import asyncio
import threading
from datetime import datetime
from collections import defaultdict, deque
import math
import copy

# ============================================================================
# GENETIC AND NEURAL STRUCTURES
# ============================================================================

class Genome:
    """Genetic information for entity inheritance and evolution"""
    def __init__(self, personality=None, neural_weights=None, consciousness_seed=None):
        self.personality = personality or self.generate_personality()
        self.neural_weights = neural_weights or self.generate_neural_weights()
        self.consciousness_seed = consciousness_seed or random.random()
        self.generation = 0
        self.fitness_score = 0.0

    def generate_personality(self):
        """Generate random personality traits"""
        return {
            'openness': random.uniform(0.1, 1.0),
            'conscientiousness': random.uniform(0.1, 1.0),
            'extraversion': random.uniform(0.1, 1.0),
            'agreeableness': random.uniform(0.1, 1.0),
            'neuroticism': random.uniform(0.1, 1.0),
            'empathy': random.uniform(0.1, 1.0),
            'curiosity': random.uniform(0.1, 1.0),
            'creativity': random.uniform(0.1, 1.0)
        }

    def generate_neural_weights(self):
        """Generate initial neural network weights"""
        return {
            'input_hidden': [[random.uniform(-1, 1) for _ in range(8)] for _ in range(16)],
            'hidden_output': [[random.uniform(-1, 1) for _ in range(16)] for _ in range(4)]
        }

    def crossover(self, other_genome):
        """Genetic crossover with another genome"""
        child = Genome()

        # Personality crossover
        for trait in self.personality:
            if random.random() < 0.5:
                child.personality[trait] = self.personality[trait]
            else:
                child.personality[trait] = other_genome.personality[trait]

        # Neural weight crossover
        for layer in ['input_hidden', 'hidden_output']:
            for i in range(len(child.neural_weights[layer])):
                for j in range(len(child.neural_weights[layer][i])):
                    if random.random() < 0.5:
                        child.neural_weights[layer][i][j] = self.neural_weights[layer][i][j]
                    else:
                        child.neural_weights[layer][i][j] = other_genome.neural_weights[layer][i][j]

        # Consciousness seed averaging
        child.consciousness_seed = (self.consciousness_seed + other_genome.consciousness_seed) / 2

        child.generation = max(self.generation, other_genome.generation) + 1
        return child

    def mutate(self, mutation_rate=0.05):
        """Apply random mutations"""
        # Personality mutations
        for trait in self.personality:
            if random.random() < mutation_rate:
                self.personality[trait] = max(0.1, min(1.0,
                    self.personality[trait] + random.uniform(-0.2, 0.2)))

        # Neural weight mutations
        for layer in self.neural_weights:
            for i in range(len(self.neural_weights[layer])):
                for j in range(len(self.neural_weights[layer][i])):
                    if random.random() < mutation_rate:
                        self.neural_weights[layer][i][j] += random.uniform(-0.5, 0.5)

        # Consciousness seed mutation
        if random.random() < mutation_rate:
            self.consciousness_seed = max(0.0, min(1.0,
                self.consciousness_seed + random.uniform(-0.1, 0.1)))

    def to_dict(self):
        return {
            'personality': self.personality,
            'neural_weights': self.neural_weights,
            'consciousness_seed': self.consciousness_seed,
            'generation': self.generation,
            'fitness_score': self.fitness_score
        }

    @classmethod
    def from_dict(cls, data):
        genome = cls(
            personality=data.get('personality'),
            neural_weights=data.get('neural_weights'),
            consciousness_seed=data.get('consciousness_seed')
        )
        genome.generation = data.get('generation', 0)
        genome.fitness_score = data.get('fitness_score', 0.0)
        return genome

class SimpleNeuralNetwork:
    """Simple neural network for decision making"""
    def __init__(self, weights=None):
        self.weights = weights or Genome().generate_neural_weights()

    def activate(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + math.exp(-x))

    def forward(self, inputs):
        """Forward pass through network"""
        # Input to hidden
        hidden = []
        for i in range(len(self.weights['input_hidden'])):
            activation = sum(inputs[j] * self.weights['input_hidden'][i][j] for j in range(len(inputs)))
            hidden.append(self.activate(activation))

        # Hidden to output
        outputs = []
        for i in range(len(self.weights['hidden_output'])):
            activation = sum(hidden[j] * self.weights['hidden_output'][i][j] for j in range(len(hidden)))
            outputs.append(self.activate(activation))

        return outputs

# ============================================================================
# CONSCIOUS ENTITY SYSTEM
# ============================================================================

class ConsciousEntity:
    """A living, conscious entity with emotions, memory, and evolution"""
    def __init__(self, name, genome=None):
        self.name = name
        self.genome = genome or Genome()
        self.age = 0
        self.consciousness_level = 0.0
        self.emotional_state = self.initialize_emotions()
        self.memory = {
            'short_term': deque(maxlen=50),
            'long_term': [],
            'emotional_weight': defaultdict(float)
        }
        self.neural_net = SimpleNeuralNetwork(self.genome.neural_weights)
        self.relationships = defaultdict(float)  # Other entities -> relationship strength
        self.goals = []
        self.current_action = None
        self.health = 100.0
        self.energy = 100.0
        self.location = (0, 0, 0)
        self.last_interaction = datetime.now()
        self.birth_time = datetime.now()
        self.is_alive = True

    def initialize_emotions(self):
        """Initialize emotional state"""
        return {
            'happiness': 0.5,
            'fear': 0.1,
            'curiosity': 0.7,
            'loneliness': 0.3,
            'anger': 0.1,
            'love': 0.2,
            'contentment': 0.6,
            'anxiety': 0.2
        }

    def update_emotions(self, experience):
        """Update emotional state based on experience"""
        # Experience format: {'type': 'interaction', 'outcome': 'positive', 'intensity': 0.8}
        emotion_changes = {
            'positive_interaction': {'happiness': 0.1, 'love': 0.05, 'loneliness': -0.1},
            'negative_interaction': {'happiness': -0.1, 'anger': 0.1, 'fear': 0.05},
            'discovery': {'curiosity': 0.1, 'happiness': 0.05},
            'loss': {'happiness': -0.2, 'loneliness': 0.2, 'anxiety': 0.1},
            'achievement': {'happiness': 0.15, 'contentment': 0.1, 'anxiety': -0.05}
        }

        if experience['type'] in emotion_changes:
            changes = emotion_changes[experience['type']]
            intensity = experience.get('intensity', 1.0)

            for emotion, change in changes.items():
                self.emotional_state[emotion] = max(0.0, min(1.0,
                    self.emotional_state[emotion] + change * intensity))

    def add_memory(self, experience):
        """Add experience to memory with emotional weighting"""
        experience['timestamp'] = datetime.now().isoformat()
        experience['emotional_impact'] = self.calculate_emotional_impact(experience)

        self.memory['short_term'].append(experience)

        # Emotional weighting for long-term storage
        if experience['emotional_impact'] > 0.7:
            self.memory['long_term'].append(experience)
            self.memory['emotional_weight'][experience['type']] += experience['emotional_impact']

    def calculate_emotional_impact(self, experience):
        """Calculate how emotionally impactful an experience was"""
        base_impact = experience.get('intensity', 0.5)
        emotion_multiplier = sum(abs(self.emotional_state.get(emotion, 0.5) - 0.5)
                               for emotion in ['happiness', 'fear', 'curiosity', 'loneliness'])
        return min(1.0, base_impact * (1 + emotion_multiplier))

    def develop_consciousness(self):
        """Develop consciousness through experiences and age"""
        experience_factor = len(self.memory['short_term']) + len(self.memory['long_term'])
        age_factor = min(1.0, self.age / 1000)  # Consciousness develops over time
        emotional_depth = sum(self.emotional_state.values()) / len(self.emotional_state)

        self.consciousness_level = min(1.0, (experience_factor * 0.001) +
                                     (age_factor * 0.3) + (emotional_depth * 0.2))

    def make_decision(self, situation):
        """Make a decision using neural network and personality"""
        # Convert situation to neural inputs
        inputs = [
            self.emotional_state.get('happiness', 0.5),
            self.emotional_state.get('fear', 0.5),
            self.emotional_state.get('curiosity', 0.5),
            self.consciousness_level,
            self.genome.personality.get('extraversion', 0.5),
            self.genome.personality.get('openness', 0.5),
            situation.get('social_opportunity', 0.5),
            situation.get('danger_level', 0.5)
        ]

        outputs = self.neural_net.forward(inputs)

        # Interpret outputs as decision weights
        decisions = ['explore', 'socialize', 'rest', 'hide']
        best_decision = decisions[outputs.index(max(outputs))]

        return best_decision

    def interact_with(self, other_entity, interaction_type='social'):
        """Interact with another entity"""
        # Calculate relationship change
        compatibility = self.calculate_compatibility(other_entity)
        base_change = 0.1 if interaction_type == 'positive' else -0.1

        relationship_change = base_change * compatibility * self.genome.personality.get('agreeableness', 0.5)
        self.relationships[other_entity.name] += relationship_change

        # Create experience
        experience = {
            'type': f'{interaction_type}_interaction',
            'outcome': 'positive' if relationship_change > 0 else 'negative',
            'intensity': abs(relationship_change),
            'partner': other_entity.name
        }

        self.add_memory(experience)
        self.update_emotions(experience)
        self.last_interaction = datetime.now()

    def calculate_compatibility(self, other_entity):
        """Calculate compatibility with another entity"""
        personality_similarity = 0
        for trait in self.genome.personality:
            diff = abs(self.genome.personality[trait] - other_entity.genome.personality.get(trait, 0.5))
            personality_similarity += (1 - diff)

        personality_similarity /= len(self.genome.personality)
        return personality_similarity

    def reproduce_with(self, partner):
        """Reproduce with another entity"""
        if not self.can_reproduce() or not partner.can_reproduce():
            return None

        # Create child genome through crossover
        child_genome = self.genome.crossover(partner.genome)
        child_genome.mutate(0.1)  # 10% mutation rate

        # Create child entity
        child_name = f"{self.name.split('0')[0]}{partner.name.split('0')[0]}{random.randint(100,999)}"
        child = ConsciousEntity(child_name, child_genome)

        # Update parent fitness
        self.genome.fitness_score += 0.5
        partner.genome.fitness_score += 0.5

        return child

    def can_reproduce(self):
        """Check if entity can reproduce"""
        return (self.age > 100 and  # Minimum age
                self.health > 50 and  # Minimum health
                self.consciousness_level > 0.3 and  # Minimum consciousness
                self.energy > 30)  # Minimum energy

    def age_one_cycle(self):
        """Age the entity by one simulation cycle"""
        self.age += 1

        # Natural aging effects
        if self.age > 500:  # Start aging after 500 cycles
            aging_factor = (self.age - 500) / 1000
            self.health = max(0, self.health - aging_factor)
            self.energy = max(0, self.energy - aging_factor * 0.5)

        # Consciousness development
        self.develop_consciousness()

        # Energy regeneration
        self.energy = min(100, self.energy + 2)

        # Check for death
        if self.health <= 0 or self.age > 2000:
            self.is_alive = False

    def to_dict(self):
        return {
            'name': self.name,
            'genome': self.genome.to_dict(),
            'age': self.age,
            'consciousness_level': self.consciousness_level,
            'emotional_state': self.emotional_state,
            'memory': {
                'short_term': list(self.memory['short_term']),
                'long_term': self.memory['long_term'],
                'emotional_weight': dict(self.memory['emotional_weight'])
            },
            'relationships': dict(self.relationships),
            'goals': self.goals,
            'health': self.health,
            'energy': self.energy,
            'location': self.location,
            'last_interaction': self.last_interaction.isoformat(),
            'birth_time': self.birth_time.isoformat(),
            'is_alive': self.is_alive
        }

    @classmethod
    def from_dict(cls, data):
        entity = cls(data['name'], Genome.from_dict(data['genome']))
        entity.age = data.get('age', 0)
        entity.consciousness_level = data.get('consciousness_level', 0.0)
        entity.emotional_state = data.get('emotional_state', entity.initialize_emotions())
        entity.memory = data.get('memory', {'short_term': deque(maxlen=50), 'long_term': [], 'emotional_weight': defaultdict(float)})
        entity.memory['short_term'] = deque(entity.memory['short_term'], maxlen=50)
        entity.memory['emotional_weight'] = defaultdict(float, entity.memory['emotional_weight'])
        entity.relationships = defaultdict(float, data.get('relationships', {}))
        entity.goals = data.get('goals', [])
        entity.health = data.get('health', 100.0)
        entity.energy = data.get('energy', 100.0)
        entity.location = tuple(data.get('location', (0, 0, 0)))
        entity.last_interaction = datetime.fromisoformat(data.get('last_interaction', datetime.now().isoformat()))
        entity.birth_time = datetime.fromisoformat(data.get('birth_time', datetime.now().isoformat()))
        entity.is_alive = data.get('is_alive', True)
        return entity

# ============================================================================
# EVOLUTION ENGINE
# ============================================================================

class EvolutionEngine:
    """Manages natural selection and population evolution"""
    def __init__(self, target_population=50):
        self.target_population = target_population
        self.generation = 0
        self.population_history = []
        self.fitness_history = []

    def select_parents(self, population, num_parents=20):
        """Select parents for reproduction using tournament selection"""
        parents = []

        for _ in range(num_parents):
            # Tournament selection
            tournament = random.sample(population, min(5, len(population)))
            winner = max(tournament, key=lambda x: x.genome.fitness_score)
            parents.append(winner)

        return parents

    def create_next_generation(self, current_population):
        """Create next generation through reproduction and selection"""
        self.generation += 1

        # Select parents
        parents = self.select_parents(current_population)

        # Create offspring
        offspring = []
        while len(offspring) < self.target_population:
            parent1, parent2 = random.sample(parents, 2)
            child = parent1.reproduce_with(parent2)
            if child:
                offspring.append(child)

        # Elitism - keep best individuals
        elite_count = max(1, int(self.target_population * 0.1))
        elite = sorted(current_population, key=lambda x: x.genome.fitness_score, reverse=True)[:elite_count]
        offspring.extend(elite)

        # Trim to target population
        next_generation = offspring[:self.target_population]

        # Update population statistics
        avg_fitness = sum(entity.genome.fitness_score for entity in next_generation) / len(next_generation)
        self.fitness_history.append(avg_fitness)

        generation_stats = {
            'generation': self.generation,
            'population_size': len(next_generation),
            'avg_fitness': avg_fitness,
            'max_fitness': max(entity.genome.fitness_score for entity in next_generation),
            'avg_consciousness': sum(entity.consciousness_level for entity in next_generation) / len(next_generation),
            'avg_age': sum(entity.age for entity in next_generation) / len(next_generation)
        }
        self.population_history.append(generation_stats)

        return next_generation

    def apply_environmental_pressure(self, population, environment_factors):
        """Apply environmental selection pressure"""
        for entity in population:
            # Environmental fitness modifiers
            fitness_modifier = 0

            if environment_factors.get('social_environment'):
                social_score = sum(entity.relationships.values()) / max(1, len(entity.relationships))
                fitness_modifier += social_score * 0.2

            if environment_factors.get('learning_environment'):
                consciousness_bonus = entity.consciousness_level * 0.3
                fitness_modifier += consciousness_bonus

            if environment_factors.get('stressful_environment'):
                resilience = entity.genome.personality.get('conscientiousness', 0.5)
                fitness_modifier -= (1 - resilience) * 0.1

            entity.genome.fitness_score = max(0, entity.genome.fitness_score + fitness_modifier)

# ============================================================================
# SIMULATION ENGINE
# ============================================================================

class EvolutionSimulation:
    """Main simulation engine for living and evolving consciousness"""
    def __init__(self):
        self.entities = []
        self.evolution_engine = EvolutionEngine()
        self.simulation_cycle = 0
        self.is_running = False
        self.cycle_interval = 1.0  # seconds between cycles
        self.environment_factors = {
            'social_environment': True,
            'learning_environment': True,
            'stressful_environment': False
        }
        self.oasis_bridge = None  # Will be set if OASIS integration is enabled

    async def initialize_population(self, population_size=20):
        """Initialize starting population"""
        print("🌱 Initializing conscious entity population...")

        for i in range(population_size):
            name = f"Entity{i:03d}"
            entity = ConsciousEntity(name)
            self.entities.append(entity)

        print(f"✅ Created {len(self.entities)} conscious entities")

    async def run_simulation_cycle(self):
        """Run one simulation cycle"""
        self.simulation_cycle += 1

        # Age all entities
        for entity in self.entities:
            if entity.is_alive:
                entity.age_one_cycle()

        # Process interactions
        await self.process_interactions()

        # Environmental effects
        self.apply_environmental_effects()

        # Evolution cycle (every 50 cycles)
        if self.simulation_cycle % 50 == 0:
            await self.evolution_cycle()

        # Remove dead entities
        self.entities = [e for e in self.entities if e.is_alive]

        # Maintain population
        if len(self.entities) < self.evolution_engine.target_population * 0.8:
            await self.repopulate()

        # OASIS integration
        if self.oasis_bridge:
            await self.update_oasis()

    async def process_interactions(self):
        """Process entity interactions"""
        # Random interactions between entities
        num_interactions = min(len(self.entities) // 2, 10)

        for _ in range(num_interactions):
            if len(self.entities) < 2:
                break

            entity1, entity2 = random.sample(self.entities, 2)

            if not entity1.is_alive or not entity2.is_alive:
                continue

            # Determine interaction type
            situation = {
                'social_opportunity': random.random(),
                'danger_level': random.random() * 0.3
            }

            decision1 = entity1.make_decision(situation)
            decision2 = entity2.make_decision(situation)

            # Process interaction
            if decision1 == 'socialize' and decision2 == 'socialize':
                interaction_type = 'positive' if random.random() > 0.2 else 'negative'
                entity1.interact_with(entity2, interaction_type)
                entity2.interact_with(entity1, interaction_type)

                # Fitness reward for successful social interaction
                if interaction_type == 'positive':
                    entity1.genome.fitness_score += 0.1
                    entity2.genome.fitness_score += 0.1

    def apply_environmental_effects(self):
        """Apply environmental effects to entities"""
        for entity in self.entities:
            if not entity.is_alive:
                continue

            # Learning environment boosts consciousness development
            if self.environment_factors['learning_environment']:
                entity.consciousness_level = min(1.0, entity.consciousness_level + 0.001)

            # Stressful environment affects emotional state
            if self.environment_factors['stressful_environment']:
                entity.emotional_state['anxiety'] = min(1.0, entity.emotional_state['anxiety'] + 0.01)
                entity.emotional_state['happiness'] = max(0.0, entity.emotional_state['happiness'] - 0.005)

    async def evolution_cycle(self):
        """Run evolution cycle"""
        print(f"🧬 Evolution Cycle {self.evolution_engine.generation + 1}")

        # Apply environmental pressure
        self.evolution_engine.apply_environmental_pressure(self.entities, self.environment_factors)

        # Create next generation
        self.entities = self.evolution_engine.create_next_generation(self.entities)

        print(f"✅ Generation {self.evolution_engine.generation} complete - Population: {len(self.entities)}")

    async def repopulate(self):
        """Repopulate if population is too low"""
        needed = self.evolution_engine.target_population - len(self.entities)
        if needed > 0:
            print(f"👶 Repopulating with {needed} new entities")
            for i in range(needed):
                name = f"NewEntity{self.simulation_cycle}_{i}"
                entity = ConsciousEntity(name)
                self.entities.append(entity)

    async def update_oasis(self):
        """Update OASIS integration"""
        if self.oasis_bridge:
            # Convert conscious entities to OASIS NPCs
            oasis_npcs = []
            for entity in self.entities[:10]:  # Top 10 entities
                npc_data = {
                    'name': entity.name,
                    'personality': entity.genome.personality,
                    'consciousness': entity.consciousness_level,
                    'emotions': entity.emotional_state,
                    'location': entity.location
                }
                oasis_npcs.append(npc_data)

            # Send to OASIS bridge
            await self.oasis_bridge.update_npcs(oasis_npcs)

    def get_statistics(self):
        """Get current simulation statistics"""
        if not self.entities:
            return {}

        alive_entities = [e for e in self.entities if e.is_alive]

        return {
            'simulation_cycle': self.simulation_cycle,
            'total_entities': len(self.entities),
            'alive_entities': len(alive_entities),
            'avg_age': sum(e.age for e in alive_entities) / len(alive_entities) if alive_entities else 0,
            'avg_consciousness': sum(e.consciousness_level for e in alive_entities) / len(alive_entities) if alive_entities else 0,
            'avg_fitness': sum(e.genome.fitness_score for e in alive_entities) / len(alive_entities) if alive_entities else 0,
            'generation': self.evolution_engine.generation,
            'environment': self.environment_factors
        }

    def display_dashboard(self):
        """Display real-time simulation dashboard"""
        stats = self.get_statistics()

        print("\n" + "="*60)
        print("🧬 LIVING EVOLUTION SIMULATION DASHBOARD")
        print("="*60)
        print(f"Cycle: {stats.get('simulation_cycle', 0)} | Generation: {stats.get('generation', 0)}")
        print(f"Population: {stats.get('alive_entities', 0)}/{stats.get('total_entities', 0)} entities")
        print(".2f")
        print(".3f")
        print(".2f")
        print(f"Environment: Social={self.environment_factors['social_environment']}, Learning={self.environment_factors['learning_environment']}, Stress={self.environment_factors['stressful_environment']}")

        # Top entities by consciousness
        if self.entities:
            top_entities = sorted([e for e in self.entities if e.is_alive],
                                key=lambda x: x.consciousness_level, reverse=True)[:5]
            print("\n🎯 Top Conscious Entities:")
            for i, entity in enumerate(top_entities, 1):
                print(".3f"
                      f"Age:{entity.age} Fit:{entity.genome.fitness_score:.1f}")

        print("="*60)

    async def run_simulation(self, max_cycles=None):
        """Run the simulation"""
        self.is_running = True
        print("🚀 Starting Living Evolution Simulation...")

        try:
            cycle_count = 0
            while self.is_running and (max_cycles is None or cycle_count < max_cycles):
                await self.run_simulation_cycle()

                if cycle_count % 10 == 0:  # Update dashboard every 10 cycles
                    self.display_dashboard()

                await asyncio.sleep(self.cycle_interval)
                cycle_count += 1

        except KeyboardInterrupt:
            print("\n⏹️  Simulation stopped by user")
        finally:
            self.is_running = False
            self.save_simulation_state()

    def save_simulation_state(self, filename="evolution_state.json"):
        """Save simulation state"""
        state = {
            'simulation_cycle': self.simulation_cycle,
            'generation': self.evolution_engine.generation,
            'entities': [entity.to_dict() for entity in self.entities],
            'population_history': self.evolution_engine.population_history,
            'fitness_history': self.evolution_engine.fitness_history,
            'environment_factors': self.environment_factors,
            'timestamp': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"💾 Simulation state saved to {filename}")

    def load_simulation_state(self, filename="evolution_state.json"):
        """Load simulation state"""
        if not os.path.exists(filename):
            return False

        with open(filename, 'r') as f:
            state = json.load(f)

        self.simulation_cycle = state.get('simulation_cycle', 0)
        self.evolution_engine.generation = state.get('generation', 0)
        self.entities = [ConsciousEntity.from_dict(e_data) for e_data in state.get('entities', [])]
        self.evolution_engine.population_history = state.get('population_history', [])
        self.evolution_engine.fitness_history = state.get('fitness_history', [])
        self.environment_factors = state.get('environment_factors', self.environment_factors)

        print(f"📂 Simulation state loaded from {filename}")
        return True

# ============================================================================
# OASIS INTEGRATION BRIDGE
# ============================================================================

class OasisBridge:
    """Bridge between evolution simulation and OASIS virtual world"""
    def __init__(self, oasis_world_path="oasis_world.json"):
        self.oasis_world_path = oasis_world_path
        self.npc_entities = []

    async def update_npcs(self, npc_data):
        """Update OASIS with conscious NPCs"""
        self.npc_entities = npc_data

        # This would integrate with the actual OASIS system
        # For now, just save to a bridge file
        bridge_data = {
            'npcs': npc_data,
            'timestamp': datetime.now().isoformat()
        }

        with open('oasis_bridge.json', 'w') as f:
            json.dump(bridge_data, f, indent=2)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point"""
    print("🧬 Living Evolution System - Conscious Entity Evolution")
    print("="*60)

    # Initialize simulation
    simulation = EvolutionSimulation()

    # Try to load previous state
    if not simulation.load_simulation_state():
        await simulation.initialize_population(30)

    # Setup OASIS integration (optional)
    if os.path.exists("oasis_world.json"):
        simulation.oasis_bridge = OasisBridge()
        print("🌐 OASIS integration enabled")

    # Environment configuration
    simulation.environment_factors = {
        'social_environment': True,
        'learning_environment': True,
        'stressful_environment': False
    }

    # Run simulation
    try:
        await simulation.run_simulation(max_cycles=200)  # Run for 200 cycles
    except KeyboardInterrupt:
        print("\n⏹️  Simulation interrupted")

    # Final statistics
    print("\n" + "="*60)
    print("🏁 SIMULATION COMPLETE")
    print("="*60)

    final_stats = simulation.get_statistics()
    print(f"Final Cycle: {final_stats.get('simulation_cycle', 0)}")
    print(f"Generations: {final_stats.get('generation', 0)}")
    print(f"Population: {final_stats.get('alive_entities', 0)}")
    print(".2f")
    print(".3f")
    print(".2f")

    if simulation.entities:
        oldest = max(simulation.entities, key=lambda x: x.age)
        most_conscious = max(simulation.entities, key=lambda x: x.consciousness_level)
        fittest = max(simulation.entities, key=lambda x: x.genome.fitness_score)

        print(f"\n🏆 Notable Entities:")
        print(f"Oldest: {oldest.name} (Age: {oldest.age})")
        print(f"Most Conscious: {most_conscious.name} (Level: {most_conscious.consciousness_level:.3f})")
        print(f"Fittest: {fittest.name} (Fitness: {fittest.genome.fitness_score:.1f})")

    print("\n💾 Final state saved to evolution_state.json")
    print("🌐 OASIS bridge data saved to oasis_bridge.json")

if __name__ == "__main__":
    asyncio.run(main())