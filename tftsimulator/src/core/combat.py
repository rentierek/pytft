from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math
from .unit import Unit
from enum import Enum

class MovementState(Enum):
    IDLE = "idle"
    MOVING = "moving"

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def distance_to(self, other: 'Position') -> float:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

class Team:
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.units: Dict[Position, Unit] = {}

    def add_unit(self, unit: Unit, position: Position):
        self.units[position] = unit

    def is_defeated(self) -> bool:
        return len(self.units) == 0

    def get_closest_enemy(self, unit_pos: Position, enemy_team: 'Team') -> tuple[Optional[Position], Optional[Unit]]:
        """Find the closest enemy unit. Optimized to return early when possible."""
        if not enemy_team.units:
            return None, None
        
        closest_distance = float('inf')
        closest_enemy = None
        closest_pos = None

        for enemy_pos, enemy_unit in enemy_team.units.items():
            distance = unit_pos.distance_to(enemy_pos)
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy_unit
                closest_pos = enemy_pos
                # Early exit optimization: if distance is 1, we found the closest possible
                if distance == 1:
                    break

        return closest_pos, closest_enemy

class Combat:
    def __init__(self):
        self.team1 = Team(1)
        self.team2 = Team(2)
        self.combat_time = 45.0  # Total combat time in seconds
        self.overtime_threshold = 30.0  # Time when overtime begins
        self.last_attack_times: Dict[Unit, float] = {}
        self.movement_states: Dict[Unit, Tuple[MovementState, float, Position, Position]] = {}
        self.movement_duration = 0.3  # Time in seconds to move between adjacent hexes
        self.tick_rate = 0.05  # Simulation tick rate in seconds (20 ticks per second)
        # Maintain reverse mapping for O(1) position lookups
        self.unit_positions: Dict[Unit, Position] = {}

    def add_unit(self, unit: Unit, position: Position, team_id: int):
        team = self.team1 if team_id == 1 else self.team2
        team.add_unit(unit, position)
        self.last_attack_times[unit] = 0
        self.unit_positions[unit] = position

    def is_overtime(self, current_time: float) -> bool:
        return current_time >= self.overtime_threshold

    def get_attack_speed_multiplier(self, current_time: float) -> float:
        return 2.0 if self.is_overtime(current_time) else 1.0

    def get_damage_multiplier(self, current_time: float) -> float:
        return 2.0 if self.is_overtime(current_time) else 1.0

    def start_movement(self, unit: Unit, current_pos: Position, target_pos: Position, current_time: float) -> bool:
        if unit in self.movement_states and self.movement_states[unit][0] == MovementState.MOVING:
            return False
        
        self.movement_states[unit] = (MovementState.MOVING, current_time, current_pos, target_pos)
        return True

    def update_unit_position(self, unit: Unit, current_time: float) -> Optional[Position]:
        if unit not in self.movement_states:
            return None

        state, start_time, start_pos, target_pos = self.movement_states[unit]
        if state != MovementState.MOVING:
            return None

        elapsed_time = current_time - start_time
        if elapsed_time >= self.movement_duration:
            self.movement_states[unit] = (MovementState.IDLE, current_time, target_pos, target_pos)
            return target_pos

        return None

    def process_unit_combat(self, unit: Unit, unit_pos: Position, current_team: Team, 
                          enemy_team: Team, current_time: float) -> None:
        # Skip combat if unit is moving
        if unit in self.movement_states and self.movement_states[unit][0] == MovementState.MOVING:
            return

        # Find closest enemy
        enemy_pos, enemy = current_team.get_closest_enemy(unit_pos, enemy_team)
        if not enemy or not enemy_pos:
            return

        # Check if enemy is in range
        distance = unit_pos.distance_to(enemy_pos)
        if not unit.is_in_range(distance):
            # If not in range, try to move towards the enemy
            dx = enemy_pos.x - unit_pos.x
            dy = enemy_pos.y - unit_pos.y
            # Move in the direction of the enemy
            new_x = unit_pos.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            new_y = unit_pos.y + (1 if dy > 0 else -1 if dy < 0 else 0)
            new_pos = Position(new_x, new_y)
            
            # Start movement if possible
            if self.start_movement(unit, unit_pos, new_pos, current_time):
                # Update unit position in team and position mapping
                current_team.units.pop(unit_pos)
                current_team.units[new_pos] = unit
                self.unit_positions[unit] = new_pos
                # Print movement information
                print(f"[{current_time:.1f}s] {unit.name} moving from ({unit_pos.x},{unit_pos.y}) to ({new_pos.x},{new_pos.y})")
            return

        # Check if enough time has passed since last attack
        attack_interval = unit.get_attack_interval() / self.get_attack_speed_multiplier(current_time)
        if current_time - self.last_attack_times.get(unit, 0) < attack_interval:
            return

        # Perform attack
        damage = unit.calculate_attack_damage() * self.get_damage_multiplier(current_time)
        is_crit = damage > unit.stats.attack_damage * (1 + unit.damage_amp)
        actual_damage = enemy.receive_damage(damage, unit.damage_type)
        unit.generate_mana_from_attack()
        self.last_attack_times[unit] = current_time

        # Print combat information with critical hit indicator
        crit_indicator = "(CRIT!)" if is_crit else ""
        print(f"[{current_time:.1f}s] {unit.name} attacks {enemy.name} for {actual_damage} damage {crit_indicator}")
        print(f"    {enemy.name}'s health: {enemy.current_health}/{enemy.stats.health}")

        # Check for overtime
        if self.is_overtime(current_time) and current_time - self.overtime_threshold < 0.1:
            print(f"\n[{current_time:.1f}s] OVERTIME! Attack speed and damage doubled!\n")

        # Remove dead units and announce death
        if enemy.current_health <= 0:
            enemy_team.units.pop(enemy_pos)
            # Remove from position mapping as well
            if enemy in self.unit_positions:
                del self.unit_positions[enemy]
            print(f"    {enemy.name} has been defeated!")


    def simulate_combat(self) -> Optional[int]:
        """Simulate combat using tick-based system for better performance"""
        current_time = 0.0
        
        while current_time < self.combat_time:
            # Update unit positions for moving units
            for unit in list(self.movement_states.keys()):
                new_pos = self.update_unit_position(unit, current_time)
                if new_pos:
                    # Update unit position using cached position mapping
                    team = self.team1 if unit in self.team1.units.values() else self.team2
                    old_pos = self.unit_positions[unit]  # O(1) lookup instead of iteration
                    team.units.pop(old_pos)
                    team.units[new_pos] = unit
                    self.unit_positions[unit] = new_pos

            # Process team 1 - avoid creating dict copy by using list of items
            for unit_pos, unit in list(self.team1.units.items()):
                self.process_unit_combat(unit, unit_pos, self.team1, self.team2, current_time)

            # Process team 2 - avoid creating dict copy by using list of items
            for unit_pos, unit in list(self.team2.units.items()):
                self.process_unit_combat(unit, unit_pos, self.team2, self.team1, current_time)

            # Check win conditions
            if self.team2.is_defeated():
                return 1  # Team 1 wins
            if self.team1.is_defeated():
                return 2  # Team 2 wins
            
            # Advance simulation by one tick
            current_time += self.tick_rate
        
        return None  # Draw if time runs out