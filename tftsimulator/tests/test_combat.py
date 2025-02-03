import pytest
from tftsimulator.src.core.combat import Combat, Team, Position, MovementState
from tftsimulator.src.core.unit import Unit, DamageType
import time

@pytest.fixture
def combat():
    return Combat()

@pytest.fixture
def basic_unit():
    unit = Unit("test_unit", star_level=1)
    unit.damage_type = DamageType.PHYSICAL
    return unit

def test_combat_initialization(combat):
    assert combat.combat_time == 45.0
    assert combat.overtime_threshold == 30.0
    assert combat.movement_duration == 0.3
    assert isinstance(combat.team1, Team)
    assert isinstance(combat.team2, Team)

def test_unit_placement(combat, basic_unit):
    pos = Position(1, 1)
    combat.add_unit(basic_unit, pos, 1)
    assert basic_unit in combat.last_attack_times
    assert combat.last_attack_times[basic_unit] == 0
    assert combat.team1.units[pos] == basic_unit

def test_movement_mechanics(combat, basic_unit):
    start_pos = Position(0, 0)
    target_pos = Position(1, 1)
    current_time = 0.0
    
    # Test movement initiation
    combat.add_unit(basic_unit, start_pos, 1)
    assert combat.start_movement(basic_unit, start_pos, target_pos, current_time)
    
    # Test unit state during movement
    state = combat.movement_states[basic_unit]
    assert state[0] == MovementState.MOVING
    assert state[2] == start_pos
    assert state[3] == target_pos
    
    # Test movement completion
    current_time += combat.movement_duration
    new_pos = combat.update_unit_position(basic_unit, current_time)
    assert new_pos == target_pos
    assert combat.movement_states[basic_unit][0] == MovementState.IDLE

def test_overtime_mechanics(combat):
    assert not combat.is_overtime(29.9)
    assert combat.is_overtime(30.0)
    assert combat.get_attack_speed_multiplier(29.9) == 1.0
    assert combat.get_attack_speed_multiplier(30.0) == 2.0
    assert combat.get_damage_multiplier(29.9) == 1.0
    assert combat.get_damage_multiplier(30.0) == 2.0

def test_combat_resolution(combat):
    unit1 = Unit("test_unit_1", star_level=1)
    unit2 = Unit("test_unit_2", star_level=1)
    unit1.damage_type = DamageType.PHYSICAL
    unit2.damage_type = DamageType.PHYSICAL
    
    # Position units within attack range
    pos1 = Position(0, 0)
    pos2 = Position(1, 0)
    combat.add_unit(unit1, pos1, 1)
    combat.add_unit(unit2, pos2, 2)
    
    # Process combat
    combat.process_unit_combat(unit1, pos1, combat.team1, combat.team2, 0.0)
    
    # Verify damage was dealt
    assert unit2.current_health < unit2.stats.health
    
    # Test unit death and team defeat
    unit2.current_health = 0
    combat.process_unit_combat(unit1, pos1, combat.team1, combat.team2, 1.0)
    assert combat.team2.is_defeated()

def test_full_combat_simulation(combat):
    # Setup two units
    unit1 = Unit("test_unit_1", star_level=1)
    unit2 = Unit("test_unit_2", star_level=1)
    unit1.damage_type = DamageType.PHYSICAL
    unit2.damage_type = DamageType.PHYSICAL
    
    # Position units
    combat.add_unit(unit1, Position(0, 0), 1)
    combat.add_unit(unit2, Position(1, 0), 2)
    
    # Simulate combat
    result = combat.simulate_combat()
    
    # Verify result is valid
    assert result in [None, 1, 2]  # Draw, Team 1 wins, or Team 2 wins