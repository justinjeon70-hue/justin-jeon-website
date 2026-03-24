#!/usr/bin/env python3
"""
build_book.py - Generate HTML chapter pages for "The Oxytocin Story" book website.
Reads translated markdown files, splits into chapters, and generates styled HTML pages.
"""

import os
import re
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Paths ──────────────────────────────────────────────────────────────────
TRANSLATION_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "\uce90\ub098\ub2e4 \uc5f0\uad6c\ud559\uae30", "translation")
BOOK_DIR = os.path.join(os.path.expanduser("~"), "justin-jeon-website", "book")
SITE_ROOT = os.path.join(os.path.expanduser("~"), "justin-jeon-website")

# Markdown source files in reading order
MD_FILES = [
    "00_introduction_and_part1.md",
    "02_part2.md",
    "03_part3.md",
    "04_part4.md",
    "05_part5.md",
    "06_part6.md",
    "07_part7.md",
    "08_part8_closing_appendix.md",
    "09_references.md",
]

# ── Figure assignments (chapter_slug -> figure filename) ──────────────────
FIGURE_MAP = {
    "00-introduction": "fig05_oxytocin_effects.png",
    "01-secret-of-roseto": "fig01_research_papers.png",
    "04-origins-of-happiness": "fig04_global_priorities.png",
    "10-hormone-that-believes-in-you": "fig08_trust_game.png",
    "15-oxytocin-and-theory-of-mind": "fig02_rme_test.png",
    "22-autism-fighter": "fig02_rme_test.png",
    "27-master-your-gut": "fig03_autism_fmt.png",
    "34-forget-cortisol": "fig06_oxytocin_vs_cortisol.png",
    "37-afterword": "fig07_oxytocin_boosters.png",
}

# ── MASTER CHAPTER LIST ───────────────────────────────────────────────────
# (web_number, slug, title_for_display, part_label, source_file_index, source_chapter_heading_regex)
# source_file_index: which MD_FILES entry to search in
# source_chapter_heading_regex: regex to find the heading in that file

