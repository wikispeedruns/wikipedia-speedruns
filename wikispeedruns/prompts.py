
from typing import List, TypedDict, Optional

import datetime

class Prompt(TypedDict, total=False):
    prompt_id: int
    start: str
    end: str

    active_start: datetime.datetime
    active_end: datetime.datetime

    currentlyRated: bool
    played: bool # TODO

def add_prompt(start: str, end: str) -> Optional[int]:
    ''' 
    Add a prompt
    '''
    pass

def set_ranked_daily_prompt(id: int, day: datetime.date) -> bool:
    '''
    Given a currently unused prompt, set it as one of the weekly prompts for the week of 'day'
    '''
    pass


def set_weekly_prompts(id: int, day: datetime.date) -> bool:
    '''
    Given a currently unused prompt, set it as one of the weekly prompts for the week of 'day'
    '''
    pass


def get_prompt(prompt_id: int, user_id: Optional[int]) -> Prompt:
    ''' 
    Get a specific prompt, while checking for whether its available and if it's been played
    '''
    pass


def get_active_prompts(user_id: Optional[int]) -> List[Prompt]:
    '''
    Get all prompts for display on front page (only show start)
    '''
    pass

def get_archive_prompts(user_id: Optional[int]) -> List[Prompt]:
    '''
    Get all prompts for archive, including currently active, ideally paginated
    '''
    pass

def get_managed_prompts() -> List[Prompt]:
    '''
    Get all prompts for admins, all active, unused, and upcoming prompts
    '''
    pass