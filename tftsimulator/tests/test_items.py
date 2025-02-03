import pytest
from tftsimulator.src.core.item import Item
from tftsimulator.src.core.unit import Unit

@pytest.fixture
def basic_unit():
    return Unit("test_unit", star_level=1)

@pytest.fixture
def giants_belt():
    return Item("ITEM_001")

@pytest.fixture
def bf_sword():
    return Item("ITEM_002")

@pytest.fixture
def warmogs():
    return Item("ITEM_007")

def test_basic_item_stats(basic_unit, giants_belt):
    # Test applying a single basic item
    Item.apply_stats_to_unit(basic_unit, [giants_belt])
    assert basic_unit.stats.health == 800  # Base 600 + 200 from Giant's Belt

def test_percentage_stats(basic_unit, warmogs):
    # Test items with percentage-based stats
    initial_health = basic_unit.stats.health
    Item.apply_stats_to_unit(basic_unit, [warmogs])
    expected_health = (initial_health + 400) * 1.1  # Flat 400 + 10% increase
    assert basic_unit.stats.health == expected_health

def test_multiple_items(basic_unit, giants_belt, bf_sword):
    # Test applying multiple different items
    Item.apply_stats_to_unit(basic_unit, [giants_belt, bf_sword])
    assert basic_unit.stats.health == 800  # Base 600 + 200
    assert basic_unit.stats.attack_damage == 72  # Base 60 * (1 + 0.2)

def test_unique_item_restriction(basic_unit, warmogs):
    # Test that unique items cannot be duplicated
    with pytest.raises(ValueError, match="Cannot equip multiple unique items"):
        Item.apply_stats_to_unit(basic_unit, [warmogs, warmogs])

def test_current_health_scaling(basic_unit, giants_belt):
    # Test that current health scales properly with max health changes
    basic_unit.current_health = 300  # Set to half health
    Item.apply_stats_to_unit(basic_unit, [giants_belt])
    assert basic_unit.current_health == 400  # Should maintain the same ratio

def test_attack_speed_cap(basic_unit):
    # Test that attack speed cannot exceed the cap of 5.0
    recurve_bow = Item("ITEM_006")
    # Apply multiple attack speed items
    items = [recurve_bow] * 10
    Item.apply_stats_to_unit(basic_unit, items)
    assert basic_unit.stats.attack_speed <= 5.0

def test_crit_conversion(basic_unit):
    # Test that excess crit chance converts to crit damage
    glove = Item("ITEM_003")  # Using a basic crit chance item
    initial_crit_multiplier = basic_unit.crit_multiplier
    # Each glove gives 25% crit chance, so we need 4 gloves to reach 100%
    Item.apply_stats_to_unit(basic_unit, [glove, glove, glove, glove, glove])
    assert basic_unit.crit_chance == 1.0  # Should be capped at 100%
    assert basic_unit.crit_multiplier > initial_crit_multiplier  # Should have increased