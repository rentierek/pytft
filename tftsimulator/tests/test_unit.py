import unittest
from tftsimulator.src.core.unit import Unit, DamageType

class TestUnit(unittest.TestCase):
    def setUp(self):
        # Initialize test units before each test
        self.garen = Unit("UNIT_001", star_level=1)  # Garen
        self.ashe = Unit("UNIT_002", star_level=1)   # Ashe

    def test_unit_initialization(self):
        """Test if units are initialized with correct base stats"""
        # Test Garen's base stats
        self.assertEqual(self.garen.name, "Garen")
        self.assertEqual(self.garen.stats.health, 750)
        self.assertEqual(self.garen.stats.attack_damage, 65)
        self.assertEqual(self.garen.stats.armor, 40)
        self.assertEqual(self.garen.stats.magic_resist, 30)
        self.assertEqual(self.garen.stats.range, 1)

    def test_star_level_scaling(self):
        """Test if star level multipliers are applied correctly"""
        garen_2star = Unit("UNIT_001", star_level=2)
        # 2-star should have 1.8x health and 1.5x attack damage
        self.assertAlmostEqual(garen_2star.stats.health, 750 * 1.8)
        self.assertAlmostEqual(garen_2star.stats.attack_damage, 65 * 1.5)

    def test_damage_calculation(self):
        """Test damage calculation with and without critical hits"""
        # Force non-crit for testing base damage
        self.garen.crit_chance = 0
        base_damage = self.garen.calculate_attack_damage()
        self.assertEqual(base_damage, 65)  # Base AD without amplification

        # Test damage amplification
        self.garen.damage_amp = 0.5  # 50% damage amp
        amp_damage = self.garen.calculate_attack_damage()
        self.assertEqual(amp_damage, 98)  # 65 * (1 + 0.5), rounded to nearest integer

    def test_damage_reduction(self):
        """Test damage reduction calculations"""
        # Test physical damage reduction
        physical_damage = 100
        damage_dealt = self.ashe.receive_damage(physical_damage, DamageType.PHYSICAL)
        expected_reduction = 100 / (100 + self.ashe.stats.armor)
        self.assertEqual(damage_dealt, round(physical_damage * expected_reduction))  # Test with rounded value

        # Test magical damage reduction
        magical_damage = 100
        damage_dealt = self.ashe.receive_damage(magical_damage, DamageType.MAGICAL)
        expected_reduction = 100 / (100 + self.ashe.stats.magic_resist)
        self.assertEqual(damage_dealt, round(magical_damage * expected_reduction))  # Test with rounded value

        # Test true damage (no reduction)
        true_damage = 100
        damage_dealt = self.ashe.receive_damage(true_damage, DamageType.TRUE)
        self.assertEqual(damage_dealt, true_damage)

    def test_mana_generation(self):
        """Test mana generation from different sources"""
        # Test mana from attack
        initial_mana = self.garen.current_mana
        self.garen.generate_mana_from_attack()
        self.assertEqual(self.garen.current_mana, initial_mana + 10)

        # Test mana from taking damage
        damage = 100
        pre_damage_mana = self.garen.current_mana
        self.garen.receive_damage(damage, DamageType.PHYSICAL)
        self.assertGreater(self.garen.current_mana, pre_damage_mana)

        # Test mana cap
        self.garen.current_mana = self.garen.stats.max_mana
        self.garen.generate_mana_from_attack()
        self.assertEqual(self.garen.current_mana, self.garen.stats.max_mana)

    def test_durability(self):
        """Test damage reduction from durability"""
        self.garen.durability = 0.3  # 30% damage reduction
        damage = 100
        # Calculate expected damage after armor and durability
        expected_damage = damage * (100 / (100 + self.garen.stats.armor)) * 0.7
        actual_damage = self.garen.receive_damage(damage, DamageType.PHYSICAL)
        self.assertAlmostEqual(actual_damage, expected_damage)

    def test_range_checks(self):
        """Test range-related functionality"""
        # Test melee unit
        self.assertTrue(self.garen.is_melee())
        self.assertTrue(self.garen.is_in_range(1))
        self.assertFalse(self.garen.is_in_range(2))

        # Test ranged unit
        self.assertFalse(self.ashe.is_melee())
        self.assertTrue(self.ashe.is_in_range(4))
        self.assertFalse(self.ashe.is_in_range(5))

if __name__ == '__main__':
    unittest.main()