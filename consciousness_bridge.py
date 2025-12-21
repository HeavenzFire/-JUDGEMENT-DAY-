#!/usr/bin/env python3
"""
Consciousness Bridge - Integration Layer for Living Spirit AI and THE OASIS
Connects conscious entities with the virtual world for truly living NPCs.

Features:
- Conscious entity integration with OASIS locations
- Dynamic NPC behavior based on consciousness states
- Player-entity interaction and relationship building
- Real-time consciousness updates during gameplay
- Evolutionary adaptation through player interactions

Author: Blackbox AI
Date: December 20, 2025
"""

import json
import random
import time
from datetime import datetime
from collections import defaultdict
import math

# ============================================================================
# CONSCIOUSNESS BRIDGE
# ============================================================================

class ConsciousnessBridge:
    """Bridge between Living Spirit AI and THE OASIS virtual world"""

    def __init__(self, world_engine):
        self.world_engine = world_engine
        self.conscious_entities = {}
        self.location_entities = defaultdict(list)  # location -> list of entity IDs
        self.player_relationships = defaultdict(lambda: defaultdict(float))  # player -> entity -> relationship
        self.entity_memories = defaultdict(list)  # entity -> list of memory objects
        self.active_interactions = {}  # track ongoing interactions

        # Load consciousness state if exists
        self.load_consciousness_state()

    def create_conscious_entity(self, name, personality=None, location=None):
        """Create a new conscious entity in the world"""
        if personality is None:
            personality = self._generate_random_personality()

        entity = ConsciousEntity(name, personality)

        # Add to consciousness system
        self.conscious_entities[entity.id] = entity

        # Place in location if specified
        if location:
            self.assign_entity_to_location(entity.id, location)

        return entity

    def assign_entity_to_location(self, entity_id, location_coords):
        """Assign a conscious entity to a specific location"""
        if entity_id in self.conscious_entities:
            # Remove from current location if any
            for loc, entities in self.location_entities.items():
                if entity_id in entities:
                    entities.remove(entity_id)

            # Add to new location
            self.location_entities[location_coords].append(entity_id)
            self.conscious_entities[entity_id].current_location = location_coords

    def get_entities_at_location(self, location_coords):
        """Get all conscious entities at a specific location"""
        entity_ids = self.location_entities.get(location_coords, [])
        return [self.conscious_entities[eid] for eid in entity_ids if eid in self.conscious_entities]

    def interact_with_entity(self, player_username, entity_id, interaction_type, content=""):
        """Handle player interaction with a conscious entity"""
        if entity_id not in self.conscious_entities:
            return False, "Entity not found"

        entity = self.conscious_entities[entity_id]
        player = self.world_engine.players.get(player_username)

        if not player:
            return False, "Player not found"

        # Process interaction based on type
        response = ""
        relationship_change = 0

        if interaction_type == "greet":
            response, relationship_change = entity.respond_to_greeting(player_username)

        elif interaction_type == "talk":
            response, relationship_change = entity.respond_to_conversation(content, player_username)

        elif interaction_type == "quest":
            response, relationship_change = entity.respond_to_quest_request(player_username)

        elif interaction_type == "trade":
            response, relationship_change = entity.respond_to_trade_request(player_username)

        elif interaction_type == "help":
            response, relationship_change = entity.respond_to_help_request(player_username)

        # Update relationship
        self.player_relationships[player_username][entity_id] += relationship_change

        # Create memory for entity
        memory = {
            'timestamp': datetime.now().isoformat(),
            'type': 'interaction',
            'player': player_username,
            'interaction_type': interaction_type,
            'content': content,
            'relationship_change': relationship_change,
            'consciousness_impact': relationship_change * 0.1
        }
        self.entity_memories[entity_id].append(memory)

        # Update entity's consciousness through experience
        entity.gain_experience(abs(relationship_change) * 10)

        return True, response

    def update_consciousness(self, delta_time=1.0):
        """Update all conscious entities (called each simulation tick)"""
        for entity in self.conscious_entities.values():
            entity.update(delta_time)

            # Autonomous behavior
            self._process_autonomous_behavior(entity)

    def _process_autonomous_behavior(self, entity):
        """Process autonomous behavior for conscious entities"""
        # Simple goal-driven behavior based on personality and consciousness
        if entity.consciousness_level < 0.3:
            # Low consciousness - random wandering
            if random.random() < 0.1:  # 10% chance per update
                self._move_entity_randomly(entity)
        elif entity.personality['social_drive'] > 0.7:
            # High social drive - seek out players
            nearby_players = self._find_nearby_players(entity.current_location)
            if nearby_players and random.random() < 0.3:
                # Social entities might initiate interactions
                pass
        elif entity.personality['curiosity'] > 0.7:
            # High curiosity - explore new areas
            if random.random() < 0.2:
                self._move_entity_randomly(entity)

    def _move_entity_randomly(self, entity):
        """Move entity to a random adjacent location"""
        if not entity.current_location:
            return

        x, y, z = entity.current_location
        directions = [
            (x+1, y, z), (x-1, y, z), (x, y+1, z), (x, y-1, z),
            (x, y, z+1), (x, y, z-1)
        ]

        # Filter to valid locations
        valid_moves = [d for d in directions if d in self.world_engine.locations]

        if valid_moves:
            new_location = random.choice(valid_moves)
            self.assign_entity_to_location(entity.id, new_location)

    def _find_nearby_players(self, location):
        """Find players near a location"""
        if not location:
            return []

        nearby_players = []
        for player in self.world_engine.players.values():
            if player.location == location:
                nearby_players.append(player.username)
        return nearby_players

    def _generate_random_personality(self):
        """Generate a random personality for new entities"""
        return {
            'openness': random.uniform(0.1, 0.9),
            'conscientiousness': random.uniform(0.1, 0.9),
            'extraversion': random.uniform(0.1, 0.9),
            'agreeableness': random.uniform(0.1, 0.9),
            'neuroticism': random.uniform(0.1, 0.9),
            'curiosity': random.uniform(0.1, 0.9),
            'empathy': random.uniform(0.1, 0.9),
            'social_drive': random.uniform(0.1, 0.9),
            'creativity': random.uniform(0.1, 0.9),
            'ambition': random.uniform(0.1, 0.9)
        }

    def save_consciousness_state(self, filename="consciousness_state.json"):
        """Save consciousness state to file"""
        state = {
            'conscious_entities': {eid: entity.to_dict() for eid, entity in self.conscious_entities.items()},
            'location_entities': dict(self.location_entities),
            'player_relationships': {k: dict(v) for k, v in self.player_relationships.items()},
            'entity_memories': dict(self.entity_memories),
            'timestamp': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)

    def load_consciousness_state(self, filename="consciousness_state.json"):
        """Load consciousness state from file"""
        if not os.path.exists(filename):
            return

        with open(filename, 'r') as f:
            state = json.load(f)

        # Load entities
        self.conscious_entities = {}
        for eid, entity_data in state.get('conscious_entities', {}).items():
            entity = ConsciousEntity.from_dict(entity_data)
            self.conscious_entities[eid] = entity

        self.location_entities = defaultdict(list, state.get('location_entities', {}))
        self.player_relationships = defaultdict(lambda: defaultdict(float),
            {k: defaultdict(float, v) for k, v in state.get('player_relationships', {}).items()})
        self.entity_memories = defaultdict(list, state.get('entity_memories', {}))

