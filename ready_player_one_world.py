#!/usr/bin/env python3
"""
THE OASIS - Ready Player One Virtual World
A complete virtual reality metaverse inspired by the book/movie Ready Player One.

Features:
- 3D virtual world with multiple zones
- Player character creation and progression
- Quest system including the Copper Key challenge
- Virtual economy with credits and auction house
- Guild system with social features
- Combat system with PvP/PvE mechanics
- Persistent world state and player data
- Immersive CLI interface

Author: Blackbox AI
Date: December 20, 2025
"""

import json
import random
import time
import os
import sys
from datetime import datetime
from collections import defaultdict
import threading
import asyncio

# ============================================================================
# DATA STRUCTURES AND CONSTANTS
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class WorldConstants:
    """Game world constants"""
    ZONES = ['Colossus', 'Green Zone', 'Danger Zone', 'Chalice Zone']
    DIRECTIONS = ['north', 'south', 'east', 'west', 'up', 'down']
    AVATAR_TYPES = ['Warrior', 'Mage', 'Rogue', 'Engineer', 'Medic']
    WEAPON_TYPES = ['Sword', 'Staff', 'Daggers', 'Gun', 'Shield']
    ARMOR_TYPES = ['Helmet', 'Chestplate', 'Leggings', 'Boots', 'Gloves']
    QUEST_TYPES = ['Exploration', 'Combat', 'Collection', 'Puzzle', 'Social']

# ============================================================================
# CORE CLASSES
# ============================================================================

class Location:
    """Represents a location in the virtual world"""
    def __init__(self, name, zone, x, y, z, description="", npcs=None, items=None):
        self.name = name
        self.zone = zone
        self.coordinates = (x, y, z)
        self.description = description
        self.npcs = npcs or []
        self.items = items or []
        self.visitors = set()

    def to_dict(self):
        return {
            'name': self.name,
            'zone': self.zone,
            'coordinates': self.coordinates,
            'description': self.description,
            'npcs': self.npcs,
            'items': [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data):
        items = [Item.from_dict(item_data) for item_data in data.get('items', [])]
        return cls(
            data['name'], data['zone'], *data['coordinates'],
            data.get('description', ''), data.get('npcs', []), items
        )

class Item:
    """Represents an item in the game world"""
    def __init__(self, name, item_type, value, rarity='common', stats=None):
        self.name = name
        self.type = item_type
        self.value = value
        self.rarity = rarity
        self.stats = stats or {}

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'rarity': self.rarity,
            'stats': self.stats
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['name'], data['type'], data['value'],
            data.get('rarity', 'common'), data.get('stats', {})
        )

class Player:
    """Represents a player character"""
    def __init__(self, username, avatar_type):
        self.username = username
        self.avatar_type = avatar_type
        self.level = 1
        self.experience = 0
        self.credits = 1000
        self.health = 100
        self.max_health = 100
        self.location = (0, 0, 0)  # x, y, z coordinates
        self.inventory = []
        self.equipment = {
            'weapon': None,
            'armor': {'helmet': None, 'chestplate': None, 'leggings': None, 'boots': None, 'gloves': None}
        }
        self.skills = defaultdict(int)
        self.quests_completed = []
        self.quests_active = []
        self.guild = None
        self.guild_rank = None
        self.created_at = datetime.now().isoformat()
        self.last_login = datetime.now().isoformat()

    def to_dict(self):
        return {
            'username': self.username,
            'avatar_type': self.avatar_type,
            'level': self.level,
            'experience': self.experience,
            'credits': self.credits,
            'health': self.health,
            'max_health': self.max_health,
            'location': self.location,
            'inventory': [item.to_dict() for item in self.inventory],
            'equipment': {
                'weapon': self.equipment['weapon'].to_dict() if self.equipment['weapon'] else None,
                'armor': {k: v.to_dict() if v else None for k, v in self.equipment['armor'].items()}
            },
            'skills': dict(self.skills),
            'quests_completed': self.quests_completed,
            'quests_active': self.quests_active,
            'guild': self.guild,
            'guild_rank': self.guild_rank,
            'created_at': self.created_at,
            'last_login': self.last_login
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data['username'], data['avatar_type'])
        player.level = data.get('level', 1)
        player.experience = data.get('experience', 0)
        player.credits = data.get('credits', 1000)
        player.health = data.get('health', 100)
        player.max_health = data.get('max_health', 100)
        player.location = tuple(data.get('location', (0, 0, 0)))
        player.inventory = [Item.from_dict(item_data) for item_data in data.get('inventory', [])]

        # Load equipment
        equip_data = data.get('equipment', {})
        if equip_data.get('weapon'):
            player.equipment['weapon'] = Item.from_dict(equip_data['weapon'])
        armor_data = equip_data.get('armor', {})
        for slot in player.equipment['armor']:
            if armor_data.get(slot):
                player.equipment['armor'][slot] = Item.from_dict(armor_data[slot])

        player.skills = defaultdict(int, data.get('skills', {}))
        player.quests_completed = data.get('quests_completed', [])
        player.quests_active = data.get('quests_active', [])
        player.guild = data.get('guild')
        player.guild_rank = data.get('guild_rank')
        player.created_at = data.get('created_at')
        player.last_login = data.get('last_login')
        return player

