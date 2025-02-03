from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum
import math

class Team(Enum):
    BOTTOM = 1
    TOP = 2

@dataclass
class HexCell:
    q: int  # axial coordinate q
    r: int  # axial coordinate r
    team: Optional[Team] = None
    unit: Optional['Unit'] = None  # Forward reference for Unit class

    def __eq__(self, other):
        if not isinstance(other, HexCell):
            return False
        return self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

class Board:
    def __init__(self):
        self.width = 7  # q-axis (columns)
        self.height = 8  # r-axis (rows)
        self.grid: Dict[Tuple[int, int], HexCell] = {}
        self._initialize_grid()

    def _initialize_grid(self):
        """Initialize the hex grid with team assignments"""
        for r in range(self.height):
            for q in range(self.width):
                team = Team.BOTTOM if r < 4 else Team.TOP
                self.grid[(q, r)] = HexCell(q=q, r=r, team=team)

    def is_valid_position(self, q: int, r: int) -> bool:
        """Check if the given coordinates are within the board boundaries"""
        return (q, r) in self.grid

    def get_cell(self, q: int, r: int) -> Optional[HexCell]:
        """Get the cell at the given coordinates"""
        return self.grid.get((q, r))

    def place_unit(self, unit: 'Unit', q: int, r: int) -> bool:
        """Place a unit on the board at the given coordinates"""
        if not self.is_valid_position(q, r):
            return False

        cell = self.grid[(q, r)]
        if cell.unit is not None:
            return False

        cell.unit = unit
        return True

    def remove_unit(self, q: int, r: int) -> Optional['Unit']:
        """Remove a unit from the given position"""
        if not self.is_valid_position(q, r):
            return None

        cell = self.grid[(q, r)]
        unit = cell.unit
        cell.unit = None
        return unit

    def get_neighbors(self, q: int, r: int) -> List[HexCell]:
        """Get all valid neighboring cells for a given position"""
        # Hex directions: (q, r) changes for each of the 6 directions
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        
        neighbors = []
        for dq, dr in directions:
            new_q, new_r = q + dq, r + dr
            if self.is_valid_position(new_q, new_r):
                neighbors.append(self.grid[(new_q, new_r)])
        return neighbors

    def distance(self, q1: int, r1: int, q2: int, r2: int) -> float:
        """Calculate the hex distance between two positions"""
        # Convert axial to cube coordinates
        x1, y1, z1 = q1, r1, -q1-r1
        x2, y2, z2 = q2, r2, -q2-r2
        return max(abs(x1-x2), abs(y1-y2), abs(z1-z2))

    def __str__(self) -> str:
        """Return a string representation of the board"""
        result = []
        for r in range(self.height-1, -1, -1):
            # Add spacing for hex alignment
            if r % 2 == 0:
                result.append(' ')
            
            row = []
            for q in range(self.width):
                cell = self.grid[(q, r)]
                if cell.unit:
                    row.append('U')
                else:
                    row.append(f'{q},{r}')
            result.append('|' + '|'.join(row) + '|')
            
            # Add connecting lines
            if r > 0:
                if r % 2 == 0:
                    result.append(' \\ / \\ / \\ / \\ / \\ / \\ / \\ /')
                else:
                    result.append(' / \\ / \\ / \\ / \\ / \\ / \\ / \\')
        
        return '\n'.join(result)