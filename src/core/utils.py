import logging
import random

from aiogram.types import Message, ReactionTypeEmoji


logger = logging.getLogger(__name__)

REACTION_LIST = ["❤", "🫡", "👍", "👀", "🥴", "🙈", "🍌", "⚡", "🔥", "🏆"]
WEIGHTS = [15, 4, 16, 1, 3, 1, 1, 3, 10, 3]

STREAK_FIRST_DAY_REACTION = ReactionTypeEmoji(emoji="❤️‍🔥")


async def bot_set_reaction(message: Message, reaction: ReactionTypeEmoji | None = None, guaranteed: bool = True):
    if not guaranteed:
        if random.random() < 0.8:
            return
    
    is_big = random.random() < 0.2
    if not reaction:
        reaction = ReactionTypeEmoji(emoji=random.choices(REACTION_LIST, WEIGHTS, k=1)[0])
    logger.info("Set reaction %s to message id=%i", reaction.emoji, message.message_id)
    await message.react(reaction=[reaction], is_big=is_big)