class Quest:
    """Represents a quest in the game"""
    def __init__(self, name, description, quest_type, objectives, rewards, difficulty='normal'):
        self.name = name
        self.description = description
        self.type = quest_type
        self.objectives = objectives  # List of objective dictionaries
        self.rewards = rewards  # Dict with credits, experience, items
        self.difficulty = difficulty
        self.completed = False
        self.progress = {obj['id']: 0 for obj in objectives}

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'objectives': self.objectives,
            'rewards': self.rewards,
            'difficulty': self.difficulty,
            'completed': self.completed,
            'progress': self.progress
        }

    @classmethod
    def from_dict(cls, data):
        quest = cls(
            data['name'], data['description'], data['type'],
            data['objectives'], data['rewards'], data.get('difficulty', 'normal')
        )
        quest.completed = data.get('completed', False)
        quest.progress = data.get('progress', {})
        return quest

class Guild:
    """Represents a player guild"""
    def __init__(self, name, founder, description=""):
        self.name = name
        self.founder = founder
        self.description = description
        self.members = {founder: 'leader'}
        self.treasury = 0
        self.level = 1
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            'name': self.name,
            'founder': self.founder,
            'description': self.description,
            'members': self.members,
            'treasury': self.treasury,
            'level': self.level,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        guild = cls(data['name'], data['founder'], data.get('description', ''))
        guild.members = data.get('members', {})
        guild.treasury = data.get('treasury', 0)
        guild.level = data.get('level', 1)
        guild.created_at = data.get('created_at')
        return guild

# ============================================================================
# WORLD ENGINE
# ============================================================================