CHAPTER_DEFS = [
    # Introduction
    (0, "00-introduction",
     "Introduction: If You Want to Be Happy and Healthy, Oxytocin",
     "Introduction", 0,
     r"# Introduction:.*?\n"),

    # Part 1
    (1, "01-secret-of-roseto",
     "Chapter 1: The Secret of Roseto",
     "Part One: What Is Oxytocin?", 0,
     r"## Chapter 0?1:\s*The Secret of Roseto"),
    (2, "02-oxytocin-101",
     "Chapter 2: Oxytocin 101 -- The Hormone That Has Protected Humanity",
     "Part One: What Is Oxytocin?", 0,
     r"## Chapter 0?2:\s*Oxytocin 101"),
    (3, "03-hormone-101",
     "Chapter 3: Hormone 101 -- The Vast Chemical Factory Called the Human Body",
     "Part One: What Is Oxytocin?", 0,
     r"## Chapter 0?3:\s*Hormone 101"),

    # Part 2
    (4, "04-origins-of-happiness",
     "Chapter 4: The Origins of Happiness",
     "Part Two: Oxytocin for the Soul", 1,
     r"## Chapter 3:\s*The Origins of Happiness"),
    (5, "05-power-that-conquers-trauma",
     "Chapter 5: The Power That Conquers Trauma",
     "Part Two: Oxytocin for the Soul", 1,
     r"## Chapter 4:\s*The Power That Conquers Trauma"),
    (6, "06-oxytocin-and-resilience",
     "Chapter 6: Oxytocin and Resilience",
     "Part Two: Oxytocin for the Soul", 1,
     r"## Chapter 5:\s*Oxytocin and Resilience"),
    (7, "07-loneliness-makes-you-sick",
     "Chapter 7: Loneliness Makes You Sick",
     "Part Two: Oxytocin for the Soul", 1,
     r"## Chapter 6:\s*Loneliness Makes You Sick"),
    (8, "08-oxytocin-the-pain-killer",
     "Chapter 8: Oxytocin, the Pain Killer",
     "Part Two: Oxytocin for the Soul", 1,
     r"## Chapter 7:\s*Oxytocin, the Pain Killer"),

    # Part 3
    (9, "09-attachment-hormone",
     "Chapter 9: Oxytocin, the Attachment Hormone",
     "Part Three: The Oxytocin That Makes Us Better People", 2,
     r"## Chapter 8:\s*Oxytocin, the Attachment Hormone"),
    (10, "10-hormone-that-believes-in-you",
     "Chapter 10: Oxytocin, the Hormone That Believes in You",
     "Part Three: The Oxytocin That Makes Us Better People", 2,
     r"## Chapter 9:\s*Oxytocin, the Hormone That Believes in You"),
    (11, "11-altruistic-hormone",
     "Chapter 11: Oxytocin, the Altruistic Hormone",
     "Part Three: The Oxytocin That Makes Us Better People", 2,
     r"## Chapter 10:\s*Oxytocin, the Altruistic Hormone"),
    (12, "12-its-okay-to-not-be-okay",
     "Chapter 12: It's Okay to Not Be Okay",
     "Part Three: The Oxytocin That Makes Us Better People", 2,
     r"## Chapter 11:\s*It.s Okay to Not Be Okay"),
    (13, "13-becoming-a-better-parent",
     "Chapter 13: Oxytocin for Becoming a Better Parent",
     "Part Three: The Oxytocin That Makes Us Better People", 2,
     r"## Chapter 12:\s*Oxytocin for Becoming a Better Parent"),

    # Part 4
    (14, "14-magic-of-eye-contact",
     "Chapter 14: The Magic of Eye Contact",
     "Part Four: The Oxytocin That Makes Us More Loving", 3,
     r"## Chapter 13:\s*The Magic of Eye Contact"),
    (15, "15-force-that-keeps-relationships-going",
     "Chapter 15: The Force That Keeps Relationships Going",
     "Part Four: The Oxytocin That Makes Us More Loving", 3,
     r"## Chapter 14:\s*The Force That Keeps Relationships Going"),
    (16, "16-oxytocin-and-theory-of-mind",
     "Chapter 16: Oxytocin and Theory of Mind",
     "Part Four: The Oxytocin That Makes Us More Loving", 3,
     r"## Chapter 15:\s*Oxytocin and Theory of Mind"),
    (17, "17-oxytocin-that-keeps-you-faithful",
     "Chapter 17: The Oxytocin That Keeps You Faithful",
     "Part Four: The Oxytocin That Makes Us More Loving", 3,
     r"## Chapter 16:\s*The Oxytocin That Keeps You Faithful"),

    # Part 5
    (18, "18-heart-beat-cardiovascular",
     "Chapter 18: The Hormone That Makes Your Heart Beat",
     "Part Five: Oxytocin for a Healthier You", 4,
     r"## Chapter 17:\s*The Hormone That Makes Your Heart Beat"),
    (19, "19-keeps-you-slim-obesity-diabetes",
     "Chapter 19: The Hormone That Keeps You Slim",
     "Part Five: Oxytocin for a Healthier You", 4,
     r"## Chapter 18:\s*The Hormone That Keeps You Slim"),
    (20, "20-healing-inflammatory-bowel",
     "Chapter 20: Oxytocin for Healing Inflammatory Bowel Disease",
     "Part Five: Oxytocin for a Healthier You", 4,
     r"## Chapter 19:\s*Oxytocin for Healing Inflammatory Bowel"),
    (21, "21-cancer-fighter",
     "Chapter 21: Oxytocin as a Cancer Fighter",
     "Part Five: Oxytocin for a Healthier You", 4,
     r"## Chapter 20:\s*Oxytocin as a Cancer Fighter"),
    (22, "22-autism-fighter",
     "Chapter 22: The Autism Fighter",
     "Part Five: Oxytocin for a Healthier You", 4,
     r"## Chapter 21:\s*The Autism Fighter"),
    (23, "23-love-is-the-medicine",
     "Chapter 23: Love Is the Medicine",
     "Part Five: Oxytocin for a Healthier You", 4,
     r"## Chapter 22:\s*Love Is the Medicine"),

    # Part 6
    (24, "24-power-of-touch",
     "Chapter 24: The Power of Touch",
     "Part Six: The Oxytocin Lifestyle -- Body and Senses", 5,
     r"## Chapter 23:\s*The Power of Touch"),
    (25, "25-pleasure-principle",
     "Chapter 25: The Pleasure Principle -- How Sex Raises Oxytocin",
     "Part Six: The Oxytocin Lifestyle -- Body and Senses", 5,
     r"## Chapter 24:\s*The Pleasure Principle"),
    (26, "26-eat-your-way-up",
     "Chapter 26: Eat Your Way Up -- How Food Raises Oxytocin",
     "Part Six: The Oxytocin Lifestyle -- Body and Senses", 5,
     r"## Chapter 25:\s*Eat Your Way Up"),
    (27, "27-master-your-gut",
     "Chapter 27: Master Your Gut, Master Your Oxytocin",
     "Part Six: The Oxytocin Lifestyle -- Body and Senses", 5,
     r"## Chapter 26:\s*Master Your Gut"),
    (28, "28-move-it-or-lose-it",
     "Chapter 28: Move It or Lose It -- How Exercise Raises Oxytocin",
     "Part Six: The Oxytocin Lifestyle -- Body and Senses", 5,
     r"## Chapter 27:\s*Move It or Lose It"),

    # Part 7
    (29, "29-dish-it-out-gossip",
     "Chapter 29: Dish It Out, and It Goes Up -- Gossip vs. Backstabbing",
     "Part Seven: The Oxytocin Lifestyle -- Mind and Community", 6,
     r"## Chapter 28:\s*Dish It Out"),
    (30, "30-sing-it-out",
     "Chapter 30: Sing It Out, and It Goes Up -- Skip the Solo, Join the Chorus",
     "Part Seven: The Oxytocin Lifestyle -- Mind and Community", 6,
     r"## Chapter 29:\s*Sing It Out"),
    (31, "31-lock-eyes-gift-your-dog",
     "Chapter 31: Lock Eyes, and It Goes Up -- The Gift Your Dog Gives You",
     "Part Seven: The Oxytocin Lifestyle -- Mind and Community", 6,
     r"## Chapter 30:\s*Lock Eyes"),
    (32, "32-be-grateful",
     "Chapter 32: Be Grateful, and It Goes Up -- The Secret of Gratitude",
     "Part Seven: The Oxytocin Lifestyle -- Mind and Community", 6,
     r"## Chapter 31:\s*Be Grateful"),
    (33, "33-listen-up-storytelling",
     "Chapter 33: Listen Up, and It Goes Up -- The Power of Storytelling",
     "Part Seven: The Oxytocin Lifestyle -- Mind and Community", 6,
     r"## Chapter 32:\s*Listen Up"),
    (34, "34-forget-cortisol",
     "Chapter 34: Forget Cortisol -- Choose the Oxytocin Lifestyle",
     "Part Seven: The Oxytocin Lifestyle -- Mind and Community", 6,
     r"## Chapter 33:\s*Forget Cortisol"),

    # Part 8
    (35, "35-change-your-narrative",
     "Chapter 35: Change Your Narrative, Change Your Life",
     "Part Eight: The Power of Narrative", 7,
     r"## Chapter 34:\s*Change Your Narrative"),
    (36, "36-from-freud-to-adler",
     "Chapter 36: From Freud to Adler",
     "Part Eight: The Power of Narrative", 7,
     r"## Chapter 35:\s*From Freud to Adler"),
    (37, "37-from-insulin-to-oxytocin",
     "Chapter 37: From Insulin to Oxytocin -- Love Is Medicine",
     "Part Eight: The Power of Narrative", 7,
     r"## Chapter 36:\s*From Insulin to Oxytocin"),
]

