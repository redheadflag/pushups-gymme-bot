import logging
import random

from aiogram.types import Message, ReactionTypeEmoji


logger = logging.getLogger(__name__)

REACTION_LIST = ["❤", "🫡", "👍", "👀", "🥴", "🙉", "🙈", "🤓", "🍌", "⚡"]

STREAK_FIRST_DAY_REACTION = ReactionTypeEmoji(emoji="❤️‍🔥")


async def bot_set_reaction(message: Message, emoji: ReactionTypeEmoji | None = None, guaranteed: bool = True):
    if not guaranteed:
        if random.random() < 0.8:
            return
    
    is_big = random.random() < 0.2
    reaction = emoji or ReactionTypeEmoji(emoji=random.choice(REACTION_LIST))
    logger.info("Set reaction %s to message id=%i", reaction.emoji, message.message_id)
    await message.react(reaction=[reaction], is_big=is_big)