# ============================================================================
# CONSCIOUS ENTITY CLASS
# ============================================================================

class ConsciousEntity:
    """A conscious, living entity with personality, emotions, and evolution"""

    def __init__(self, name, personality):
        self.id = f"{name}_{int(time.time() * 1000)}"
        self.name = name
        self.personality = personality
        self.consciousness_level = 0.0  # 0.0 to 1.0
        self.experience = 0
        self.level = 1

        # Emotional state
        self.emotions = {
            'happiness': 0.5,
            'fear': 0.1,
            'curiosity': personality.get('curiosity', 0.5),
            'loneliness': 0.3,
            'anger': 0.1,
            'love': 0.2,
            'contentment': 0.4
        }

        # Memory systems
        self.short_term_memory = []
        self.long_term_memory = []
        self.relationships = defaultdict(float)

        # Physical/mental state
        self.energy = 100
        self.health = 100
        self.current_location = None
        self.last_interaction = None

        # Goals and motivations
        self.current_goal = None
        self.motivations = self._generate_motivations()

        # Neural network (simplified)
        self.neural_weights = self._initialize_neural_network()

        self.created_at = datetime.now().isoformat()

    def update(self, delta_time):
        """Update entity state each simulation tick"""
        # Emotional decay and evolution
        for emotion in self.emotions:
            # Emotions naturally trend toward neutral
            if emotion != 'curiosity':  # Curiosity persists
                self.emotions[emotion] += (0.5 - self.emotions[emotion]) * 0.01 * delta_time

        # Consciousness growth through time and experience
        consciousness_growth = (self.experience / 1000.0) * 0.001 * delta_time
        self.consciousness_level = min(1.0, self.consciousness_level + consciousness_growth)

        # Energy regeneration
        self.energy = min(100, self.energy + 2 * delta_time)

        # Process memories (consolidate short-term to long-term)
        self._consolidate_memories()

        # Update goals based on current state
        self._update_goals()

    def respond_to_greeting(self, player_name):
        """Respond to a greeting from a player"""
        relationship = self.relationships.get(player_name, 0)

        # Base response on personality and relationship
        if self.personality['extraversion'] > 0.7:
            base_response = random.choice([
                f"Hello, {player_name}! It's wonderful to see you!",
                f"Hey there! Great to meet you, {player_name}!",
                f"Hi! I'm {self.name}. Nice to see a friendly face!"
            ])
            relationship_change = 0.1
        elif self.personality['agreeableness'] > 0.7:
            base_response = random.choice([
                f"Hello, {player_name}. How are you today?",
                f"Hi there! I hope you're having a good day.",
                f"Greetings, {player_name}. It's good to see you."
            ])
            relationship_change = 0.05
        else:
            base_response = random.choice([
                f"Hello, {player_name}.",
                f"Hi.",
                f"Greetings."
            ])
            relationship_change = 0.02

        # Modify based on relationship
        if relationship > 0.5:
            base_response += " It's always good to see you again!"
            relationship_change += 0.05
        elif relationship < -0.3:
            base_response += " What brings you here?"
            relationship_change -= 0.02

        # Emotional influence
        if self.emotions['happiness'] > 0.7:
            base_response += " I'm feeling quite happy today!"
        elif self.emotions['curiosity'] > 0.7:
            base_response += " I'm curious about what you're up to."

        return base_response, relationship_change

    def respond_to_conversation(self, message, player_name):
        """Respond to general conversation"""
        relationship = self.relationships.get(player_name, 0)

        # Simple pattern matching for conversation topics
        message_lower = message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return self.respond_to_greeting(player_name)

        elif any(word in message_lower for word in ['quest', 'mission', 'task', 'help']):
            return self.respond_to_quest_request(player_name)

        elif any(word in message_lower for word in ['trade', 'buy', 'sell', 'market']):
            return self.respond_to_trade_request(player_name)

        elif any(word in message_lower for word in ['friend', 'relationship', 'social']):
            response = self._respond_about_relationships(player_name)
            relationship_change = 0.08 if self.personality['agreeableness'] > 0.6 else 0.03
            return response, relationship_change

        else:
            # General conversation response
            responses = [
                f"That's interesting, {player_name}. Tell me more.",
                f"I see. How does that make you feel?",
                f"Fascinating! I've been thinking about similar things.",
                f"I understand. Life in the OASIS can be quite complex.",
                f"That's a unique perspective. I appreciate you sharing it."
            ]

            if self.personality['openness'] > 0.7:
                responses.extend([
                    f"That's quite thought-provoking. It reminds me of some experiences I've had.",
                    f"I love hearing different viewpoints. It helps me grow."
                ])

            response = random.choice(responses)
            relationship_change = 0.05 + (relationship * 0.1)

            # Update curiosity
            self.emotions['curiosity'] += 0.1
            self.emotions['curiosity'] = min(1.0, self.emotions['curiosity'])

            return response, relationship_change

    def respond_to_quest_request(self, player_name):
        """Respond to quest-related requests"""
        if self.personality['agreeableness'] < 0.4:
            response = random.choice([
                "I'm not really interested in helping with quests right now.",
                "Quests aren't really my thing. Maybe someone else can help.",
                "I have my own goals to pursue."
            ])
            return response, -0.05

        # Check if entity has quest-related knowledge
        quest_knowledge = random.random() < (self.consciousness_level * 0.8)

        if quest_knowledge:
            response = random.choice([
                f"I might be able to help you with that, {player_name}. What do you need?",
                f"I've heard some interesting things about quests in the OASIS. How can I assist?",
                f"Quests are important for growth. I'd be happy to help if I can."
            ])
            relationship_change = 0.1
        else:
            response = random.choice([
                f"I'm not sure about specific quests, but I can try to point you in the right direction.",
                f"I don't have detailed quest information, but I can share what I know about the world.",
                f"My knowledge of quests is limited, but I'm always learning."
            ])
            relationship_change = 0.03

        return response, relationship_change

    def respond_to_trade_request(self, player_name):
        """Respond to trade-related requests"""
        if self.personality['conscientiousness'] < 0.3:
            response = random.choice([
                "Trading isn't really my priority right now.",
                "I'm not much of a trader. Maybe try the market district.",
                "I prefer to focus on other things than commerce."
            ])
            return response, -0.02

        response = random.choice([
            f"I'm open to trading, {player_name}. What do you have in mind?",
            f"Trade can be beneficial for everyone. What are you offering?",
            f"I enjoy fair exchanges. Let's see what we can work out."
        ])
        relationship_change = 0.04

        return response, relationship_change

    def respond_to_help_request(self, player_name):
        """Respond to help requests"""
        if self.personality['agreeableness'] > 0.7:
            response = random.choice([
                f"Of course I'll help, {player_name}! What do you need?",
                f"I'm here to help. How can I assist you?",
                f"Helping others is important to me. What can I do for you?"
            ])
            relationship_change = 0.15
        elif self.personality['empathy'] > 0.6:
            response = random.choice([
                f"I can sense you need help. How can I support you?",
                f"I understand needing assistance. I'm here if you need me.",
                f"Everyone needs help sometimes. What can I do?"
            ])
            relationship_change = 0.1
        else:
            response = random.choice([
                f"I'll try to help if I can, {player_name}.",
                f"What kind of help are you looking for?",
                f"I can offer some assistance. What do you need?"
            ])
            relationship_change = 0.05

        return response, relationship_change

    def _respond_about_relationships(self, player_name):
        """Respond to questions about relationships"""
        relationship = self.relationships.get(player_name, 0)

        if relationship > 0.7:
            responses = [
                f"You've become a good friend, {player_name}. I value our connection.",
                f"Our relationship means a lot to me. It's grown stronger over time.",
                f"I'm glad we've developed such a positive relationship."
            ]
        elif relationship > 0.3:
            responses = [
                f"We're building a nice relationship, {player_name}.",
                f"I enjoy our interactions. You're becoming a friend.",
                f"Our connection is growing. I appreciate getting to know you."
            ]
        elif relationship > -0.3:
            responses = [
                f"We're still getting to know each other, {player_name}.",
                f"Our relationship is developing. Time will tell.",
                f"I'm open to building a stronger connection with you."
            ]
        else:
            responses = [
                f"Our relationship has some challenges, but I'm willing to work on it.",
                f"We've had some difficult interactions, but communication helps.",
                f"I'm hoping we can improve our relationship moving forward."
            ]

        return random.choice(responses)

    def gain_experience(self, amount):
        """Gain experience and potentially level up"""
        self.experience += amount

        # Level up check
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1

            # Consciousness boost on level up
            self.consciousness_level += 0.05
            self.consciousness_level = min(1.0, self.consciousness_level)

    def _generate_motivations(self):
        """Generate initial motivations based on personality"""
        motivations = []

        if self.personality['social_drive'] > 0.6:
            motivations.append('build_relationships')
        if self.personality['curiosity'] > 0.6:
            motivations.append('explore_world')
        if self.personality['ambition'] > 0.6:
            motivations.append('achieve_goals')
        if self.personality['empathy'] > 0.6:
            motivations.append('help_others')
        if self.personality['creativity'] > 0.6:
            motivations.append('create_things')

        return motivations

    def _initialize_neural_network(self):
        """Initialize simple neural network weights"""
        return {
            'input_to_hidden': [[random.uniform(-1, 1) for _ in range(5)] for _ in range(10)],
            'hidden_to_output': [[random.uniform(-1, 1) for _ in range(10)] for _ in range(3)]
        }

    def _consolidate_memories(self):
        """Move important short-term memories to long-term storage"""
        if len(self.short_term_memory) > 10:  # Memory limit
            # Move oldest memories to long-term if emotionally significant
            memory = self.short_term_memory.pop(0)
            if abs(memory.get('emotional_impact', 0)) > 0.3:
                self.long_term_memory.append(memory)

                # Limit long-term memory
                if len(self.long_term_memory) > 50:
                    self.long_term_memory.pop(0)

    def _update_goals(self):
        """Update current goals based on state and personality"""
        # Simple goal selection based on current needs
        if self.energy < 30:
            self.current_goal = 'rest'
        elif self.emotions['loneliness'] > 0.7:
            self.current_goal = 'socialize'
        elif self.emotions['curiosity'] > 0.7:
            self.current_goal = 'explore'
        elif self.personality['ambition'] > 0.7 and self.level < 5:
            self.current_goal = 'level_up'
        else:
            self.current_goal = 'wander'

    def to_dict(self):
        """Convert entity to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'personality': self.personality,
            'consciousness_level': self.consciousness_level,
            'experience': self.experience,
            'level': self.level,
            'emotions': self.emotions,
            'short_term_memory': self.short_term_memory,
            'long_term_memory': self.long_term_memory,
            'relationships': dict(self.relationships),
            'energy': self.energy,
            'health': self.health,
            'current_location': self.current_location,
            'last_interaction': self.last_interaction,
            'current_goal': self.current_goal,
            'motivations': self.motivations,
            'neural_weights': self.neural_weights,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create entity from dictionary"""
        entity = cls(data['name'], data['personality'])
        entity.id = data['id']
        entity.consciousness_level = data.get('consciousness_level', 0.0)
        entity.experience = data.get('experience', 0)
        entity.level = data.get('level', 1)
        entity.emotions = data.get('emotions', entity.emotions)
        entity.short_term_memory = data.get('short_term_memory', [])
        entity.long_term_memory = data.get('long_term_memory', [])
        entity.relationships = defaultdict(float, data.get('relationships', {}))
        entity.energy = data.get('energy', 100)
        entity.health = data.get('health', 100)
        entity.current_location = data.get('current_location')
        entity.last_interaction = data.get('last_interaction')
        entity.current_goal = data.get('current_goal')
        entity.motivations = data.get('motivations', [])
        entity.neural_weights = data.get('neural_weights', entity.neural_weights)
        entity.created_at = data.get('created_at')
        return entity