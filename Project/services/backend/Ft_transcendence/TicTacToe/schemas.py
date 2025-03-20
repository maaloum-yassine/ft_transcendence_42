from pydantic import BaseModel, Field, validator
from typing import Optional

class TicTacToeGameSchema(BaseModel):
    id: int
    player_x: Optional[str] = None  # Display username instead of ID
    player_o: Optional[str] = None  # Allow None for Player O
    board_state: str
    current_turn: Optional[str] = None
    winner: Optional[str] = None  # Allow None for Winner

    class Config:
        from_attributes = True  # This allows Pydantic to work with ORM models directly

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            player_x=obj.player_x.username if obj.player_x else None,
            player_o=obj.player_o.username if obj.player_o else None,
            board_state=obj.board_state,
            current_turn=obj.current_turn,
            winner=obj.winner if obj.winner else None,
        )

    # Coerce None to empty string for optional fields
    @validator('player_o', always=True)
    def coerce_none_to_empty(cls, v):
        return v or ''

    @validator('winner', always=True)
    def coerce_none_to_empty_winner(cls, v):
        return v or ''

    
class GameResponseSchema(BaseModel):
    id: int
    player_x: str  # Expecting an integer (user ID)
    player_o: Optional[str]  # Expecting an integer (user ID)
    board_state: str
    winner: Optional[str]
    status: str  # or any appropriate type

    class Config:
        from_attributes = True  # This allows Pydantic to work with ORM models directly


class TicTacToeJoinGame(BaseModel):
    player_o: int
    room_id: int

class TicTacToeGameCreateSchema(BaseModel):
    player_x: Optional[int] = None  # Use int for user IDs (not needed for PUT)
    player_o: Optional[int] = None  # Use int for user IDs (not needed for PUT)
    board_state: str = Field(..., min_length=9, max_length=9, pattern=r'^[XO-]{9}$')
    current_turn: str = Field(..., pattern='^[XO]$')
    winner: Optional[str] = None

    @validator('board_state')
    def validate_board_state(cls, v):
        if len(v) != 9 or any(c not in 'XO-' for c in v):
            raise ValueError('Invalid board state')
        return v

    class Config:
        from_attributes = True
