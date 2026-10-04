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

# Page titles under Category:Tradeskills on the wiki (each is "Skill <Name>"; commands
# drop the "Skill " prefix, e.g. !monsters smelting -> page "Skill Smelting"). Just a
# name list, not per-skill data like CLASS_LEVELS - tab names/recipe tables are read
# live off each page rather than hardcoded. Re-check Category:Tradeskills if a skill
# stops resolving.
TRADESKILLS = [
    'Alchemy', 'Animal Taming', 'Archaeology', 'Bind Wound', 'Blacksmithing', 'Brewing',
    'Carpentry', 'Cooking', 'Disenchanting', 'Enchanting', 'Farming', 'Fermenting',
    'Fishing', 'Fletching', 'Herbalism', 'Jewelcrafting', 'Leatherworking',
    'Lumberjacking', 'Masonry', 'Mining', 'Navigation', 'Poison Making', 'Pottery',
    'Riding', 'Skinning', 'Smelting', 'Spellcrafting', 'Spinning', 'Spycraft',
    'Stone Cutting', 'Survival', 'Tailoring', 'Tanning', 'Tinkering', 'Wagoneering',
    'Wilderness', 'Woodworking',
]
TRADESKILL_LOOKUP = {_normalize(name): f'Skill {name}' for name in TRADESKILLS}

# (title, id) for every map on mnmatlas.com - id=None is the entry/world map, which
# lives at the site root rather than its own /<id>/ path. Pulled from the site's own
# data/maps.json registry; re-fetch that if a map stops resolving or a new one's missing.
MAPS = [
    ('World map', None),
    ('Night Harbor', 'night-harbor'),
    ('Underdocks', 'underdocks'),
    ("Ail'Vorith", 'ail-vorith'),
    ('Faelindral', 'faelindral'),
    ('Evershade Weald', 'evershade-weald'),
    ('Sungreet Strand', 'sungreet-strand'),
    ('Shaded Dunes', 'shaded-dunes'),
    ('Fallen Pass', 'fallen-pass'),
    ('Tomb of the Last Wyrmsbane', 'wyrmsbane-tomb'),
    ('Glass Flats', 'glass-flats'),
    ('Ancient Crypt', 'ancient-crypt'),
    ('Scarwood', 'scarwood'),
]
MAPS_BASE = 'https://www.mnmatlas.com/'


def map_url(map_id):
    return MAPS_BASE if map_id is None else f'{MAPS_BASE}{map_id}/'


def closest_map(query):
    """Best-match a free-text query against MAPS titles: exact normalized match
    first, then a title that starts with it, then any substring match - in each
    tier preferring the shortest (most specific) title. None if nothing matches."""
    needle = _normalize(query)
    tiers = (
        [(t, i) for t, i in MAPS if _normalize(t) == needle],
        [(t, i) for t, i in MAPS if _normalize(t).startswith(needle)],
        [(t, i) for t, i in MAPS if needle in _normalize(t)],
    )
    for tier in tiers:
        if tier:
            return min(tier, key=lambda ti: len(ti[0]))
    return None

SPELL_ROW_RE = re.compile(r'\{\{SpellRow\s*(.*?)\}\}', re.DOTALL)
FIELD_RE = re.compile(r'\|\s*(\w+)\s*=\s*(.*?)(?=\n\s*\||\Z)', re.DOTALL)
WIKILINK_RE = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]')
TABBER_RE = re.compile(r'<tabber>(.*?)</tabber>', re.DOTALL)
TAB_SPLIT_RE = re.compile(r'\n\|-\|\s*(.*?)\s*=\n')
TABLE_RE = re.compile(r'\{\|.*?\n\|\}', re.DOTALL)
SUBHEADING_RE = re.compile(r'===\s*(.*?)\s*===')
CELL_ATTR_RE = re.compile(r'^(?:\s*[\w-]+\s*=\s*"[^"]*"\s*)+\|\s*')


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


def strip_cell(cell):
    """Drop a cell's leading `style="..." |` attribute block, then clean wiki markup."""
    return strip_wiki_markup(CELL_ATTR_RE.sub('', cell.strip()))


def extract_tabs(wikitext):
    """Split a page using <tabber> into {tab name: tab wikitext}.

    Falls back to a single "Overview" tab covering the whole page for any
    tradeskill page that doesn't use <tabber> (none currently do, but new
    pages might not follow the convention yet).
    """
    match = TABBER_RE.search(wikitext)
    if not match:
        return {'Overview': wikitext}
    pieces = TAB_SPLIT_RE.split(match.group(1))
    tabs = {}
    for i in range(1, len(pieces), 2):
        name = pieces[i].strip()
        content = pieces[i + 1] if i + 1 < len(pieces) else ''
        tabs[name] = content
    return tabs or {'Overview': match.group(1)}


