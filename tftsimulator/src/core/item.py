from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import os
from enum import Enum

@dataclass
class ItemStats:
    hp: float = 0
    hp_percent: float = 0
    ad: float = 0
    ap: float = 0
    armor: float = 0
    magic_resist: float = 0
    attack_speed: float = 0
    mana: float = 0
    crit_chance: float = 0
    crit_damage: float = 0
    damage_amp: float = 0
    omnivamp: float = 0
    durability: float = 0

class Item:
    def __init__(self, item_id: str):
        self.item_id = item_id
        self._load_item_data()

    def _load_item_data(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, '..', '..', 'data', 'items', 'items.json')
        
        with open(json_path, 'r') as f:
            items_data = json.load(f)
            
        if self.item_id not in items_data:
            raise ValueError(f"Item ID {self.item_id} not found in items data")
            
        item_data = items_data[self.item_id]
        self.name = item_data['name']
        self.category = item_data['category']
        self.description = item_data['description']
        self.components = item_data['components']
        self.is_unique = item_data['is_unique']
        self.effects = item_data['effects']
        
        # Initialize stats
        self.stats = ItemStats()
        for stat, value in item_data['stats'].items():
            setattr(self.stats, stat, value)

    @staticmethod
    def apply_stats_to_unit(unit, items: List['Item']):
        """Apply stats from items to a unit"""
        # Verify unique item restriction
        unique_items = set()
        for item in items:
            if item.is_unique and item.item_id in unique_items:
                raise ValueError(f"Cannot equip multiple unique items: {item.name}")
            if item.is_unique:
                unique_items.add(item.item_id)

        # Calculate base stats first
        total_stats = ItemStats()
        for item in items:
            for stat_name, stat_value in vars(item.stats).items():
                current_value = getattr(total_stats, stat_name)
                setattr(total_stats, stat_name, current_value + stat_value)

        # Store initial health ratio before applying stats
        if unit.current_health > 0:  # Only update if unit is alive
            initial_health_ratio = unit.current_health / unit.stats.health

        # Apply flat HP first
        unit.stats.health += total_stats.hp

        # Apply HP percent to the base health only
        if total_stats.hp_percent > 0:
            unit.stats.health *= (1 + total_stats.hp_percent / 100)

        # Update current health proportionally
        if unit.current_health > 0:  # Only update if unit is alive
            unit.current_health = unit.stats.health * initial_health_ratio

        # Apply AD (percentage based on base AD)
        if total_stats.ad > 0:
            unit.stats.attack_damage *= (1 + total_stats.ad / 100)

        # Apply armor and magic resist
        unit.stats.armor += total_stats.armor
        unit.stats.magic_resist += total_stats.magic_resist

        # Apply attack speed with cap
        if total_stats.attack_speed > 0:
            new_attack_speed = unit.stats.attack_speed * (1 + total_stats.attack_speed / 100)
            unit.stats.attack_speed = min(5.0, new_attack_speed)

        # Apply ability power
        unit.ability_power += total_stats.ap

        # Calculate total crit chance from base and items
        total_crit = unit.crit_chance + total_stats.crit_chance / 100  # Convert item crit chance to decimal

        # Cap crit chance at 1.0 (100%) and convert excess to crit damage
        if total_crit > 1.0:
            excess_crit = total_crit - 1.0
            unit.crit_multiplier += excess_crit * 0.5  # Convert excess crit to damage (1:2 ratio)
            total_crit = 1.0

        unit.crit_chance = total_crit

        # Apply damage amplification
        unit.damage_amp += total_stats.damage_amp / 100

        # Apply omnivamp
        if hasattr(unit, 'omnivamp'):
            unit.omnivamp = total_stats.omnivamp / 100

        # Apply durability (multiplicative)
        if total_stats.durability > 0:
            for item in items:
                if item.stats.durability > 0:
                    unit.durability = 1 - ((1 - unit.durability) * (1 - item.stats.durability / 100))

        # Update current health to match new max health
        if unit.current_health > 0:  # Only update if unit is alive
            health_ratio = unit.current_health / unit.stats.health
            unit.current_health = unit.stats.health * health_ratio