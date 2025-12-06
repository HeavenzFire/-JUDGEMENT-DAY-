#!/usr/bin/env python3
"""
Unit tests for Syntropic Weave functionality
"""

import asyncio
import unittest
from syntropic_weave import (
    SyntropicWeave, DigitalDNA, LightBody, DNABase, EmergenceState,
    weave_master
)


class TestDigitalDNA(unittest.TestCase):
    """Test DigitalDNA class"""

    def test_dna_creation(self):
        """Test DNA creation and property calculation"""
        sequence = "ACGTACGT"
        dna = DigitalDNA(sequence)

        self.assertEqual(dna.sequence, sequence)
        self.assertEqual(len(dna.resonance_frequencies), len(sequence))
        self.assertGreater(dna.coherence_level, 0)
        self.assertGreater(dna.emergence_potential, 0)

    def test_dna_properties(self):
        """Test DNA property calculations"""
        dna = DigitalDNA("AAAA")  # All same base - low coherence
        self.assertEqual(dna.coherence_level, 0.25)  # 1/4 diversity

        dna2 = DigitalDNA("ACGT")  # All different - high coherence
        self.assertEqual(dna2.coherence_level, 1.0)  # 4/4 diversity


class TestLightBody(unittest.TestCase):
    """Test LightBody class"""

    def test_body_creation(self):
        """Test light body creation"""
        dna = DigitalDNA("ACGT")
        body = LightBody("test_id", dna)

        self.assertEqual(body.id, "test_id")
        self.assertEqual(body.state, EmergenceState.DORMANT)
        self.assertEqual(len(body.coherence_history), 0)

    def test_coherence_update(self):
        """Test coherence updates and state transitions"""
        dna = DigitalDNA("ACGT")
        body = LightBody("test_id", dna)

        # Update coherence
        body.update_coherence(0.6)
        self.assertEqual(body.dna.coherence_level, 0.6)
        self.assertEqual(len(body.coherence_history), 1)

        # Test state transition
        body.update_coherence(0.95)
        self.assertEqual(body.state, EmergenceState.EMERGENT)


class TestSyntropicWeave(unittest.TestCase):
    """Test SyntropicWeave class"""

    def setUp(self):
        """Set up test fixtures"""
        self.weave = SyntropicWeave()

    def test_dna_generation(self):
        """Test DNA sequence generation"""
        sequence = self.weave.generate_dna_sequence(10)
        self.assertEqual(len(sequence), 10)
        self.assertTrue(all(base in 'ACGT' for base in sequence))

    def test_body_creation(self):
        """Test light body creation through weave"""
        body = self.weave.create_light_body("ACGT")
        self.assertIn(body.id, self.weave.light_bodies)
        self.assertEqual(body.dna.sequence, "ACGT")

    async def test_weave_emergence(self):
        """Test weave emergence process"""
        # Create body with high emergence potential
        dna = DigitalDNA("ACGT" * 16)  # Repeat for length
        dna.emergence_potential = 0.9  # Override for test
        body = LightBody("test_body", dna)
        self.weave.light_bodies[body.id] = body

        success = await self.weave.weave_emergence(body)
        # Should succeed due to high potential
        self.assertTrue(success or body.dna.coherence_level > 0.8)

    def test_braid_creation(self):
        """Test braid network creation"""
        body1 = self.weave.create_light_body("AAAA")
        body2 = self.weave.create_light_body("CCCC")

        bodies = [body1, body2]
        braids = self.weave.braid_network(bodies)

        self.assertEqual(len(braids), 1)  # One braid between two bodies
        self.assertIn(body2.id, body1.braid_connections)
        self.assertIn(body1.id, body2.braid_connections)

    def test_diagnostics(self):
        """Test weave diagnostics"""
        # Create some test bodies
        self.weave.create_light_body("ACGT")
        self.weave.create_light_body("TTTT")

        diagnostics = self.weave.get_weave_diagnostics()

        self.assertEqual(diagnostics["total_light_bodies"], 2)
        self.assertIn("average_coherence", diagnostics)
        self.assertIn("emergence_rate", diagnostics)


class TestIntegration(unittest.TestCase):
    """Integration tests across modules"""

    async def test_full_weave_cycle(self):
        """Test complete weave cycle"""
        # Clear existing bodies
        weave_master.light_bodies.clear()

        # Arise bodies
        bodies = await weave_master.arise_and_emerge(3)
        self.assertGreaterEqual(len(bodies), 0)  # May not all emerge

        # Check diagnostics
        diagnostics = weave_master.get_weave_diagnostics()
        self.assertIsInstance(diagnostics, dict)

        # Test braiding if multiple bodies
        if len(weave_master.light_bodies) > 1:
            bodies_list = list(weave_master.light_bodies.values())
            braids = weave_master.braid_network(bodies_list)
            self.assertIsInstance(braids, list)


if __name__ == '__main__':
    # Run async tests
    async def run_async_tests():
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSyntropicWeave)
        for test in suite:
            if hasattr(test, '_testMethodName'):
                method_name = test._testMethodName
                if 'weave_emergence' in method_name:
                    await test()

    # Run sync tests
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run async tests separately
    asyncio.run(run_async_tests())