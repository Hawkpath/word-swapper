import logging
import sys
from typing import cast

import discord
import discord.ext.commands as commands

from .generator import make_pun

logger = logging.getLogger('musician_pun.bot')


# noinspection PyMethodMayBeStatic
class Bot(commands.Bot):

    def __init__(self, *args, max_messages=None, **kwargs):
        super().__init__(*args, max_messages=max_messages, **kwargs)
        self.add_cog(Cog(self))

    async def on_connect(self):
        logger.info('Client connected')

    async def on_disconnect(self):
        logger.info('Client disconnected')

    async def on_resumed(self):
        logger.info('Session resumed')

    async def on_ready(self):
        logger.info('Client started')

    async def on_error(self, event_method: str, *args, **kwargs):
        exc_type, exc, tb = sys.exc_info()

        if exc_type is discord.HTTPException:
            logger.warning('HTTP exception', exc_info=True)

        elif exc_type is discord.Forbidden:
            logger.warning('Forbidden request', exc_info=True)

        elif event_method == 'on_message':
            msg: discord.Message = args[0]
            logger.error(
                f'Unhandled in on_message (content: {msg.content!r} '
                f'author: {msg.author} channel: {msg.channel})',
                exc_info=True
            )

        elif exc_type is KeyboardInterrupt:
            await self.close()

        else:
            logger.error(
                f"Unhandled in {event_method} (args: {args} kwargs: {kwargs})",
                exc_info=True
            )

    async def on_command_error(self, ctx: commands.Context, exception):
        logger.error("Unhandled exception", exc_info=exception)


class Cog(commands.Cog):

    REROLL_EMOJI = '🎲'

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command('pun')
    async def pun(self, ctx: commands.Context, *, phrase: str):
        pun = make_pun(phrase)
        if pun is None:
            pun = "Failed to generate anything"
        await cast(discord.Message, ctx.message).add_reaction(self.REROLL_EMOJI)
        await ctx.send(pun)

    @commands.Cog.listener('on_raw_reaction_add')
    async def reroll(self, react: discord.RawReactionActionEvent):
        if react.user_id == self.bot.user.id:
            return

        emoji: discord.PartialEmoji = react.emoji
        if emoji.name != self.REROLL_EMOJI:
            return

        logger.info(f"Rerolling message")
        chan: discord.TextChannel = self.bot.get_channel(react.channel_id)
        msg: discord.Message = await chan.fetch_message(react.message_id)

        await msg.remove_reaction(emoji.name, react.member)
        await self.bot.process_commands(msg)


def main():
    import json
    from pathlib import Path

    config = Path(__file__, '../config.json')

    with config.open() as f:
        bot_token = json.load(f)['bot_token']

    bot = Bot('$')
    bot.run(bot_token)
