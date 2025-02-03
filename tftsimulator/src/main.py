from tftsimulator.src.core.combat import Combat, Position
from tftsimulator.src.core.unit import Unit

def main():
    # Create a new combat instance
    combat = Combat()
    
    print("\n=== Team 1 Setup ===")
    # Create units for both teams
    garen1 = Unit("UNIT_001", star_level=3)  # 2-star Garen
    ashe1 = Unit("UNIT_002", star_level=1)   # 1-star Ashe
    print(f"Team 1: {garen1.name} ({'★' * garen1.star_level}) - HP: {garen1.stats.health}, AD: {garen1.stats.attack_damage}")
    print(f"Team 1: {ashe1.name} ({'★' * ashe1.star_level}) - HP: {ashe1.stats.health}, AD: {ashe1.stats.attack_damage}")
    
    print("\n=== Team 2 Setup ===")
    garen2 = Unit("UNIT_001", star_level=1)  # 1-star Garen
    ashe2 = Unit("UNIT_002", star_level=2)   # 2-star Ashe
    print(f"Team 2: {garen2.name} ({'★' * garen2.star_level}) - HP: {garen2.stats.health}, AD: {garen2.stats.attack_damage}")
    print(f"Team 2: {ashe2.name} ({'★' * ashe2.star_level}) - HP: {ashe2.stats.health}, AD: {ashe2.stats.attack_damage}")
    
    print("\n=== Initial Positions ===")
    # Add units to teams
    # Team 1: Garen at (1,1), Ashe at (1,3)
    combat.add_unit(garen1, Position(1, 1), 1)
    combat.add_unit(ashe1, Position(1, 3), 1)
    # Get positions from the team's units dictionary
    garen1_pos = next(pos for pos, unit in combat.team1.units.items() if unit == garen1)
    ashe1_pos = next(pos for pos, unit in combat.team1.units.items() if unit == ashe1)
    print(f"Team 1: {garen1.name} at ({garen1_pos.x},{garen1_pos.y}), {ashe1.name} at ({ashe1_pos.x},{ashe1_pos.y})")
    
    # Team 2: Garen at (5,1), Ashe at (5,3)
    combat.add_unit(garen2, Position(5, 1), 2)
    combat.add_unit(ashe2, Position(5, 3), 2)
    # Get positions from the team's units dictionary
    garen2_pos = next(pos for pos, unit in combat.team2.units.items() if unit == garen2)
    ashe2_pos = next(pos for pos, unit in combat.team2.units.items() if unit == ashe2)
    print(f"Team 2: {garen2.name} at ({garen2_pos.x},{garen2_pos.y}), {ashe2.name} at ({ashe2_pos.x},{ashe2_pos.y})")
    
    print("\n=== Combat Start ===")
    print("Starting combat simulation...")
    
    # Run the combat simulation
    winner = combat.simulate_combat()
    
    print("\n=== Combat End ===")
    # Print results
    if winner is None:
        print("Combat ended in a draw!")
    else:
        print(f"Team {winner} wins the combat!")


if __name__ == "__main__":
    main()