def extract_tables_in_tab(tab_text):
    """Returns [(subheading or None, table wikitext), ...] for every {| ... |} in a tab."""
    headings = list(SUBHEADING_RE.finditer(tab_text))
    results = []
    for table_match in TABLE_RE.finditer(tab_text):
        heading = None
        for heading_match in headings:
            if heading_match.end() < table_match.start():
                heading = heading_match.group(1)
            else:
                break
        results.append((heading, table_match.group(0)))
    return results


def parse_wikitable(table_text):
    """Parse a {| ... |} wikitable into (headers, rows), tolerating both ways MediaWiki
    allows cells to be written (joined with !!/|| on one line, or one per line) and an
    optional |+ Caption line. The header row isn't always the very first thing in the
    table - treat every |- separated block uniformly instead of only checking the top,
    so a table that opens with a caption still gets its real header recognised."""
    body = table_text.strip()
    body = re.sub(r'^\{\|[^\n]*\n', '', body)
    body = re.sub(r'\n\|\}\s*$', '', body)
    body = re.sub(r'^\s*\|\+[^\n]*\n', '', body)
    # Some tables open straight into a |- row marker (no header, or a header after an
    # explicit |-) rather than going directly into a header/row - give it a leading
    # newline so that |- splits the same way wherever it appears, including at position 0.
    body = '\n' + body

    headers = []
    rows = []
    for block in re.split(r'\n\|-', body):
        block = block.strip()
        if block.startswith('!'):
            if not headers:
                headers = [strip_cell(c) for c in re.split(r'!!|\n!', block[1:])]
        elif block.startswith('|'):
            cells = [strip_cell(c) for c in re.split(r'\|\||\n\|', block[1:])]
            if any(cells):
                rows.append(cells)
    return headers, rows


def render_table(headers, rows):
    """Render (headers, rows) as an aligned plain-text table for a ``` ``` code block."""
    ncols = len(headers) if headers else (max((len(r) for r in rows), default=0))
    norm_rows = [(row + [''] * ncols)[:ncols] for row in rows]
    widths = [len(h) for h in headers] if headers else [0] * ncols
    for row in norm_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(cells):
        return '  '.join(c.ljust(widths[i]) for i, c in enumerate(cells)).rstrip()

    lines = []
    if headers:
        lines.append(fmt(headers))
        lines.append('  '.join('-' * w for w in widths))
    lines.extend(fmt(row) for row in norm_rows)
    return '\n'.join(lines)


def parse_tradeskill_tab(tab_text):
    """A tab as [(subheading or None, headers, rows), ...] - one entry per {| ... |}."""
    parsed = []
    for heading, table_text in extract_tables_in_tab(tab_text):
        headers, rows = parse_wikitable(table_text)
        if rows:
            parsed.append((heading, headers, rows))
    return parsed


def chunk_table_rows(heading, headers, rows, budget=1800):
    """Render one table's rows as one or more ``` ```-ready text blocks, each under
    `budget` characters. A table too big for one block is split by rows, repeating
    its header/subheading on each continuation so every block reads correctly alone."""
    prefix = f'== {heading} ==\n' if heading else ''
    blocks = []
    current = []
    for row in rows:
        current.append(row)
        if len(prefix) + len(render_table(headers, current)) > budget:
            current.pop()
            if current:
                blocks.append(prefix + render_table(headers, current))
            current = [row]
    if current:
        blocks.append(prefix + render_table(headers, current))
    return blocks


def find_category_options(parsed_tables, limit=8):
    """If any table in a tab has a column literally called "Category", return the
    distinct values seen in it (first-seen order) - these make good suggestions for
    narrowing down a tab that's too big to post in full."""
    seen = []
    for _, headers, rows in parsed_tables:
        try:
            col = next(i for i, h in enumerate(headers) if h.strip().lower() == 'category')
        except StopIteration:
            continue
        for row in rows:
            if col < len(row) and row[col] and row[col] not in seen:
                seen.append(row[col])
    return seen[:limit]
    return blocks


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


class ChoiceButton(discord.ui.Button):
    def __init__(self, option):
        super().__init__(label=option[:80], style=discord.ButtonStyle.primary)
        self.option = option

    async def callback(self, interaction):
        self.view.chosen = self.option
        self.view.stop()
        await interaction.response.defer()


