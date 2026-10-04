import asyncio
import re
import discord
import requests
from discord.ext import commands

WIKI_BASE = 'https://monstersandmemories.miraheze.org'
WIKI_API = WIKI_BASE + '/w/api.php'
HEADERS = {'User-Agent': 'JadedBot/2.5 (+https://github.com/Virtual-/JadedBot)'}

# The wiki doesn't space spell/ability levels evenly across classes (casters get
# them every 4 levels, melee classes get one almost every level), so there's no
# formula for "what level section does this class have" - it has to be read off
# the actual pages and kept here. Pulled from each class's section list on
# monstersandmemories.miraheze.org; this is an early-access game so the wiki
# (and these breakpoints) will drift - re-check Category:Classes if a class
# stops resolving or a level comes back empty that shouldn't.
CLASS_LEVELS = {
    'Archer': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25,
               26, 28, 29, 30, 32, 33, 34, 35, 38, 39, 40, 42, 44, 45, 46, 48, 49, 50, 52, 55, 58, 59, 60],
    'Bard': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 24, 26, 28, 30, 32, 33, 36,
             40, 44, 46, 48, 50, 56, 60],
    'Beastmaster': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26,
                    27, 28, 29, 30, 32, 33, 35, 36, 37, 39, 40, 41, 43, 44, 45, 47, 48, 49, 50, 52, 53, 54, 55, 56, 57, 59],
    'Cleric': [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 55, 56, 60],
    'Druid': [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 50, 52, 55, 56, 60],
    'Elementalist': [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 50, 52, 54, 56, 58, 60],
    'Enchanter': [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 55, 56, 60],
    'Fighter': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 22, 23, 24, 25,
                28, 29, 30, 31, 32, 33, 34, 35, 38, 40, 41, 42, 43, 44, 45, 48, 49, 50, 51, 52, 53, 54, 58],
    'Inquisitor': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 22, 23, 24,
                   25, 26, 27, 28, 30, 31, 32, 34, 36, 40, 42, 44, 48, 50, 52, 53, 54, 55, 56, 60],
    'Monk': [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 16, 18, 20, 21, 22, 24, 25, 26, 28, 30, 31, 34, 35],
    'Necromancer': [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 54, 56, 60],
    'Paladin': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 24, 28,
                29, 30, 32, 36, 40, 44, 48, 50, 51, 52, 55, 56, 60],
    'Ranger': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
               24, 26, 28, 30, 31, 32, 35, 36, 38, 40, 41, 44, 46, 47, 48, 49, 50, 52, 54, 55, 56, 59],
    'Rogue': [1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 20, 22, 24, 25, 26, 28, 30, 32,
              34, 36, 38, 40, 44, 45, 46, 48, 50, 54, 56, 58],
    'Shadow Knight': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 20, 22, 24, 26,
                      28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 52, 54, 56, 58, 60],
    'Shaman': [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60],
    'Spellblade': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 25, 26, 28, 30,
                   32, 34, 35, 36, 38, 40, 42, 44, 45, 46, 48, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60],
    'Wizard': [1, 4, 8, 12, 16, 20, 24, 28, 30, 32, 36, 40, 44, 48, 50, 52, 55, 56, 60],
}


def _normalize(name):
    return re.sub(r'[\s_-]+', '', name.strip().lower())


CLASS_LOOKUP = {_normalize(name): name for name in CLASS_LEVELS}

STATIC_LINKS = {
    'maps': 'https://www.mnmatlas.com/?level=surface&x=1335.38&y=1256&z=2.88',
}

SPELL_ROW_RE = re.compile(r'\{\{SpellRow\s*(.*?)\}\}', re.DOTALL)
FIELD_RE = re.compile(r'\|\s*(\w+)\s*=\s*(.*?)(?=\n\s*\||\Z)', re.DOTALL)
WIKILINK_RE = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]')


