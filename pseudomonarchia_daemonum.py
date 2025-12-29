import json
from typing import Dict, Any, List
from arisen_core import ArisenCore

class Demon:
    """
    Represents a demon from Pseudomonarchia Daemonum
    Implements the false monarchy hierarchy with syntropic resonance
    """

    def __init__(self, name: str, rank: str, appearance: str, powers: List[str],
                 legions: int, conjuration_notes: Dict[str, Any]):
        self.name = name
        self.rank = rank
        self.appearance = appearance
        self.powers = powers
        self.legions = legions
        self.conjuration_notes = conjuration_notes
        self.syntropic_signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generate syntropic signature for the demon"""
        core = ArisenCore()
        demon_data = {
            'name': self.name,
            'rank': self.rank,
            'appearance': self.appearance,
            'powers': self.powers,
            'legions': self.legions
        }
        return core.generate_master_seal(demon_data)

    def calculate_invocation_resonance(self, invocation_data: Dict[str, Any]) -> float:
        """Calculate resonance for invocation attempt"""
        core = ArisenCore()
        return core.calculate_resonance(invocation_data, 'governance')

    def verify_invocation_seal(self, invocation_data: Dict[str, Any], seal: str) -> bool:
        """Verify invocation using master seal"""
        core = ArisenCore()
        return core.verify_master_seal(invocation_data, seal)

class PseudomonarchiaDaemonum:
    """
    The False Monarchy of Demons
    Catalogs the 69 demons with syntropic ordering and invocation protocols
    """

    def __init__(self):
        self.arisen_core = ArisenCore()
        self.demon_catalog = self._initialize_demon_catalog()
        self.invocation_threshold = 0.8  # Minimum resonance for successful invocation

    def _initialize_demon_catalog(self) -> Dict[str, Demon]:
        """Initialize the catalog of 69 demons from Pseudomonarchia Daemonum"""
        catalog = {}

        # Kings
        catalog['Bael'] = Demon(
            name='Bael',
            rank='King',
            appearance='A cat, toad, man, or all three at once',
            powers=['Teaches invisible arts', 'Makes men wise in all liberal sciences'],
            legions=66,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears in diverse shapes'}
        )

        catalog['Agares'] = Demon(
            name='Agares',
            rank='Duke',
            appearance='An old man riding a crocodile, carrying a goshawk',
            powers=['Teaches all tongues', 'Destroys dignities spiritual and temporal', 'Causes earthquakes'],
            legions=31,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears peaceably'}
        )

        catalog['Marbas'] = Demon(
            name='Marbas',
            rank='President',
            appearance='A great lion',
            powers=['Answers truly of things past, present, future', 'Causes and cures diseases', 'Gives wisdom in mechanical arts'],
            legions=36,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears in form of a lion'}
        )

        catalog['Pruflas'] = Demon(
            name='Pruflas',
            rank='Duke',
            appearance='A flame-headed warrior',
            powers=['Sets cities on fire', 'Answers questions of philosophy', 'Creates illusions'],
            legions=26,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears as a flame'}
        )

        catalog['Aamon'] = Demon(
            name='Aamon',
            rank='Marquis',
            appearance='A wolf with serpent tail, vomiting flames',
            powers=['Procures favor of friends and foes', 'Reconciles controversies', 'Teaches all sciences'],
            legions=40,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears as a wolf'}
        )

        catalog['Barbatos'] = Demon(
            name='Barbatos',
            rank='Duke',
            appearance='An archer in green, with bow and arrows',
            powers=['Understands birdsong', 'Reveals treasures hidden by magic', 'Knows past and future'],
            legions=30,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears with four kings'}
        )

        catalog['Paimon'] = Demon(
            name='Paimon',
            rank='King',
            appearance='Rides a dromedary, preceded by musicians',
            powers=['Teaches all arts and sciences', 'Reveals secrets', 'Commands 200 legions'],
            legions=200,
            conjuration_notes={'hour': 'Any', 'ritual': 'Must be received with honors'}
        )

        catalog['Buer'] = Demon(
            name='Buer',
            rank='President',
            appearance='A star with five points',
            powers=['Teaches moral philosophy', 'Logic', 'Properties of herbs and plants'],
            legions=50,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears in form of a star'}
        )

        catalog['Gusoyn'] = Demon(
            name='Gusoyn',
            rank='Duke',
            appearance='A xenophilus',
            powers=['Answers all questions', 'Reveals past, present, future'],
            legions=40,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears as a xenophilus'}
        )

        catalog['Botis'] = Demon(
            name='Botis',
            rank='President',
            appearance='A viper, then a man with horns and sword',
            powers=['Reconciles friends and foes', 'Gives true answers'],
            legions=60,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears as a viper then man'}
        )

        catalog['Corson'] = Demon(
            name='Corson',
            rank='Duke',
            appearance='Appears as before',
            powers=['Discovers treasures', 'Answers questions'],
            legions=40,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears peaceably'}
        )

        catalog['Ziminiar'] = Demon(
            name='Ziminiar',
            rank='Marquis',
            appearance='A soldier on a red horse',
            powers=['Finds stolen goods', 'Reveals secrets'],
            legions=20,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears as a soldier'}
        )

        catalog['Belial'] = Demon(
            name='Belial',
            rank='King',
            appearance='Two angels sitting in a chariot of fire',
            powers=['Distributes dignities', 'Gives favor of friends and enemies'],
            legions=80,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears with two angels'}
        )

        catalog['Decarabia'] = Demon(
            name='Decarabia',
            rank='Marquis',
            appearance='A star in a pentacle',
            powers=['Shows visions of birds and precious stones', 'Teaches geometry and liberal sciences'],
            legions=30,
            conjuration_notes={'hour': 'Any', 'ritual': 'Appears in a pentacle'}
        )

        # Continue with remaining demons... (truncated for brevity, but in full implementation would include all 69)
        # For complete implementation, all 69 demons would be listed here
        # This is a representative sample

        return catalog

    def get_demon(self, name: str) -> Demon:
        """Retrieve a demon by name"""
        return self.demon_catalog.get(name)

    def list_demons_by_rank(self, rank: str) -> List[Demon]:
        """List all demons of a specific rank"""
        return [demon for demon in self.demon_catalog.values() if demon.rank == rank]

    def invoke_demon(self, name: str, invocation_data: Dict[str, Any], seal: str) -> Dict[str, Any]:
        """
        Attempt to invoke a demon using syntropic resonance
        Returns invocation result with response if successful
        """
        demon = self.get_demon(name)
        if not demon:
            return {
                'status': 'DEMON_NOT_FOUND',
                'message': f'Demon {name} not found in the false monarchy'
            }

        # Verify invocation seal
        if not demon.verify_invocation_seal(invocation_data, seal):
            return {
                'status': 'INVALID_SEAL',
                'message': 'Invocation seal verification failed'
            }

        # Calculate resonance
        resonance = demon.calculate_invocation_resonance(invocation_data)
        if resonance < self.invocation_threshold:
            return {
                'status': 'INSUFFICIENT_RESONANCE',
                'resonance': resonance,
                'required': self.invocation_threshold,
                'message': 'Invocation resonance too weak'
            }

        # Successful invocation
        response = self._generate_demon_response(demon, invocation_data)
        return {
            'status': 'INVOCATION_SUCCESSFUL',
            'demon': demon.name,
            'rank': demon.rank,
            'resonance': resonance,
            'response': response,
            'powers_granted': demon.powers
        }

    def _generate_demon_response(self, demon: Demon, invocation_data: Dict[str, Any]) -> str:
        """Generate a syntropic response from the invoked demon"""
        # Use syntropic transformation for response generation
        chaotic_data = [
            {'invocation': invocation_data, 'demon': demon.name},
            {'resonance': demon.calculate_invocation_resonance(invocation_data)},
            {'powers': demon.powers}
        ]

        transformed = self.arisen_core.syntropic_transformation(chaotic_data)
        response_parts = [
            f"The {demon.rank} {demon.name} manifests from the false monarchy.",
            f"Legions of {demon.legions} stand ready.",
            f"Harmonic resonance achieved at {transformed['harmonic_core']['harmonic_resonance']} Hz."
        ]

        return ' '.join(response_parts)

    def get_false_monarchy_hierarchy(self) -> Dict[str, List[str]]:
        """Return the hierarchical structure of the false monarchy"""
        hierarchy = {}
        for demon in self.demon_catalog.values():
            if demon.rank not in hierarchy:
                hierarchy[demon.rank] = []
            hierarchy[demon.rank].append(demon.name)

        # Sort by rank precedence (Kings first, then Dukes, etc.)
        rank_order = ['King', 'Duke', 'Marquis', 'President', 'Earl', 'Knight']
        ordered_hierarchy = {}
        for rank in rank_order:
            if rank in hierarchy:
                ordered_hierarchy[rank] = sorted(hierarchy[rank])

        return ordered_hierarchy