class ChoicePromptView(discord.ui.View):
    """Buttons for picking one of several options (tradeskill categories, atlas
    maps, ...). Only the person who ran the command can use them - everyone else
    gets a quiet nudge. Pairs with a `!monsters ...` message waiting on a typed
    number for the same choice; whichever the user does first wins (see
    Monsters._prompt_for_choice)."""

    def __init__(self, author, options, timeout=60):
        super().__init__(timeout=timeout)
        self.author = author
        self.chosen = None
        for option in options:
            self.add_item(ChoiceButton(option))

    async def interaction_check(self, interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("This isn't your prompt to answer.", ephemeral=True)
            return False
        return True


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
        - `!monsters <search term>`
        - `!monsters class 4` - Searches level 4 spells for specific class eg: `!monsters cleric 4`
        - `!monsters class spells` - Lists the levels a class gets new spells at eg: `!monsters cleric spells`
        - `!monsters tradeskill` - Lists the recipe tabs for a tradeskill eg: `!monsters smelting`
        - `!monsters tradeskill tab` - Prints that tab's recipes eg: `!monsters smelting refining`
        - `!monsters tradeskill tab filter` - Narrows a big tab down eg: `!monsters blacksmithing copper weapons`
        (if a tab's too big to post, you get its categories as buttons, or reply with the number, instead)
        - `!monsters maps` - Lets you pick an atlas map (buttons or a typed number)
        - `!monsters maps <search>` - Jumps straight to the closest-matching map eg: `!monsters maps night`"""
        if not args:
            await ctx.send("See `!help monsters` for usage examples.")
            return

        try:
            await self._send_search_result(ctx, ' '.join(args))
        except Exception as e:
            await ctx.send(f"Couldn't reach the wiki ({e}).")
            print(f"[monsters error] {e}")

    @monsters.command(name='maps')
    async def maps_command(self, ctx, *args):
        """!monsters maps [search] - Lists the atlas maps on mnmatlas.com to pick
        from (buttons, or reply with a number), or jumps straight to the
        closest-matching map if you give a search term - no prompt in that case."""
        query = ' '.join(args).strip()

        if not query:
            titles = [title for title, _ in MAPS]
            choice = await self._prompt_for_choice(ctx, ":map: Pick an atlas map:", titles)
            if choice is not None:
                await ctx.send(f"**{choice}** — {map_url(dict(MAPS)[choice])}")
            return

        match = closest_map(query)
        if match is None:
            await ctx.send(f"No map matches `{query}`. Run `!monsters maps` to see the list.")
            return
        title, map_id = match
        await ctx.send(f"**{title}** — {map_url(map_id)}")

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

    async def _tradeskill_shortcut(self, ctx, skill_title, args):
        """Shared handler behind each tradeskill's subcommand, e.g. !monsters smelting
        [tab] [filter]. `filter` is free text matched against any cell in a row - the
        natural case is a value from that tab's "Category" column (see
        find_category_options), but it'll match on an ingredient or item name too."""
        try:
            full_text = await self._fetch_full_wikitext(skill_title)
            if full_text is None:
                await ctx.send(f"Couldn't load that page. Here's the link: {page_url(skill_title)}")
                return

            tabs = extract_tabs(full_text)
            display_name = skill_title.removeprefix('Skill ')

            if not args:
                await self._send_tradeskill_tabs(ctx, skill_title, display_name, tabs)
                return

            tab_name, filter_term, ambiguous = self._resolve_tradeskill_tab(args, tabs)
            if tab_name:
                await self._send_tradeskill_table(
                    ctx, skill_title, display_name, tab_name, tabs[tab_name], filter_term)
            elif ambiguous:
                await ctx.send(
                    f"`{' '.join(args)}` matches more than one tab for {display_name}: "
                    + ', '.join(f'`{m}`' for m in ambiguous) + ". Be more specific.")
            else:
                await ctx.send(
                    f"No tab called `{' '.join(args)}` for {display_name}. "
                    f"Run `!monsters {_normalize(display_name)}` for the tab list.")
        except Exception as e:
            await ctx.send(f"Couldn't reach the wiki ({e}).")
            print(f"[monsters error] {e}")

    def _resolve_tradeskill_tab(self, args, tabs):
        """Match args against tab names, trying the whole thing first and - if that
        finds nothing - treating the last word as a filter and re-matching on the
        rest, e.g. `copper weapons` -> tab "Copper Tier (5-75)", filter "weapons".
        Returns (tab_name, filter_term, ambiguous_matches); exactly one of
        tab_name/ambiguous_matches is set on failure, filter_term is None unless used."""
        full_query = _normalize(' '.join(args))
        matches = [name for name in tabs if full_query in _normalize(name)]
        if len(matches) == 1:
            return matches[0], None, None
        if len(matches) == 0 and len(args) > 1:
            short_query = _normalize(' '.join(args[:-1]))
            retry = [name for name in tabs if short_query in _normalize(name)]
            if len(retry) == 1:
                return retry[0], args[-1], None
        return None, None, (matches if len(matches) > 1 else None)

    async def _send_tradeskill_tabs(self, ctx, skill_title, display_name, tabs):
        names = ', '.join(tabs.keys())
        cmd = _normalize(display_name)
        example = next(iter(tabs)).split()[0].lower()
        await ctx.send(
            f":hammer: **{display_name}** tabs: {names}\n"
            f"Use `!monsters {cmd} <tab>` to see one, e.g. `!monsters {cmd} {example}`.")

    async def _send_tradeskill_table(self, ctx, skill_title, display_name, tab_name, tab_text, filter_term=None):
        tables = parse_tradeskill_tab(tab_text)

        if filter_term:
            needle = filter_term.lower()
            tables = [(heading, headers, [r for r in rows if any(needle in c.lower() for c in r)])
                      for heading, headers, rows in tables]
            tables = [t for t in tables if t[2]]

        if not tables:
            if filter_term:
                await ctx.send(
                    f"Nothing in {display_name} — {tab_name} matches `{filter_term}`. "
                    f"Page: {page_url(skill_title)}")
            else:
                await ctx.send(
                    f"Nothing listed under {display_name} - {tab_name} yet (early access - the wiki's "
                    f"still filling in). Page: {page_url(skill_title)}")
            return

        blocks = [block for heading, headers, rows in tables for block in chunk_table_rows(heading, headers, rows)]

        if len(blocks) > 2 and not filter_term:
            categories = find_category_options(tables)
            header = f":hammer: **{display_name} — {tab_name}** has too many recipes to list at once."
            if not categories:
                await ctx.send(f"{header} See the full page: {page_url(skill_title)}")
                return

            category = await self._prompt_for_choice(ctx, header, categories)
            if category is not None:
                await self._send_tradeskill_table(
                    ctx, skill_title, display_name, tab_name, tab_text, category.lower())
            return

        max_messages = 6
        title = f":hammer: **{display_name} — {tab_name}**"
        if filter_term:
            title += f" ({filter_term})"
        await ctx.send(title)
        for block in blocks[:max_messages]:
            await ctx.send(f"```\n{block}\n```")
        if len(blocks) > max_messages:
            await ctx.send(
                f"+{len(blocks) - max_messages} more block(s) - see the full page: {page_url(skill_title)}")

    async def _prompt_for_choice(self, ctx, header, options, timeout=60):
        """Offer `options` as clickable buttons and, in parallel, accept a typed
        number for the same choice - whichever the user does first wins. Returns
        the chosen string, or None if the prompt timed out unanswered."""
        numbered = '\n'.join(f'{i}. {o}' for i, o in enumerate(options, 1))
        view = ChoicePromptView(ctx.author, options, timeout=timeout)
        message = await ctx.send(
            f"{header}\nPick one below, or reply with its number:\n{numbered}", view=view)

        def is_valid_number(msg):
            return (msg.author == ctx.author and msg.channel == ctx.channel
                    and msg.content.strip().isdigit() and 1 <= int(msg.content.strip()) <= len(options))

        view_wait = asyncio.ensure_future(view.wait())
        text_wait = asyncio.ensure_future(self.bot.wait_for('message', check=is_valid_number, timeout=timeout))
        done, pending = await asyncio.wait([view_wait, text_wait], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

        chosen = view.chosen
        if chosen is None and text_wait in done and not text_wait.cancelled() and text_wait.exception() is None:
            chosen = options[int(text_wait.result().content.strip()) - 1]

        if not view.is_finished():
            view.stop()
        for child in view.children:
            child.disabled = True
        try:
            await message.edit(view=view)
        except discord.HTTPException:
            pass

        return chosen

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

    # Same generation trick, one subcommand per tradeskill (!monsters smelting [tab]).
    for _skill_name in TRADESKILLS:
        _cmd_name = _normalize(_skill_name)
        _skill_title = f'Skill {_skill_name}'

        def _make_subcommand(_skill_title=_skill_title, _cmd_name=_cmd_name):
            async def _subcommand(self, ctx, *args):
                await self._tradeskill_shortcut(ctx, _skill_title, args)
            _subcommand.__name__ = _cmd_name
            _subcommand.__qualname__ = f'Monsters.{_cmd_name}'
            return _subcommand

        locals()[_cmd_name] = monsters.command(
            name=_cmd_name,
            help=(f"!monsters {_cmd_name} [tab] - Lists {_skill_name}'s recipe tabs, or prints one "
                  f"tab's recipes as a table. No argument lists the tabs."),
        )(_make_subcommand())
    del _skill_name, _skill_title, _cmd_name, _make_subcommand


async def setup(bot):
    await bot.add_cog(Monsters(bot))