def strip_wiki_markup(text):
    if not text:
        return ''
    text = WIKILINK_RE.sub(r'\1', text)
    text = text.replace("'''", '').replace("''", '')
    text = re.sub(r'<br\s*/?>', ', ', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()


def page_url(title, anchor=None):
    url = WIKI_BASE + '/wiki/' + title.replace(' ', '_')
    if anchor:
        url += '#' + anchor
    return url


def extract_level_section(full_wikitext, level):
    """Pull just the body of a `==Level N==` heading out of a full page's wikitext."""
    heading_re = re.compile(r'^==\s*Level\s+' + str(level) + r'\s*==\s*$', re.MULTILINE)
    match = heading_re.search(full_wikitext)
    if not match:
        return None
    rest = full_wikitext[match.end():]
    next_heading = re.search(r'^==[^=].*?==\s*$', rest, re.MULTILINE)
    return rest[:next_heading.start()] if next_heading else rest


def parse_spell_rows(section_text):
    spells = []
    for block in SPELL_ROW_RE.findall(section_text):
        fields = {k: v.strip() for k, v in FIELD_RE.findall(block)}
        if not fields.get('name'):
            continue
        spells.append({
            'name': strip_wiki_markup(fields.get('name', '')),
            'description': strip_wiki_markup(fields.get('description', '')),
            'mana': strip_wiki_markup(fields.get('mana', '')) or '?',
            'casttime': strip_wiki_markup(fields.get('casttime', '')),
        })
    return spells


def parse_where_to_obtain(spell_wikitext):
    section = re.search(r'=\s*Where to Obtain\s*=(.*?)(?:\n=[^=]|\Z)', spell_wikitext, re.DOTALL)
    if not section:
        return None
    rows = section.group(1).split('|-')[1:]
    if not rows:
        return None
    first_row = rows[0].split('|}')[0].strip()
    if first_row.startswith('|'):
        first_row = first_row[1:]
    cells = [strip_wiki_markup(c) for c in first_row.split('||')]
    cells = [c for c in cells if c and c != '-']
    return ' — '.join(cells) if cells else None


class Monsters(commands.Cog):
    """Looks things up on the Monsters & Memories wiki. Experimental - this is
    an early-access game and the wiki is actively being filled in, so some
    spells/levels will come back with nothing listed yet."""

    def __init__(self, bot):
        self.bot = bot

    async def _wiki_get(self, params):
        loop = asyncio.get_running_loop()
        params = dict(params, format='json')
        response = await loop.run_in_executor(
            None, lambda: requests.get(WIKI_API, params=params, headers=HEADERS, timeout=10))
        return response.json()

    async def _search_top_result(self, query):
        data = await self._wiki_get({'action': 'query', 'list': 'search', 'srsearch': query, 'srlimit': 1})
        results = data.get('query', {}).get('search', [])
        return results[0]['title'] if results else None

    async def _fetch_full_wikitext(self, title):
        data = await self._wiki_get({'action': 'parse', 'page': title, 'prop': 'wikitext'})
        if 'error' in data:
            return None
        return data['parse']['wikitext']['*']

    async def _fetch_vendor_info(self, spell_names):
        if not spell_names:
            return {}
        data = await self._wiki_get({
            'action': 'query', 'titles': '|'.join(spell_names),
            'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main', 'redirects': 1,
        })
        pages = data.get('query', {}).get('pages', {})
        by_title = {}
        for page in pages.values():
            if 'missing' in page or 'revisions' not in page:
                continue
            content = page['revisions'][0]['slots']['main']['*']
            by_title[page['title']] = parse_where_to_obtain(content)
        # titles can come back redirect-resolved or re-cased; match on a normalized key too
        normalized_lookup = {_normalize(k): v for k, v in by_title.items()}
        return {name: by_title.get(name, normalized_lookup.get(_normalize(name))) for name in spell_names}

    @commands.group(invoke_without_command=True)
    async def monsters(self, ctx, *args):
        """Looks things up on the Monsters & Memories wiki.
        - !monsters <search term>
        - !monsters class 4 - Searches level 4 spells for specific class eg: !monsters cleric 4
        - !monsters class spells - Lists the levels a class gets new spells at eg: !monsters cleric spells
        - !monsters maps - Returns link to interactive map site."""
        if not args:
            await ctx.send("See `!help monsters` for usage examples.")
            return

        if len(args) == 1 and args[0].lower() in STATIC_LINKS:
            await ctx.send(STATIC_LINKS[args[0].lower()])
            return

        try:
            await self._send_search_result(ctx, ' '.join(args))
        except Exception as e:
            await ctx.send(f"Couldn't reach the wiki ({e}).")
            print(f"[monsters error] {e}")

    async def _class_shortcut(self, ctx, class_name, args):
        """Shared handler behind each class's subcommand, e.g. !monsters cleric 20 / spells / (bare)."""
        try:
            if not args:
                await ctx.send(f":closed_book: **{class_name}** — {page_url(class_name)}")
            elif args[0].lower() == 'spells':
                await self._send_class_spell_levels(ctx, class_name)
            elif args[-1].isdigit():
                await self._send_class_level(ctx, class_name, int(args[-1]))
            else:
                cmd = _normalize(class_name)
                await ctx.send(f"Usage: `!monsters {cmd} <level>` or `!monsters {cmd} spells`.")
        except Exception as e:
            await ctx.send(f"Couldn't reach the wiki ({e}).")
            print(f"[monsters error] {e}")

    async def _send_search_result(self, ctx, query):
        title = await self._search_top_result(query)
        if not title:
            await ctx.send(f"Couldn't find anything for `{query}`.")
            return
        await ctx.send(f":closed_book: **{title}** — {page_url(title)}")

    async def _send_class_spell_levels(self, ctx, class_name):
        levels = ', '.join(str(n) for n in CLASS_LEVELS[class_name])
        await ctx.send(f":scroll: **{class_name}** gets new abilities at levels: {levels}")

    async def _send_class_level(self, ctx, class_name, requested_level):
        breakpoints = CLASS_LEVELS[class_name]
        if requested_level < breakpoints[0]:
            await ctx.send(
                f"{class_name} doesn't have anything listed below level {breakpoints[0]} yet. "
                f"Page: {page_url(class_name)}")
            return

        snapped = max(b for b in breakpoints if b <= requested_level)

        full_text = await self._fetch_full_wikitext(class_name)
        if full_text is None:
            await ctx.send(f"Couldn't load that page. Here's the link: {page_url(class_name)}")
            return

        section = extract_level_section(full_text, snapped)
        spells = parse_spell_rows(section) if section else []

        if not spells:
            await ctx.send(
                f"Nothing listed for {class_name} at level {snapped} yet (early access - the wiki's still "
                f"filling in). Page: {page_url(class_name, f'Level_{snapped}')}")
            return

        vendors = await self._fetch_vendor_info([s['name'] for s in spells])

        title = f"{class_name} — Level {snapped}"
        if snapped != requested_level:
            title += f" (nearest to {requested_level})"

        embed = discord.Embed(
            title=title,
            url=page_url(class_name, f'Level_{snapped}'),
            colour=discord.Colour.blurple(),
        )
        for spell in spells[:20]:
            stats = f"{spell['mana']} mana"
            if spell['casttime']:
                stats += f", {spell['casttime']} cast"
            vendor = vendors.get(spell['name']) or "Not listed yet"
            description = spell['description']
            if len(description) > 220:
                description = description[:217] + '...'
            embed.add_field(
                name=f"{spell['name']} ({stats})",
                value=f"{description}\nVendor: {vendor}",
                inline=False,
            )
        if len(spells) > 20:
            embed.set_footer(text=f"+{len(spells) - 20} more at this level - see the full page")

        await ctx.send(embed=embed)

    # One subcommand per class (!monsters cleric 20 / spells / bare), generated here so
    # adding a class to CLASS_LEVELS is enough to get it a subcommand - no per-class
    # boilerplate below. Attached to the `monsters` group object defined above, which is
    # still a plain local name at this point in the class body.
    #
    # Each one is also bound to a class attribute (locals()[_cmd_name] = ...), not just
    # registered on the group as a side effect - discord.py's Cog machinery only assigns
    # `.cog` (and therefore `self`) to commands it finds as named class attributes when
    # scanning the class body; a subcommand that's only reachable via monsters.commands
    # silently keeps `.cog = None`, which corrupts the self/ctx binding at call time.
    # `.parent` (set by monsters.command() below) is what stops it from ALSO being
    # registered as a top-level !<class> command - see Cog._inject's `parent is None` check.
    for _class_name in CLASS_LEVELS:
        _cmd_name = _normalize(_class_name)

        def _make_subcommand(_class_name=_class_name, _cmd_name=_cmd_name):
            async def _subcommand(self, ctx, *args):
                await self._class_shortcut(ctx, _class_name, args)
            _subcommand.__name__ = _cmd_name
            # Discord.py decides how many leading params (self, ctx) to hide from
            # !help by checking __qualname__ for a real class-method shape; a
            # closure's default qualname has a <locals> segment that fails that
            # check and leaves `ctx` showing up as a visible argument. Giving it
            # a plain "Monsters.<name>" qualname makes it look like one.
            _subcommand.__qualname__ = f'Monsters.{_cmd_name}'
            return _subcommand

        locals()[_cmd_name] = monsters.command(
            name=_cmd_name,
            help=(f"!monsters {_cmd_name} [level|spells] - {_class_name}'s abilities at that level "
                  f"(nearest below if needed) or, with `spells`, its spell-level list. No argument "
                  f"just links the page."),
        )(_make_subcommand())
    del _class_name, _cmd_name, _make_subcommand


async def setup(bot):
    await bot.add_cog(Monsters(bot))
