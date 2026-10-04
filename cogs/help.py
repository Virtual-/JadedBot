import discord
from discord.ext import commands


# display name : (emoji, [cog qualified names that belong to this category])
CATEGORY_META = {
    "Music":      ("\N{MUSICAL NOTE}",          ["Music"]),
    "Soundboard": ("\N{SPEAKER WITH THREE SOUND WAVES}", ["Sounds"]),
    "Reactions":  ("\N{FRAME WITH PICTURE}",     ["Reactions"]),
    "Search":     ("\N{RIGHT-POINTING MAGNIFYING GLASS}", ["WikiSearch", "WoW"]),
    "Monsters & Memories": ("\N{DRAGON FACE}",   ["Monsters"]),
    "Bot":        ("\N{GEAR}",                   ["HelpCog", None]),
}

CATEGORY_ORDER = ["Music", "Soundboard", "Reactions", "Search", "Monsters & Memories", "Bot"]

# reverse lookup: cog qualified name -> category display name
COG_TO_CATEGORY = {}
for _disp, (_emoji, _cogs) in CATEGORY_META.items():
    for _c in _cogs:
        COG_TO_CATEGORY[_c] = _disp

# extra words accepted as `!help <category>` that aren't a cog name
CATEGORY_ALIASES = {
    "sounds": "Soundboard",
    "soundboard": "Soundboard",
    "search": "Search",
    "misc": "Bot",
}


def _clean_doc(text):
    """Strip a leading `!cmd - ` prefix from an existing docstring.

    Only looks at the first line - a docstring can have further lines (e.g. a
    bulleted usage list) that legitimately contain " - " of their own, and
    those must survive untouched rather than being swallowed by a global split.
    """
    if not text:
        return ""
    lines = text.strip().split("\n")
    first = lines[0]
    lines[0] = first.split(" - ", 1)[1].strip() if " - " in first else first.strip()
    return "\n".join(lines)


class JadedHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            "help": "Shows this menu. !help <command> or !help <category> for more.",
            "brief": "Show the command list",
        })

    # ---- helpers -------------------------------------------------------------

    def _category_of(self, cog):
        name = cog.qualified_name if cog is not None else None
        return COG_TO_CATEGORY.get(name, name or "Bot")

    def _emoji_of(self, disp):
        return CATEGORY_META.get(disp, ("\N{SMALL BLUE DIAMOND}", []))[0]

    def _format_list(self, cmds):
        prefix = self.context.clean_prefix
        lines = []
        for c in cmds:
            doc = _clean_doc(c.short_doc)
            lines.append(f"`{prefix}{c.name}` \N{EM DASH} {doc}" if doc else f"`{prefix}{c.name}`")
        text = "\n".join(lines)
        if len(text) <= 1024:
            return text
        # too long for one field: fall back to bare command names
        return " ".join(f"`{prefix}{c.name}`" for c in cmds)

    def _match_category(self, arg):
        a = arg.strip().lower()
        for disp in CATEGORY_META:
            if a == disp.lower():
                return disp
        return CATEGORY_ALIASES.get(a)

    # ---- entry point: intercept category names before normal resolution -----

    async def command_callback(self, ctx, *, command=None):
        if command is not None:
            disp = self._match_category(command)
            if disp is not None:
                await self.prepare_help_command(ctx, command)
                return await self.send_category_help(disp)
        return await super().command_callback(ctx, command=command)

    # ---- renderers ---------------------------------------------------------

    async def send_bot_help(self, mapping):
        prefix = self.context.clean_prefix
        buckets = {}
        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds, sort=True)
            if not filtered:
                continue
            buckets.setdefault(self._category_of(cog), []).extend(filtered)

        embed = discord.Embed(
            title="JadedBot \N{EM DASH} Commands",
            description=f"Prefix `{prefix}` \N{MIDDLE DOT} `{prefix}help <command>` for details on any command.",
            colour=discord.Colour.blurple(),
        )
        order = [c for c in CATEGORY_ORDER if c in buckets]
        order += [c for c in buckets if c not in order]
        for disp in order:
            cmds = sorted(set(buckets[disp]), key=lambda c: c.name)
            embed.add_field(name=f"{self._emoji_of(disp)}  {disp}", value=self._format_list(cmds), inline=False)
        embed.set_footer(text="JadedBot")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        await self.send_category_help(self._category_of(cog))

    async def send_group_help(self, group):
        # discord.py routes Group commands here instead of send_command_help; the base
        # implementation is a no-op, so without this override `!help <group>` silently
        # does nothing. send_command_help already handles Group (it lists subcommands).
        await self.send_command_help(group)

    async def send_category_help(self, disp):
        prefix = self.context.clean_prefix
        cmds = [c for c in self.context.bot.commands if self._category_of(c.cog) == disp]
        cmds = await self.filter_commands(cmds, sort=True)
        if not cmds:
            return await self.send_error_message(f'No category called "{disp}" found.')

        embed = discord.Embed(
            title=f"{self._emoji_of(disp)}  {disp}",
            colour=discord.Colour.blurple(),
            description=self._format_list(cmds),
        )
        embed.set_footer(text=f"{prefix}help <command> for usage and aliases")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        prefix = self.context.clean_prefix
        embed = discord.Embed(
            title=f"{prefix}{command.qualified_name}",
            description=_clean_doc(command.help) or "No description.",
            colour=discord.Colour.blurple(),
        )
        usage = f"{prefix}{command.qualified_name}"
        if command.signature:
            usage += f" {command.signature}"
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
        if command.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join(f"`{prefix}{a}`" for a in command.aliases),
                inline=False,
            )
        if isinstance(command, commands.Group):
            subs = await self.filter_commands(command.commands, sort=True)
            if subs:
                lines = []
                for c in subs:
                    doc = _clean_doc(c.short_doc)
                    lines.append(f"`{prefix}{c.qualified_name}` \N{EM DASH} {doc}" if doc else f"`{prefix}{c.qualified_name}`")
                text = "\n".join(lines)
                if len(text) > 1024:
                    text = " ".join(f"`{prefix}{c.qualified_name}`" for c in subs)
                embed.add_field(name="Subcommands", value=text, inline=False)
        disp = self._category_of(command.cog)
        embed.set_footer(text=f"{self._emoji_of(disp)} {disp}")
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(description=str(error), colour=discord.Colour.red())
        await self.get_destination().send(embed=embed)


class HelpCog(commands.Cog):
    """Bot info and the help menu."""
    def __init__(self, bot):
        self.bot = bot
        self._original_help = bot.help_command
        help_command = JadedHelp()
        help_command.cog = self
        bot.help_command = help_command

    async def cog_unload(self):
        self.bot.help_command = self._original_help


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
