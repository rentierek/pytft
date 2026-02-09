from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import math
import json
import os
import random

class DamageType(Enum):
    PHYSICAL = "physical"
    MAGICAL = "magical"
    TRUE = "true"

# Cache for unit data to avoid repeated file I/O
# Note: This cache is not thread-safe. The simulator is designed for single-threaded use.
_UNIT_DATA_CACHE: Optional[Dict] = None

@dataclass
class UnitStats:
    health: float
    attack_damage: float
    armor: float
    magic_resist: float
    attack_speed: float
    starting_mana: float
    max_mana: float
    range: int

class Unit:
    def __init__(self, unit_id: str, star_level: int = 1):
        self.unit_id = unit_id
        self.star_level = max(0, min(4, star_level))  # Clamp between 0 and 4 stars
        self.durability = 0.0  # Always starts at 0%
        self.damage_amp = 0.0  # Damage amplification starts at 0%
        self.current_mana = 0
        self.current_health = 0
        self.ability_power = 100.0  # Base ability power is 100
        self.crit_chance = 0.25  # 25% base crit chance
        self.crit_multiplier = 1.4  # 40% increased damage on crit
        self.damage_type = DamageType.PHYSICAL  # Default damage type
        self._load_unit_data()

    def _load_unit_data(self):
        global _UNIT_DATA_CACHE
        
        # Load unit data from cache or file
        if _UNIT_DATA_CACHE is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, '..', '..', 'data', 'units', 'units.json')
            
            with open(json_path, 'r') as f:
                _UNIT_DATA_CACHE = json.load(f)
        
        units_data = _UNIT_DATA_CACHE
            
        if self.unit_id not in units_data:
            raise ValueError(f"Unit ID {self.unit_id} not found in units data")
            
        unit_data = units_data[self.unit_id]
        self.name = unit_data['name']
        self.cost = unit_data['cost']
        self.traits = unit_data['traits']
        self.ability = unit_data['ability']
        
        # Load stats
        stats = unit_data['stats']
        base_health = stats['health']
        base_attack_damage = stats['attack_damage']

        # Apply star level multipliers
        if self.star_level == 0:
            base_health *= 0.7
            base_attack_damage *= 0.7
        else:
            # Apply multipliers for stars 2-4 (1.8x health and 1.5x AD per level above 1)
            for _ in range(1, self.star_level):
                base_health *= 1.8
                base_attack_damage *= 1.5

        self.stats = UnitStats(
            health=base_health,
            attack_damage=base_attack_damage,
            armor=stats['armor'],
            magic_resist=stats['magic_resist'],
            attack_speed=stats['attack_speed'],
            starting_mana=stats['starting_mana'],
            max_mana=stats['max_mana'],
            range=stats['range']
        )
        self.current_health = self.stats.health
        self.current_mana = self.stats.starting_mana

    def calculate_damage_reduction(self, resistance: float) -> float:
        """Calculate damage reduction based on armor or magic resist"""
        return round(100 / (100 + max(0, resistance)), 3)  # Ensure resistance is not negative

    def calculate_attack_damage(self) -> float:
        """Calculate final attack damage with amplification and potential crit"""
        base_damage = self.stats.attack_damage * (1 + self.damage_amp)
        if random.random() < self.crit_chance:
            base_damage *= self.crit_multiplier
        return round(base_damage)  # Round the final damage

    def receive_damage(self, damage: float, damage_type: DamageType) -> float:
        """Process incoming damage and return the actual damage dealt"""
        pre_mitigation_damage = round(damage)

        if damage_type == DamageType.TRUE:
            actual_damage = pre_mitigation_damage
        else:
            resistance = self.stats.armor if damage_type == DamageType.PHYSICAL else self.stats.magic_resist
            damage_reduction = self.calculate_damage_reduction(resistance)
            actual_damage = round(pre_mitigation_damage * damage_reduction * (1 - self.durability))
            self.generate_mana_from_damage(pre_mitigation_damage, actual_damage)

        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage

    def generate_mana_from_damage(self, pre_mitigation_damage: float, post_mitigation_damage: float):
        """Generate mana from receiving damage"""
        # Calculate mana gain based on damage (1% of pre-mitigation + 7% of post-mitigation)
        mana_gain = (0.01 * pre_mitigation_damage) + (0.07 * post_mitigation_damage)
        # Cap mana gain at 42.5
        mana_gain = min(42.5, mana_gain)
        self.gain_mana(mana_gain)

    def generate_mana_from_attack(self):
        """Generate mana from performing an attack"""
        self.gain_mana(10)  # 10 mana per attack

    def gain_mana(self, amount: float):
        """Add mana to the unit, capped at max_mana"""
        self.current_mana = min(self.stats.max_mana, self.current_mana + amount)

    def is_in_range(self, distance: float) -> bool:
        """Check if a target is within attack range"""
        return distance <= self.stats.range

    def get_attack_interval(self) -> float:
        """Get the time interval between attacks based on attack speed"""
        return 1.0 / self.stats.attack_speed

    def is_melee(self) -> bool:
        """Check if the unit is a melee unit"""
        return self.stats.range == 1