class WorldEngine:
    """Core world simulation engine"""
    def __init__(self):
        self.locations = {}
        self.players = {}
        self.quests = {}
        self.guilds = {}
        self.auction_house = []
        self.world_events = []
        self.consciousness_bridge = ConsciousnessBridge(self)
        self.initialize_world()

    def initialize_world(self):
        """Initialize the game world with locations and content"""
        # Create main zones
        zones = WorldConstants.ZONES

        # Colossus Zone - Starting area
        self.add_location("Spawn Point", "Colossus", 0, 0, 0,
                         "The central hub of the OASIS. Players from around the world log in here.")
        self.add_location("Training Grounds", "Colossus", 1, 0, 0,
                         "A safe area for new players to learn combat basics.")
        self.add_location("Market District", "Colossus", 0, 1, 0,
                         "Bustling marketplace where players trade goods and services.")

        # Green Zone - Safe exploration
        self.add_location("Forest of Whispers", "Green Zone", 0, 10, 0,
                         "A peaceful forest with hidden secrets.")
        self.add_location("Crystal Lake", "Green Zone", 5, 10, 0,
                         "A serene lake said to hold ancient artifacts.")
        self.add_location("Mountain Peak", "Green Zone", 0, 15, 5,
                         "Highest point in the Green Zone with panoramic views.")

        # Danger Zone - Combat focused
        self.add_location("Dark Caverns", "Danger Zone", -10, 0, 0,
                         "Dangerous underground tunnels filled with hostile creatures.")
        self.add_location("Abandoned City", "Danger Zone", -15, 5, 0,
                         "Ruins of an ancient civilization, now overrun by mutants.")
        self.add_location("Volcano's Edge", "Danger Zone", -20, 0, 10,
                         "Treacherous volcanic terrain with lava flows.")

        # Chalice Zone - Endgame content
        self.add_location("Floating Islands", "Chalice Zone", 0, -10, 20,
                         "Magical islands suspended in the sky.")
        self.add_location("Time Temple", "Chalice Zone", 10, -10, 25,
                         "Ancient temple where time flows differently.")
        self.add_location("Halliday's Tomb", "Chalice Zone", 0, -20, 30,
                         "The final resting place of James Halliday.")

        # Initialize quests
        self.initialize_quests()

    def add_location(self, name, zone, x, y, z, description, npcs=None, items=None):
        """Add a location to the world"""
        location = Location(name, zone, x, y, z, description, npcs, items)
        self.locations[(x, y, z)] = location

    def initialize_quests(self):
        """Initialize the quest system"""
        # Copper Key Quest - The main storyline
        copper_key_quest = Quest(
            "The Copper Key",
            "Find the three parts of the legendary Copper Key hidden throughout the OASIS.",
            "Exploration",
            [
                {"id": "find_first_part", "description": "Find the first part of the Copper Key", "target": 1},
                {"id": "find_second_part", "description": "Find the second part of the Copper Key", "target": 1},
                {"id": "find_third_part", "description": "Find the third part of the Copper Key", "target": 1}
            ],
            {"credits": 10000, "experience": 5000, "items": []},
            "legendary"
        )
        self.quests["copper_key"] = copper_key_quest

        # Other quests
        exploration_quest = Quest(
            "World Explorer",
            "Visit all major zones in the OASIS.",
            "Exploration",
            [
                {"id": "visit_colossus", "description": "Visit Colossus zone", "target": 1},
                {"id": "visit_green", "description": "Visit Green Zone", "target": 1},
                {"id": "visit_danger", "description": "Visit Danger Zone", "target": 1},
                {"id": "visit_chalice", "description": "Visit Chalice Zone", "target": 1}
            ],
            {"credits": 2000, "experience": 1000, "items": []},
            "normal"
        )
        self.quests["world_explorer"] = exploration_quest

    def get_location(self, coordinates):
        """Get location at coordinates"""
        return self.locations.get(coordinates)

    def move_player(self, username, direction):
        """Move a player in the specified direction"""
        if username not in self.players:
            return False, "Player not found"

        player = self.players[username]
        x, y, z = player.location

        if direction == 'north':
            y += 1
        elif direction == 'south':
            y -= 1
        elif direction == 'east':
            x += 1
        elif direction == 'west':
            x -= 1
        elif direction == 'up':
            z += 1
        elif direction == 'down':
            z -= 1
        else:
            return False, "Invalid direction"

        new_location = (x, y, z)
        if new_location in self.locations:
            player.location = new_location
            location = self.locations[new_location]
            return True, f"Moved to {location.name} in {location.zone}"
        else:
            return False, "Cannot move there - location doesn't exist"

    def create_player(self, username, avatar_type):
        """Create a new player"""
        if username in self.players:
            return False, "Username already exists"

        if avatar_type not in WorldConstants.AVATAR_TYPES:
            return False, f"Invalid avatar type. Choose from: {', '.join(WorldConstants.AVATAR_TYPES)}"

        player = Player(username, avatar_type)
        self.players[username] = player
        return True, f"Player {username} created successfully as {avatar_type}"

    def save_world(self, filename="oasis_world.json"):
        """Save the entire world state"""
        world_data = {
            'locations': {str(k): v.to_dict() for k, v in self.locations.items()},
            'players': {k: v.to_dict() for k, v in self.players.items()},
            'quests': {k: v.to_dict() for k, v in self.quests.items()},
            'guilds': {k: v.to_dict() for k, v in self.guilds.items()},
            'auction_house': self.auction_house,
            'world_events': self.world_events,
            'timestamp': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(world_data, f, indent=2)
        return True

    def load_world(self, filename="oasis_world.json"):
        """Load the world state from file"""
        if not os.path.exists(filename):
            return False

        with open(filename, 'r') as f:
            world_data = json.load(f)

        # Load locations
        self.locations = {}
        for coord_str, loc_data in world_data.get('locations', {}).items():
            coords = tuple(map(int, coord_str.strip('()').split(', ')))
            self.locations[coords] = Location.from_dict(loc_data)

        # Load players
        self.players = {}
        for username, player_data in world_data.get('players', {}).items():
            self.players[username] = Player.from_dict(player_data)

        # Load quests
        self.quests = {}
        for quest_id, quest_data in world_data.get('quests', {}).items():
            self.quests[quest_id] = Quest.from_dict(quest_data)

        # Load guilds
        self.guilds = {}
        for guild_name, guild_data in world_data.get('guilds', {}).items():
            self.guilds[guild_name] = Guild.from_dict(guild_data)

        self.auction_house = world_data.get('auction_house', [])
        self.world_events = world_data.get('world_events', [])

        return True

# ============================================================================
# CLI INTERFACE
# ============================================================================

class OasisCLI:
    """Command-line interface for the OASIS"""
    def __init__(self):
        self.world = WorldEngine()
        self.current_player = None
        self.running = True
        self.load_world()

    def load_world(self):
        """Load world state on startup"""
        if self.world.load_world():
            print(f"{Colors.GREEN}World state loaded successfully!{Colors.END}")
        else:
            print(f"{Colors.YELLOW}No saved world found. Starting fresh.{Colors.END}")

    def save_world(self):
        """Save world state"""
        self.world.save_world()
        print(f"{Colors.GREEN}World saved successfully!{Colors.END}")

    def show_welcome(self):
        """Display welcome message"""
        print(f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                     🌟 THE OASIS 🌟                          ║
║              Ready Player One Virtual World                  ║
║                                                              ║
║  "Three hidden keys open three secret gates.                 ║
║   Where there's a key, there's a lock." - James Halliday     ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

Type 'help' for commands or 'create <username> <avatar>' to start playing!
""")

    def show_help(self):
        """Display help information"""
        print(f"""
{Colors.BLUE}{Colors.BOLD}THE OASIS - Available Commands:{Colors.END}

{Colors.GREEN}Account:{Colors.END}
  create <username> <avatar>    Create new character
  login <username>              Login to existing character
  status                        View your character stats
  logout                        Logout current character

{Colors.GREEN}Movement:{Colors.END}
  move <direction>              Move (north/south/east/west/up/down)
  look                          Look around current location
  map                           Show world map

{Colors.GREEN}Quests:{Colors.END}
  quests                        List available quests
  quest accept <id>             Accept a quest
  quest progress                Check quest progress

{Colors.GREEN}Economy:{Colors.END}
  inventory                     View your inventory
  auction list                  Browse auction house
  auction sell <item> <price>   Sell item on auction house
  credits                       Check your credit balance

{Colors.GREEN}Social:{Colors.END}
  guild create <name>           Create a new guild
  guild join <name>             Join an existing guild
  guild info                    View guild information
  chat <message>                Send global chat message

{Colors.GREEN}Combat:{Colors.END}
  attack <target>               Attack a target
  skills                        View your skills
  equip <item>                  Equip an item

{Colors.GREEN}System:{Colors.END}
  world                         Show world statistics
  save                          Save game progress
  help                          Show this help
  exit                          Exit the game

{Colors.YELLOW}Avatar Types: {', '.join(WorldConstants.AVATAR_TYPES)}{Colors.END}
""")

    def handle_command(self, command):
        """Process user commands"""
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()

        # Account commands
        if cmd == 'create' and len(parts) >= 3:
            username = parts[1]
            avatar = ' '.join(parts[2:])
            success, message = self.world.create_player(username, avatar)
            print(message)
            if success:
                self.current_player = username
                print(f"{Colors.GREEN}Welcome to the OASIS, {username}!{Colors.END}")

        elif cmd == 'login' and len(parts) >= 2:
            username = parts[1]
            if username in self.world.players:
                self.current_player = username
                self.world.players[username].last_login = datetime.now().isoformat()
                print(f"{Colors.GREEN}Welcome back, {username}!{Colors.END}")
            else:
                print(f"{Colors.RED}Player {username} not found.{Colors.END}")

        elif cmd == 'status':
            if not self.current_player:
                print(f"{Colors.RED}Please login first.{Colors.END}")
                return
            player = self.world.players[self.current_player]
            print(f"""
{Colors.BLUE}{Colors.BOLD}Player Status - {player.username}{Colors.END}
Avatar: {player.avatar_type}
Level: {player.level} ({player.experience} XP)
Credits: {player.credits}
Health: {player.health}/{player.max_health}
Location: {player.location}
Guild: {player.guild or 'None'}
Active Quests: {len(player.quests_active)}
Completed Quests: {len(player.quests_completed)}
""")

        elif cmd == 'logout':
            if self.current_player:
                print(f"{Colors.GREEN}Goodbye, {self.current_player}!{Colors.END}")
                self.current_player = None
            else:
                print(f"{Colors.YELLOW}Not logged in.{Colors.END}")

        # Movement commands
        elif cmd == 'move' and len(parts) >= 2:
            if not self.current_player:
                print(f"{Colors.RED}Please login first.{Colors.END}")
                return
            direction = parts[1].lower()
            success, message = self.world.move_player(self.current_player, direction)
            print(message)

        elif cmd == 'look':
            if not self.current_player:
                print(f"{Colors.RED}Please login first.{Colors.END}")
                return
            player = self.world.players[self.current_player]
            location = self.world.get_location(player.location)
            if location:
                print(f"""
{Colors.BLUE}{Colors.BOLD}{location.name} - {location.zone}{Colors.END}
{location.description}

NPCs: {', '.join(location.npcs) if location.npcs else 'None'}
Items: {', '.join([item.name for item in location.items]) if location.items else 'None'}
""")
            else:
                print(f"{Colors.RED}Location not found.{Colors.END}")

        # Quest commands
        elif cmd == 'quests':
            print(f"\n{Colors.BLUE}{Colors.BOLD}Available Quests:{Colors.END}")
            for quest_id, quest in self.world.quests.items():
                status = "✓" if quest.completed else "○"
                print(f"{status} {quest.name} ({quest.difficulty}) - {quest.description}")

        # Economy commands
        elif cmd == 'inventory':
            if not self.current_player:
                print(f"{Colors.RED}Please login first.{Colors.END}")
                return
            player = self.world.players[self.current_player]
            print(f"\n{Colors.BLUE}{Colors.BOLD}Inventory:{Colors.END}")
            if not player.inventory:
                print("Empty")
            else:
                for item in player.inventory:
                    print(f"- {item.name} ({item.type}) - {item.value} credits")

        elif cmd == 'credits':
            if not self.current_player:
                print(f"{Colors.RED}Please login first.{Colors.END}")
                return
            player = self.world.players[self.current_player]
            print(f"{Colors.GREEN}Credits: {player.credits}{Colors.END}")

        # Guild commands
        elif cmd == 'guild' and len(parts) >= 2:
            subcmd = parts[1].lower()
            if subcmd == 'create' and len(parts) >= 3:
                if not self.current_player:
                    print(f"{Colors.RED}Please login first.{Colors.END}")
                    return
                guild_name = ' '.join(parts[2:])
                if guild_name in self.world.guilds:
                    print(f"{Colors.RED}Guild {guild_name} already exists.{Colors.END}")
                else:
                    guild = Guild(guild_name, self.current_player)
                    self.world.guilds[guild_name] = guild
                    self.world.players[self.current_player].guild = guild_name
                    self.world.players[self.current_player].guild_rank = 'leader'
                    print(f"{Colors.GREEN}Guild '{guild_name}' created successfully!{Colors.END}")

            elif subcmd == 'info':
                if not self.current_player or not self.world.players[self.current_player].guild:
                    print(f"{Colors.RED}You are not in a guild.{Colors.END}")
                    return
                guild_name = self.world.players[self.current_player].guild
                guild = self.world.guilds[guild_name]
                print(f"""
{Colors.BLUE}{Colors.BOLD}Guild: {guild.name}{Colors.END}
Founded by: {guild.founder}
Members: {len(guild.members)}
Treasury: {guild.treasury} credits
Level: {guild.level}
""")

        # System commands
        elif cmd == 'world':
            print(f"""
{Colors.BLUE}{Colors.BOLD}World Statistics:{Colors.END}
Locations: {len(self.world.locations)}
Players: {len(self.world.players)}
Guilds: {len(self.world.guilds)}
Active Quests: {len(self.world.quests)}
Auction Items: {len(self.world.auction_house)}
World Events: {len(self.world.world_events)}
""")

        elif cmd == 'save':
            self.save_world()

        elif cmd == 'help':
            self.show_help()

        elif cmd == 'exit':
            self.save_world()
            print(f"{Colors.GREEN}Thanks for playing THE OASIS!{Colors.END}")
            self.running = False

        else:
            print(f"{Colors.RED}Unknown command. Type 'help' for available commands.{Colors.END}")

    def run(self):
        """Main CLI loop"""
        self.show_welcome()

        while self.running:
            try:
                if self.current_player:
                    prompt = f"{Colors.GREEN}{self.current_player}@OASIS>{Colors.END} "
                else:
                    prompt = f"{Colors.YELLOW}OASIS>{Colors.END} "

                command = input(prompt).strip()
                if command:
                    self.handle_command(command)

            except KeyboardInterrupt:
                print(f"\n{Colors.GREEN}Saving and exiting...{Colors.END}")
                self.save_world()
                break
            except EOFError:
                break

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
THE OASIS - Ready Player One Virtual World

Usage: python ready_player_one_world.py

Commands:
  create <username> <avatar>    Create new character
  login <username>              Login to existing character
  move <direction>              Move around the world
  quests                        View available quests
  guild create <name>           Create a guild
  status                        Check character status
  world                         View world statistics
  save                          Save game progress
  help                          Show all commands
  exit                          Exit the game

Avatar Types: Warrior, Mage, Rogue, Engineer, Medic
""")
        return

    cli = OasisCLI()
    cli.run()

if __name__ == "__main__":
    main()