# ── Helper: convert markdown to HTML ──────────────────────────────────────
def inline_format(text):
    """Handle inline markdown: bold, italic, links, superscripts."""
    # Bold+italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'(?<!\w)\*(.*?)\*(?!\w)', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    # Superscript references like ^1, ^2, etc.
    text = re.sub(r'\^(\d+)', r'<sup>\1</sup>', text)
    # Footnote style [^17-1]
    text = re.sub(r'\[\^([\w-]+)\]', '', text)
    # Em dash
    text = text.replace(' -- ', ' &mdash; ')
    text = text.replace(' --- ', ' &mdash; ')
    text = re.sub(r'(?<=\w)---(?=\w)', '&mdash;', text)
    return text


def md_to_html(md_text):
    """Simple markdown-to-HTML converter for the book content."""
    lines = md_text.split('\n')
    html_parts = []
    in_blockquote = False
    in_table = False
    table_rows = []
    bq_lines = []

    def flush_blockquote():
        nonlocal in_blockquote, bq_lines
        if in_blockquote and bq_lines:
            content = '\n'.join(bq_lines)
            # Check if it starts with Oxytocin tip/booster or similar
            if any(kw in content for kw in ['Oxytocin in Everyday', 'Oxytocin Booster', 'Oxytocin in Action',
                                             'Everyday Oxytocin', 'Oxytocin Boost', 'Oxytocin Way',
                                             'Oxytocin Stress', 'Oxytocin Gratitude',
                                             'Oxytocin Lifestyle', 'Oxytocin Leadership',
                                             'Oxytocin and Family', 'Oxytocin Reconciliation',
                                             'Theory of mind', 'The Oxytocin Way',
                                             'The Oxytocin Gratitude', 'Oxytocin Boost:',
                                             'Key finding:', 'On gossip:']):
                html_parts.append(f'<div class="hl">{inline_format(content)}</div>')
            else:
                # Pull quote style
                html_parts.append(f'<div class="pq">{inline_format(content)}</div>')
        in_blockquote = False
        bq_lines = []

    def flush_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            html_parts.append('<div class="table-wrap"><table>')
            header_done = False
            for row in table_rows:
                cells = [c.strip() for c in row.split('|')]
                cells = [c for c in cells if c]
                if not cells:
                    continue
                # Skip separator rows
                if all(set(c.strip()) <= {'-', ':', ' '} for c in cells):
                    if not header_done:
                        header_done = True
                    continue
                if not header_done:
                    html_parts.append('<thead><tr>' + ''.join(f'<th>{inline_format(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                    header_done = True
                else:
                    html_parts.append('<tr>' + ''.join(f'<td>{inline_format(c)}</td>' for c in cells) + '</tr>')
            html_parts.append('</tbody></table></div>')
        in_table = False
        table_rows = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip figure references in brackets
        if stripped.startswith('[Figure:') or stripped.startswith('[figure:'):
            i += 1
            continue

        # Skip top-level headings (# Part ..., ## Chapter ...) since we handle them in the header
        if re.match(r'^#{1,2}\s+(Chapter|Part)\s', stripped):
            i += 1
            continue

        # Horizontal rules
        if stripped in ('---', '***', '* * *'):
            flush_blockquote()
            flush_table()
            i += 1
            continue

        # H3 headings (### )
        if stripped.startswith('### '):
            flush_blockquote()
            flush_table()
            title = stripped[4:].strip()
            html_parts.append(f'<h3>{inline_format(title)}</h3>')
            i += 1
            continue

        # H4 headings (#### )
        if stripped.startswith('#### '):
            flush_blockquote()
            flush_table()
            title = stripped[5:].strip()
            html_parts.append(f'<h4>{inline_format(title)}</h4>')
            i += 1
            continue

        # Tables
        if '|' in stripped and stripped.startswith('|'):
            flush_blockquote()
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(stripped)
            i += 1
            continue
        elif in_table:
            flush_table()

        # Blockquotes
        if stripped.startswith('> ') or (stripped == '>' and not in_table):
            flush_table()
            if not in_blockquote:
                in_blockquote = True
                bq_lines = []
            content = stripped.lstrip('> ').strip()
            if content:
                bq_lines.append(content)
            i += 1
            continue
        elif in_blockquote:
            flush_blockquote()

        # Footnote-style lines (small text beginning with *)
        if stripped.startswith('*[') or stripped.startswith('*\\'):
            html_parts.append(f'<p class="footnote">{inline_format(stripped.strip("*").strip())}</p>')
            i += 1
            continue

        # Empty lines
        if not stripped:
            i += 1
            continue

        # Regular paragraphs
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if (not next_line or next_line.startswith('#') or next_line.startswith('>') or
                (next_line.startswith('|') and '|' in next_line[1:]) or
                next_line in ('---', '***') or
                next_line.startswith('*[')):
                break
            para_lines.append(next_line)
            i += 1
        para_text = ' '.join(para_lines)
        html_parts.append(f'<p>{inline_format(para_text)}</p>')

    flush_blockquote()
    flush_table()
    return '\n'.join(html_parts)


# ── Read source files ─────────────────────────────────────────────────────
def read_source_files():
    """Read all markdown files into a list."""
    contents = []
    for fname in MD_FILES:
        fpath = os.path.join(TRANSLATION_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                contents.append(f.read())
        else:
            print(f"  WARNING: File not found: {fpath}")
            contents.append("")
    return contents


def extract_chapter_content(file_text, heading_regex, file_idx):
    """Extract content from heading to the next ## heading or # heading or EOF."""
    m = re.search(heading_regex, file_text)
    if not m:
        return ""

    start = m.end()
    # Find the next ## Chapter, # Part, # Afterword, # Appendix, # References, or EOF
    rest = file_text[start:]

    # For introduction, extract from after the intro heading to first ## Chapter
    if 'Introduction' in heading_regex:
        # Get everything from the intro title line to just before "## Chapter 01"
        intro_match = re.search(r'# Introduction:.*?\n(.*?)(?=\n## Chapter\s)', file_text, re.DOTALL)
        if intro_match:
            return intro_match.group(1).strip()
        return ""

    # For regular chapters, find next boundary
    next_heading = re.search(r'\n(?:## Chapter\s+\d|# (?:Part|Afterword|Appendix|References)|\*\[End of Part)', rest)
    if next_heading:
        content = rest[:next_heading.start()]
    else:
        content = rest

    return content.strip()


# ── HTML Template ─────────────────────────────────────────────────────────
def get_chapter_html(chapter, prev_ch, next_ch):
    """Generate full HTML for a chapter page."""

    figure_html = ""
    if chapter['slug'] in FIGURE_MAP and FIGURE_MAP[chapter['slug']]:
        fig = FIGURE_MAP[chapter['slug']]
        fig_alt = fig.replace('.png', '').replace('_', ' ').title()
        figure_html = f'''
    <figure class="chapter-figure">
        <img src="figures/{fig}" alt="{fig_alt}" loading="lazy">
    </figure>'''

    prev_link = ""
    if prev_ch:
        prev_title = prev_ch["title"].replace("&", "&amp;")
        prev_link = f'<a href="{prev_ch["filename"]}" class="nav-prev"><span class="nav-arrow">&larr;</span><span class="nav-label">Previous</span><span class="nav-title">{prev_title}</span></a>'
    else:
        prev_link = '<span class="nav-prev nav-disabled"></span>'

    next_link = ""
    if next_ch:
        next_title = next_ch["title"].replace("&", "&amp;")
        next_link = f'<a href="{next_ch["filename"]}" class="nav-next"><span class="nav-label">Next</span><span class="nav-arrow">&rarr;</span><span class="nav-title">{next_title}</span></a>'
    else:
        next_link = '<span class="nav-next nav-disabled"></span>'

    content_html = md_to_html(chapter['content'])
    safe_title = chapter["title"].replace("&", "&amp;").replace('"', "&quot;")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_title} &mdash; The Oxytocin Story</title>
<meta name="description" content="{safe_title} from The Oxytocin Story by Justin Jeon">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:ital,wght@0,300;0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root{{--cream:#FDF8F0;--rose:#8B3A4A;--coral:#D4726A;--gold:#C4944A;--dark:#2C2C2C;--body:#3D3D3D;--light:#6B6B6B;--divider:#E8DDD0;--hl:#FFF5EB}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Source Sans 3',Georgia,serif;background:var(--cream);color:var(--body);line-height:1.85;font-size:17px}}

/* Progress bar */
.progress-bar{{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,var(--rose),var(--coral),var(--gold));z-index:1000;width:0%;transition:width .1s linear}}

/* Top nav */
.top-nav{{background:var(--dark);padding:12px 40px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:999}}
.top-nav a{{color:rgba(255,255,255,.7);text-decoration:none;font-family:'Source Sans 3',sans-serif;font-size:14px;letter-spacing:.5px;transition:color .2s}}
.top-nav a:hover{{color:#fff}}
.top-nav .book-title{{font-family:'Playfair Display',serif;font-style:italic;color:rgba(255,255,255,.5);font-size:13px}}

/* Chapter header */
.chapter-header{{background:linear-gradient(135deg,#8B3A4A 0%,#6B2A3A 40%,#4A1A2A 100%);color:#fff;text-align:center;padding:64px 40px 56px;position:relative;overflow:hidden}}
.chapter-header::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 50%,rgba(212,114,106,.15) 0%,transparent 70%),radial-gradient(ellipse at 70% 30%,rgba(196,148,74,.1) 0%,transparent 60%);pointer-events:none}}
.chapter-header-inner{{position:relative;z-index:1;max-width:720px;margin:0 auto}}
.part-label{{font-size:12px;font-weight:300;letter-spacing:4px;text-transform:uppercase;color:rgba(255,255,255,.5);margin-bottom:18px}}
.chapter-title{{font-family:'Playfair Display',serif;font-size:38px;font-weight:700;line-height:1.2;margin-bottom:0}}

/* Content */
.content{{max-width:720px;margin:0 auto;padding:56px 40px 48px}}
.content p{{margin-bottom:18px;text-align:justify;hyphens:auto}}
.content h3{{font-family:'Playfair Display',serif;font-size:25px;font-weight:600;color:var(--rose);margin-top:52px;margin-bottom:18px;padding-top:28px;border-top:1px solid var(--divider)}}
.content h3:first-child{{border-top:none;padding-top:0;margin-top:0}}
.content h4{{font-family:'Playfair Display',serif;font-size:20px;font-weight:600;color:var(--dark);margin-top:36px;margin-bottom:14px}}
.content a{{color:var(--coral);text-decoration:none;border-bottom:1px solid rgba(212,114,106,.3);transition:border-color .2s}}
.content a:hover{{border-color:var(--coral)}}
.content sup{{font-size:11px;color:var(--gold);font-weight:600}}
.content em{{font-style:italic}}
.content strong{{font-weight:600;color:var(--dark)}}

/* Pull quote */
.pq{{font-family:'Playfair Display',serif;font-size:21px;font-style:italic;color:var(--rose);text-align:center;padding:28px 36px;margin:36px 0;line-height:1.55}}
.pq::before,.pq::after{{content:'';display:block;width:56px;height:2px;background:linear-gradient(90deg,transparent,var(--coral),transparent);margin:0 auto}}
.pq::before{{margin-bottom:20px}}.pq::after{{margin-top:20px}}

/* Highlight box */
.hl{{background:var(--hl);border-left:3px solid var(--gold);padding:22px 26px;margin:28px 0;border-radius:0 8px 8px 0;font-size:15.5px;line-height:1.75}}
.hl strong{{color:var(--dark)}}

/* Footnotes */
.footnote{{font-size:14px;color:var(--light);font-style:italic;margin:18px 0;padding-left:16px;border-left:2px solid var(--divider)}}

/* Table */
.table-wrap{{overflow-x:auto;margin:28px 0}}
.table-wrap table{{width:100%;border-collapse:collapse;font-size:15px}}
.table-wrap th{{background:var(--rose);color:#fff;padding:10px 14px;text-align:left;font-weight:600;font-size:14px}}
.table-wrap td{{padding:10px 14px;border-bottom:1px solid var(--divider)}}
.table-wrap tr:nth-child(even) td{{background:rgba(253,248,240,.5)}}

/* Chapter figure */
.chapter-figure{{margin:36px 0;text-align:center}}
.chapter-figure img{{max-width:100%;border-radius:10px;box-shadow:0 4px 24px rgba(0,0,0,.08)}}

/* Chapter nav */
.chapter-nav{{display:flex;justify-content:space-between;align-items:stretch;gap:20px;max-width:720px;margin:0 auto;padding:48px 40px 56px}}
.chapter-nav a{{display:flex;flex-direction:column;justify-content:center;text-decoration:none;padding:20px 24px;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.04);border:1px solid var(--divider);transition:all .2s;flex:1;max-width:48%}}
.chapter-nav a:hover{{box-shadow:0 4px 20px rgba(0,0,0,.08);border-color:var(--coral);transform:translateY(-2px)}}
.nav-prev{{text-align:left}}
.nav-next{{text-align:right}}
.nav-arrow{{font-size:20px;color:var(--coral);display:block;margin-bottom:4px}}
.nav-label{{font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--gold);display:block;margin-bottom:4px}}
.nav-title{{font-family:'Playfair Display',serif;font-size:15px;color:var(--dark);line-height:1.35;display:block}}
.nav-disabled{{visibility:hidden;flex:1}}

/* Divider */
.pdiv{{text-align:center;padding:48px 0 0}}
.pdiv span{{display:inline-block;width:180px;height:1px;background:linear-gradient(90deg,transparent,var(--coral),transparent);position:relative}}
.pdiv span::after{{content:'\\2767';position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--cream);padding:0 12px;color:var(--coral);font-size:17px}}

/* Footer */
footer{{background:var(--dark);color:rgba(255,255,255,.6);text-align:center;padding:36px;font-size:13px}}
footer strong{{color:rgba(255,255,255,.9)}}
footer a{{color:var(--coral);text-decoration:none}}

/* Animations */
.fade-in{{opacity:0;transform:translateY(20px);animation:fadeIn .6s ease forwards}}
@keyframes fadeIn{{to{{opacity:1;transform:translateY(0)}}}}
.content>*{{opacity:0;transform:translateY(12px)}}

/* Responsive */
@media(max-width:768px){{
    .chapter-header{{padding:44px 22px 38px}}
    .chapter-title{{font-size:28px}}
    .content{{padding:36px 22px 36px}}
    .content h3{{font-size:21px}}
    .pq{{font-size:18px;padding:22px 14px}}
    .chapter-nav{{padding:28px 22px 36px;gap:12px}}
    .chapter-nav a{{padding:14px 16px}}
    .nav-title{{font-size:13px}}
    .top-nav{{padding:10px 18px}}
    .top-nav .book-title{{display:none}}
}}
@media(max-width:480px){{
    .chapter-header{{padding:36px 16px 30px}}
    .chapter-title{{font-size:24px}}
    .content{{padding:28px 16px 28px}}
    .chapter-nav{{flex-direction:column}}
    .chapter-nav a{{max-width:100%}}
    .nav-disabled{{display:none}}
}}
@media print{{
    .top-nav,.progress-bar,.chapter-nav{{display:none}}
    .chapter-header{{background:#fff;color:#000;padding:24px 0}}
    .chapter-title{{color:#000}}
    body{{font-size:12pt}}
}}
</style>
</head>
<body>

<div class="progress-bar" id="progressBar"></div>

<nav class="top-nav">
    <a href="../oxytocin.html">&larr; The Oxytocin Story</a>
    <span class="book-title">The Oxytocin Story &mdash; Justin Jeon</span>
    <a href="../oxytocin.html#toc">Table of Contents</a>
</nav>

<header class="chapter-header">
    <div class="chapter-header-inner fade-in">
        <div class="part-label">{chapter["part_label"]}</div>
        <h1 class="chapter-title">{chapter["title"]}</h1>
    </div>
</header>

<main class="content" id="chapterContent">
{figure_html}
{content_html}
</main>

<div class="pdiv"><span></span></div>

<nav class="chapter-nav">
    {prev_link}
    {next_link}
</nav>

<footer>
    <strong>The Oxytocin Story</strong> &mdash; by <a href="../">Justin Jeon</a>, Professor, Yonsei University<br>
    <span style="font-size:11px;margin-top:6px;display:inline-block">&copy; Justin Jeon. English translation.</span>
</footer>

<script>
// Reading progress bar
window.addEventListener('scroll',function(){{
    var h=document.documentElement,b=document.body;
    var st=h.scrollTop||b.scrollTop;
    var sh=h.scrollHeight||b.scrollHeight;
    var ch=h.clientHeight;
    var pct=(st/(sh-ch))*100;
    document.getElementById('progressBar').style.width=pct+'%';
}});
// Scroll-triggered fade-in for content elements
(function(){{
    var els=document.querySelectorAll('#chapterContent > *');
    var observer=new IntersectionObserver(function(entries){{
        entries.forEach(function(e){{
            if(e.isIntersecting){{
                e.target.style.opacity='1';
                e.target.style.transform='translateY(0)';
                e.target.style.transition='opacity .5s ease, transform .5s ease';
                observer.unobserve(e.target);
            }}
        }});
    }},{{threshold:0.1,rootMargin:'0px 0px -40px 0px'}});
    els.forEach(function(el){{observer.observe(el);}});
}})();
</script>

</body>
</html>'''


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    os.makedirs(BOOK_DIR, exist_ok=True)

    print("Reading markdown files...")
    file_contents = read_source_files()
    print(f"  Read {len(file_contents)} files")

    print("Extracting chapters...")
    chapters = []

    for web_num, slug, title, part_label, file_idx, heading_regex in CHAPTER_DEFS:
        content = extract_chapter_content(file_contents[file_idx], heading_regex, file_idx)
        if not content:
            print(f"  WARNING: No content found for [{slug}] in file {MD_FILES[file_idx]}")
        chapters.append({
            'num': web_num,
            'slug': slug,
            'title': title,
            'part_label': part_label,
            'content': content,
            'filename': f"{slug}.html",
        })

    # ── Afterword ──
    p8_text = file_contents[7]  # 08_part8_closing_appendix.md
    afterword_match = re.search(r'# Afterword:?\s*(.*?)\n(.*?)(?=\n# Appendix|\Z)', p8_text, re.DOTALL)
    if afterword_match:
        content = afterword_match.group(2).strip()
        chapters.append({
            'num': 38,
            'slug': '37-afterword',
            'title': 'Afterword: The Health of Our Nation Is at Risk',
            'part_label': 'Afterword',
            'content': content,
            'filename': '37-afterword.html',
        })
    else:
        print("  WARNING: Afterword not found")

    # ── Appendix ──
    appendix_match = re.search(r'# Appendix:?\s*(.*?)\n(.*?)(?=\n#{1,2}\s*References|\Z)', p8_text, re.DOTALL)
    if appendix_match:
        content = appendix_match.group(2).strip()
        chapters.append({
            'num': 39,
            'slug': '38-appendix',
            'title': 'Appendix: The Oxytocin & Cortisol Lifestyle Questionnaires',
            'part_label': 'Appendix',
            'content': content,
            'filename': '38-appendix.html',
        })
    else:
        print("  WARNING: Appendix not found")

    # ── References ──
    ref_text = file_contents[8]  # 09_references.md
    # Also grab references from part8 file
    p8_ref_match = re.search(r'## References\s*\n(.*?)$', p8_text, re.DOTALL)
    combined_refs = ref_text
    if p8_ref_match:
        combined_refs += "\n\n" + p8_ref_match.group(1)

    if combined_refs.strip():
        chapters.append({
            'num': 40,
            'slug': '39-references',
            'title': 'References',
            'part_label': 'References',
            'content': combined_refs.strip(),
            'filename': '39-references.html',
        })

    print(f"  Total chapters: {len(chapters)}")
    for ch in chapters:
        content_len = len(ch['content']) if ch['content'] else 0
        print(f"    [{ch['slug']}] {ch['title'][:60]}... ({content_len:,} chars)")

    print("\nGenerating HTML files...")
    files_created = 0
    for i, ch in enumerate(chapters):
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i < len(chapters) - 1 else None
        html_content = get_chapter_html(ch, prev_ch, next_ch)
        filepath = os.path.join(BOOK_DIR, ch['filename'])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        files_created += 1
        print(f"  Created: {ch['filename']}")

    print(f"\n{'='*60}")
    print(f"  Total files created: {files_created}")
    print(f"  Output directory: {BOOK_DIR}")
    print(f"{'='*60}")

    return chapters


if __name__ == '__main__':
    chapters = main()
