"""
Agents Prompts Package
======================

エージェント用プロンプト定義
"""

from agents.prompts.problem_discovery import (
    CRITIC_PROMPT,
    FOLLOWUP_QUESTION_PROMPT,
    OUTPUT_SCHEMA,
    SYSTEM_PROMPT,
    get_user_prompt,
)

__all__ = [
    "CRITIC_PROMPT",
    "FOLLOWUP_QUESTION_PROMPT",
    "OUTPUT_SCHEMA",
    "SYSTEM_PROMPT",
    "get_user_prompt",
]
