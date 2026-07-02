"""
World Cup 2026 Fantasy Football Dashboard
==========================================

Usage:
    python worldcup_dashboard.py
    → generates index.html
"""

from datetime import datetime, timezone, date
from collections import defaultdict
from data.data_processor import PARSED_WC_FIXTURES_PATH
import json

# ─────────────────────────────────────────────────────────────────────────────
# 1. YOUR GROUP — edit names and teams
# ─────────────────────────────────────────────────────────────────────────────
GROUP_MEMBERS = {
    "Patrick": ["Colombia", "Brazil", "Germany", "Japan", "Côte d’Ivoire", "Ghana"],
    "Indre":   ["Colombia", "Spain", "Argentina", "Switzerland", "Norway", "New Zealand", "Ecuador"],
    "Erin": ["Colombia", "France", "Belgium", "Australia", "Scotland", "Sweden", "Cabo Verde"],
    "Javier":  ["Colombia", "England", "Mexico", "Morocco", "South Africa", "Czechia", "Croatia"],
    "Gillian":  ["Colombia", "Portugal", "Netherlands", "Korea Republic", "Egypt", "Türkiye", "Congo DR", "Senegal"],
}

MEMBER_LOOKUP = {
    'Brazil': ['Patrick',0],
    'Germany': ['Patrick',0],
    'Japan': ['Patrick',0],
    'Côte d’Ivoire': ['Patrick',0],
    'Ghana': ['Patrick',0],
    'Spain': ['Indre',0],
    'Argentina': ['Indre',0],
    'Switzerland': ['Indre',0],
    'Norway': ['Indre',0],
    'New Zealand': ['Indre',0],
    'Ecuador': ['Indre',1],
    'France': ['Erin',0],
    'Belgium': ['Erin',0],
    'Australia': ['Erin',0],
    'Scotland': ['Erin',0],
    'Sweden': ['Erin',0],
    'Cabo Verde': ['Erin',1],
    'England': ['Javier',0],
    'Mexico': ['Javier',0],
    'Morocco': ['Javier',0],
    'South Africa': ['Javier',0],
    'Czechia': ['Javier',0],
    'Croatia': ['Javier',1],
    'Portugal': ['Gill',0],
    'Netherlands': ['Gill',0],
    'Korea Republic': ['Gill',0],
    'Egypt': ['Gill',0],
    'Türkiye': ['Gill',0],
    'Congo DR': ['Gill',1],
    'Senegal': ['Gill',1],
  }

COUNTRIES = [
    "Haiti",
    "Türkiye",
    "Ecuador",
    "Egypt",
    "Croatia",
    "Korea Republic",
    "Brazil",
    "Canada",
    "Congo DR",
    "Qatar",
    "Argentina",
    "Portugal",
    "New Zealand",
    "Curaçao",
    "Côte d’Ivoire",
    "Spain",
    "Ghana",
    "Paraguay",
    "Scotland",
    "Netherlands",
    "Austria",
    "Morocco",
    "Algeria",
    "Norway",
    "South Africa",
    "Sweden",
    "Senegal",
    "Czechia",
    "Bosnia and Herzegovina",
    "Germany",
    "Cabo Verde",
    "Uzbekistan",
    "Switzerland",
    "Colombia",
    "Australia",
    "Uruguay",
    "Belgium",
    "Iraq",
    "Tunisia",
    "Mexico",
    "Japan",
    "United States",
    "Jordan",
    "Iran",
    "England",
    "France",
    "Saudi Arabia",
    "Panama"
]

ELIMINATED = [
    "Panama",
    "Haiti",
    "Tunisia",
    "Türkiye",
    "Jordan",
    "Qatar",
    "Czechia",
    "Curaçao",
    "Iraq",
    "Uruguay",
    "Saudi Arabia",
    "New Zealand",
    "Scotland",
    "Uzbekistan",
    "Korea Republic",
    "Iran",
    "South Africa",
    "Japan",
    "Germany",
    "Netherlands",
    "Congo DR",
    "Senegal",
    "Ecuador",
    "Sweden"
]
# ─────────────────────────────────────────────────────────────────────────────
# 2. SCORING RULES
# ─────────────────────────────────────────────────────────────────────────────
POINTS = {
    "win":           3,
    "draw":          1,
    "loss":          0,
    "clean_sheet":   1,   # per clean sheet kept
    "goal":          1,   # per goal scored
    "red_card":     -1,   # per red card received
    "penalties_win": 2,
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. MATCH RESULTS — add a new dict here after each game
#
#  Required fields:
#    date        "YYYY-MM-DD"
#    home        team name (must match exactly what you put in GROUP_MEMBERS)
#    away        team name
#    home_goals  integer
#    away_goals  integer
#
#  Optional fields (defaults to 0 if omitted):
#    home_red_cards   integer
#    away_red_cards   integer
#
#  Status is inferred automatically:
#    "upcoming" — no result yet, just add date/home/away, leave goals out entirely
#    or set status="upcoming" explicitly
#
# Example completed match:
#   {"date":"2026-06-12","home":"Brazil","away":"Mexico","home_goals":2,"away_goals":1},
#
# Example upcoming match (no score yet):
#   {"date":"2026-06-13","home":"France","away":"Germany"},
#
# ─────────────────────────────────────────────────────────────────────────────
with open(PARSED_WC_FIXTURES_PATH, "r") as file:
    MATCHES = json.load(file) 

# ─────────────────────────────────────────────────────────────────────────────
# ENGINE — no need to edit below this line
# ─────────────────────────────────────────────────────────────────────────────
OUTPUT_FILE = "index.html"

def is_complete(m):
    return "home_goals" in m and "away_goals" in m

def calc_points(m):
    """Return {home_team: pts, away_team: pts} for a completed match."""
    hg = m["home_goals"]
    ag = m["away_goals"]
    hr = m.get("home_red_cards", 0)
    ar = m.get("away_red_cards", 0)
    h_pw = m.get("penalties_win_home", 0)
    a_pw = m.get("penalties_win_away", 0)

    result = {}
    for team, scored, conceded, reds, pw in [
        (m["home"], hg, ag, hr, h_pw),
        (m["away"], ag, hg, ar, a_pw),
    ]:
        pts = 0
        if scored > conceded:   pts += POINTS["win"]
        elif scored == conceded: pts += POINTS["draw"]
        if conceded == 0:       pts += POINTS["clean_sheet"]
        pts += scored * POINTS["goal"]
        pts += reds   * POINTS["red_card"]
        pts += pw     * POINTS["penalties_win"]
        result[team] = pts
    return result


def build_member_scores():
    scores = {name: {"total": 0, "breakdown": [], "teams": teams}
              for name, teams in GROUP_MEMBERS.items()}

    team_to_members = defaultdict(list)
    for name, teams in GROUP_MEMBERS.items():
        for t in teams:
            team_to_members[t.lower()].append(name)

    for m in MATCHES:
        if not is_complete(m):
            continue
        pts_map = calc_points(m)
        for raw_team, pts in pts_map.items():
            for member in team_to_members.get(raw_team.lower(), []):
                if (raw_team == "Colombia") or (raw_team in MEMBER_LOOKUP.keys() and (MEMBER_LOOKUP[raw_team][1]==0 or (MEMBER_LOOKUP[raw_team][1]==1 and date.fromisoformat(m["date"])>date.fromisoformat("2026-06-28")))):
                  scores[member]["total"] += pts
                  scores[member]["breakdown"].append({
                      "date":    m["date"],
                      "fixture": f"{m['home']} {m['home_goals']}–{m['away_goals']} {m['away']}",
                      "team":    raw_team,
                      "pts":     pts,
                  })
    return scores


def build_group_standings():
    """Derive group standings purely from MATCHES data."""
    record = defaultdict(lambda: {"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Red Cards":0,"Pts":0})
    groups = defaultdict(set)

    for m in MATCHES:
        if m["home"] in COUNTRIES and m["away"] in COUNTRIES:
          grp = m.get("group", "Group Stage")
          groups[grp].update([m["home"], m["away"]])
          if not is_complete(m):
              continue
          hg, ag = m["home_goals"], m["away_goals"]
          h_rc, a_rc = m["home_red_cards"], m["away_red_cards"]
          for team, scored, conceded, red_cards in [(m["home"],hg,ag,h_rc),(m["away"],ag,hg,a_rc)]:
              r = record[team]
              r["P"]  += 1
              r["GF"] += scored
              r["Pts"] += scored
              r["Red Cards"] += red_cards
              r["Pts"] -= red_cards
              r["GA"] += conceded
              r["GD"] += scored - conceded
              if scored > conceded:   r["W"]+=1; r["Pts"]+=3
              elif scored == conceded: r["D"]+=1; r["Pts"]+=1
              else:                    r["L"]+=1

    result = {}
    for grp, teams in groups.items():
        table = sorted(teams, key=lambda t: (-record[t]["Pts"], -record[t]["GD"], -record[t]["GF"]))
        result[grp] = [(i+1, t, record[t]) for i, t in enumerate(table)]
    return result


# ─────────────────────────────────────────────────────────────────────────────
# HTML BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def pts_cls(p):
    return "pts-pos" if p > 0 else ("pts-neg" if p < 0 else "pts-zero")

def style_teamnames(teams_list: list)->list:
    
  team_spans = []
  for team in teams_list:
      classes = []
      if team in MEMBER_LOOKUP.keys():
        if MEMBER_LOOKUP[team][1] == 1:
            classes.append("team-new")
        if MEMBER_LOOKUP[team][0] == 0:
            classes.append("team-old")
      if team in ELIMINATED:
          classes.append("team-eliminated")

      class_attr = f' class="{" ".join(classes)}"' if classes else ""
      team_spans.append(f"<span{class_attr}>{team}</span>")
  return team_spans


def build_leaderboard_html(member_scores):
    ranked = sorted(member_scores.items(), key=lambda x: -x[1]["total"])
    html = ""
    for i, (member, data) in enumerate(ranked, 1):
        rank_cls = f"rank-{i}" if i <= 3 else ""
        rows = "".join(
            f"<tr><td>{b['date']}</td><td>{b['fixture']}</td>"
            f"<td>{b['team']}</td>"
            f"<td class='{pts_cls(b['pts'])}'>{b['pts']:+d}</td></tr>"
            for b in sorted(data["breakdown"], key=lambda x: x["date"], reverse=True)
        )
        empty_row = '<tr><td colspan="4" class="empty-row">No scored matches yet</td></tr>'
        teams_list = data["teams"]
        team_spans = style_teamnames(teams_list=teams_list)
        teams_str = " · ".join(team_spans)
        html += f"""
        <div class="lb-card {rank_cls}" onclick="toggleBreakdown(this)">
          <div class="lb-rank">{i}</div>
          <div class="lb-info">
            <div class="lb-name">{member}</div>
            <div class="lb-teams">{teams_str}</div>
            <div class="breakdown">
              <table>
                <thead><tr><th>Date</th><th>Match</th><th>Your team</th><th>Pts</th></tr></thead>
                <tbody>{rows if rows else empty_row}</tbody>
              </table>
            </div>
          </div>
          <div class="lb-score">{data['total']}</div>
        </div>"""
    return html

def _process_team_name(name: str):
    if name in MEMBER_LOOKUP.keys():
        return f"({MEMBER_LOOKUP[name][0]})"
    else:
        return ""

def build_results_html():
    done = sorted([m for m in MATCHES if is_complete(m)],
                  key=lambda m: (m["date"], m["time"]), reverse=True)
    if not done:
        return '<div class="empty">No completed matches yet</div>'
    html = ""
    for m in done:
        hr = m.get("home_red_cards", 0)
        ar = m.get("away_red_cards", 0)
        red_h = f' <span class="red-card">{"🟥"*hr}</span>' if hr else ""
        red_a = f' <span class="red-card">{"🟥"*ar}</span>' if ar else ""
        h_pw = m.get("penalties_win_home", 0)
        a_pw = m.get("penalties_win_away", 0)
        home_pen_win = f' <span class="pen-win">{" (P)"}</span>' if h_pw==1 else ""
        away_pen_win = f' <span class="pen-win">{" (P)"}</span>' if a_pw==1 else ""
        html += f"""
        <div class="fixture location">{m["location"]}</div>
        <div class="fixture-card">
          <div class="team home"><font class="member-font">{f"{_process_team_name(m['home'])} "}</font>{m['home']}{red_h}</div>
          <div class="score-col">
            <div class="score">{home_pen_win}{m['home_goals']} – {m['away_goals']}{away_pen_win}</div>
            <div class="fixture-meta">{m['date']}, {m['time']} <span class="badge badge-ft">FT</span></div>
          </div>
          <div class="team away">{m['away']}{red_a}<font class="member-font">{f" {_process_team_name(m['away'])}"}</font></div>
        </div>"""
    return html


def build_fixtures_html():
    upcoming = sorted([m for m in MATCHES if not is_complete(m)],
                      key=lambda m: m["date"])
    if not upcoming:
        return '<div class="empty">No upcoming fixtures</div>'

    by_date = defaultdict(list)
    for m in upcoming:
        by_date[m["date"]].append(m)

    html = ""
    for date in sorted(by_date.keys()):
        try:
            label = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %-d %B")
        except Exception:
            label = date
        html += f'<div class="fixture-date-group"><h3>{label}</h3>'
        for m in by_date[date]:
            time_str = m.get("time", "TBC")
            html += f"""
            <div class="fixture location">{m["location"]}</div>
            <div class="fixture-card">
              <div class="team home"><font class="member-font">{f"{_process_team_name(m['home'])} "}</font>{m['home']}</div>
              <div class="score-col">
                <div class="score vs">vs</div>
                <div class="fixture-meta"><span class="badge badge-sched">{time_str}</span></div>
              </div>
              <div class="team away">{m['away']}<font class="member-font">{f" {_process_team_name(m['away'])}"}</font></div>
            </div>"""
        html += "</div>"
    return html


def build_standings_html():
    groups = build_group_standings()
    if not groups:
        return '<div class="empty">No match data yet</div>'
    html = ""
    for grp in sorted(groups.keys()):
        html += f'<div class="group-block"><h3>{grp}</h3>'
        html += """<table class="standings-table">
          <thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th>
          <th>L</th><th>GF</th><th>GA</th><th>GD</th><th class="pts-col">Pts</th></tr></thead><tbody>"""
        for rank, team, r in groups[grp]:
            row_cls = "qualify" if rank <= 2 else ""
            html += f"""<tr class="{row_cls}">
              <td>{rank}</td><td>{team}</td><td>{r['P']}</td><td>{r['W']}</td>
              <td>{r['D']}</td><td>{r['L']}</td><td>{r['GF']}</td><td>{r['GA']}</td>
              <td>{r['GD']:+d}</td><td class="pts-col">{r['Pts']}</td></tr>"""
        html += "</tbody></table></div>"
    return html


def build_scoring_key_html():
    rows = "".join(
        f"<tr><td>{k.replace('_',' ').title()}</td>"
        f"<td class='{'pts-pos' if v>0 else 'pts-neg' if v<0 else 'pts-zero'}'>"
        f"{v:+d}</td></tr>"
        for k, v in POINTS.items()
    )
    return f"""<table class="scoring-table"><thead>
        <tr><th>Event</th><th>Points</th></tr></thead><tbody>{rows}</tbody></table>"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Cup 2026 — Draft Scores</title>
<style>
  :root {{
    --bg:      #0a0e1a;
    --surface: #111827;
    --card:    #1a2235;
    --border:  #2a3450;
    --accent:  #e8c84a;
    --accent2: #4aaee8;
    --text:    #e8eaf2;
    --muted:   #7a8099;
    --win:     #4CAF50;
    --loss:    #f44336;
    --gold:    #FFD700;
    --silver:  #C0C0C0;
    --bronze:  #CD7F32;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); min-height: 100vh; }}

  header {{
    background: linear-gradient(135deg, #0d1b2e 0%, #1a2a4a 100%);
    border-bottom: 2px solid var(--accent);
    padding: 1.4rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: .5rem;
  }}
  header h1 {{ font-size: 1.3rem; font-weight: 700; color: var(--accent); }}
  header .updated {{ font-size: .75rem; color: var(--muted); }}

  nav {{
    display: flex; gap: .5rem; padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    position: sticky; top: 0; z-index: 10;
    overflow-x: auto;
  }}
  nav button {{
    padding: .4rem 1rem; border: 1px solid var(--border);
    border-radius: 20px; background: transparent;
    color: var(--muted); cursor: pointer; font-size: .83rem;
    white-space: nowrap; transition: all .15s;
  }}
  nav button.active, nav button:hover {{
    background: var(--accent); color: #000;
    border-color: var(--accent); font-weight: 600;
  }}

  main {{ max-width: 1000px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }}
  section {{ display: none; }}
  section.visible {{ display: block; }}
  h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: var(--text); text-transform: uppercase; letter-spacing: .06em; }}

  /* ── LEADERBOARD ── */
  .leaderboard {{ display: grid; gap: .85rem; }}
  .lb-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.1rem 1.4rem;
    display: flex; align-items: center; gap: 1.1rem;
    cursor: pointer; transition: border-color .15s;
  }}
  .lb-card:hover {{ border-color: var(--accent2); }}
  .lb-card.rank-1 {{ border-color: var(--gold); }}
  .lb-card.rank-2 {{ border-color: var(--silver); }}
  .lb-card.rank-3 {{ border-color: var(--bronze); }}
  .lb-rank {{ font-size: 1.4rem; font-weight: 800; width: 2rem; text-align: center; color: var(--muted); }}
  .rank-1 .lb-rank {{ color: var(--gold); }}
  .rank-2 .lb-rank {{ color: var(--silver); }}
  .rank-3 .lb-rank {{ color: var(--bronze); }}
  .lb-info {{ flex: 1; min-width: 0; }}
  .lb-name {{ font-size: 1rem; font-weight: 600; }}
  .lb-teams {{ font-size: .75rem; color: var(--muted); margin-top: .2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .lb-score {{ font-size: 2rem; font-weight: 800; color: var(--accent); flex-shrink: 0; }}
  .breakdown {{ display: none; margin-top: .8rem; border-top: 1px solid var(--border); padding-top: .7rem; }}
  .breakdown.open {{ display: block; }}
  .breakdown table {{ width: 100%; font-size: .78rem; border-collapse: collapse; }}
  .breakdown thead th {{ text-align: left; color: var(--muted); padding: .25rem .4rem; border-bottom: 1px solid var(--border); font-weight: 500; }}
  .breakdown tbody td {{ padding: .3rem .4rem; border-bottom: 1px solid #1a2540; }}
  .empty-row {{ color: var(--muted); font-style: italic; }}

  /* ── FIXTURES & RESULTS ── */
  .results-grid {{ display: grid; gap: .65rem; }}
  .fixture-date-group {{ margin-bottom: 1.4rem; }}
  .fixture-date-group h3 {{
    font-size: .75rem; text-transform: uppercase; letter-spacing: .08em;
    color: var(--muted); margin-bottom: .55rem; padding-bottom: .3rem;
    border-bottom: 1px solid var(--border); font-weight: 500;
  }}
  .fixture-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: .85rem 1.1rem;
    display: grid; grid-template-columns: 1fr auto 1fr;
    align-items: center; gap: .5rem;
  }}
  .team {{ font-size: .88rem; font-weight: 600; }}
  .team.home {{ text-align: right; }}
  .team.away {{ text-align: left; }}
  .member-font {{ color: #6C5185; font-style: italic; }}
  .team-new {{ font-style: italic; }}
  .team-old {{ font-weight: bold; }}
  .team-eliminated {{ text-decoration: line-through; text-decoration-color: red; }}
  .score-col {{ text-align: center; }}
  .score {{ font-size: 1.2rem; font-weight: 800; color: var(--accent); min-width: 3.5rem; }}
  .score.vs {{ font-size: .9rem; color: var(--muted); font-weight: 400; }}
  .fixture.location {{ font-size: .9rem; color: var(--muted); font-weight: 400; text-align: center; padding-top: .50rem}}
  .fixture-meta {{ font-size: .7rem; color: var(--muted); margin-top: .2rem; }}
  .badge {{
    display: inline-block; padding: .12rem .45rem;
    border-radius: 4px; font-size: .67rem; font-weight: 600;
  }}
  .badge-ft    {{ background: #2a3450; color: var(--muted); }}
  .badge-sched {{ background: #1a2a3a; color: var(--accent2); border: 1px solid #2a3a5a; }}

  /* ── STANDINGS ── */
  .group-block {{ margin-bottom: 1.8rem; }}
  .group-block h3 {{
    font-size: .85rem; font-weight: 700; color: var(--accent2);
    margin-bottom: .55rem; letter-spacing: .04em; text-transform: uppercase;
  }}
  .standings-table {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
  .standings-table th {{
    text-align: left; padding: .38rem .55rem;
    color: var(--muted); border-bottom: 1px solid var(--border); font-weight: 500;
  }}
  .standings-table td {{ padding: .42rem .55rem; border-bottom: 1px solid #1a2540; }}
  .standings-table tr:hover td {{ background: #1e2a3a; }}
  .standings-table .pts-col {{ font-weight: 700; color: var(--accent); }}
  .standings-table .qualify td:first-child {{ border-left: 3px solid var(--win); }}

  /* ── SCORING KEY ── */
  .scoring-table {{ border-collapse: collapse; font-size: .85rem; min-width: 200px; }}
  .scoring-table th {{
    text-align: left; padding: .4rem .8rem;
    border-bottom: 1px solid var(--border); color: var(--muted); font-weight: 500;
  }}
  .scoring-table td {{ padding: .42rem .8rem; border-bottom: 1px solid #1a2540; }}
  .scoring-table tr:last-child td {{ border-bottom: none; }}
  .scoring-table td:last-child {{ font-weight: 700; text-align: right; }}
  .key-card {{
    display: inline-block; background: var(--card);
    border: 1px solid var(--border); border-radius: 10px;
    padding: 1rem 1.2rem; margin-bottom: 1rem;
  }}
  .how-to {{ font-size: .82rem; color: var(--muted); line-height: 1.7; max-width: 540px; white-space: pre; }}
  .how-to code {{
    background: #1e2a3a; color: var(--accent2); padding: .1rem .35rem;
    border-radius: 3px; font-size: .8rem;
  }}
  .how-to h3 {{ font-size: .85rem; color: var(--text); margin: 1rem 0 .4rem; font-weight: 600; }}

  /* shared */
  .pts-pos {{ color: #4CAF50; font-weight: 600; }}
  .pts-neg {{ color: #f44336; font-weight: 600; }}
  .pts-zero {{ color: var(--muted); }}
  .empty {{ color: var(--muted); text-align: center; padding: 3rem; font-size: .88rem; }}
  .red-card {{ font-size: .75rem; }}
  .pen-win {{ font-size: .75rem; }}
</style>
</head>
<body>

<header>
  <h1>⚽ World Cup 2026 — Draft Scores</h1>
  <div class="updated">Last updated: {updated}</div>
</header>

<nav>
  <button class="active" onclick="show('leaderboard',this)">🏆 Leaderboard</button>
  <button onclick="show('results',this)">📋 Results</button>
  <button onclick="show('fixtures',this)">📅 Fixtures</button>
  <button onclick="show('standings',this)">📊 Standings</button>
  <button onclick="show('howto',this)">ℹ️ Scoring Explained</button>
</nav>

<main>

<section id="leaderboard" class="visible">
  <h2>Draft standings</h2>
  <div class="leaderboard">{leaderboard_html}</div>
</section>

<section id="results">
  <h2>Completed matches</h2>
  <div class="results-grid">{results_html}</div>
</section>

<section id="fixtures">
  <h2>Upcoming fixtures</h2>
  {fixtures_html}
</section>

<section id="standings">
  <h2>Group standings</h2>
  {standings_html}
</section>

<section id="howto">
  <h2>Scoring key</h2>
  <div class="key-card">{scoring_key_html}</div>

  <div class="how-to">
    <h3>Results</h3>
    Teams will receive the typical <code>+3</code>, <code>+1</code>, and <code>0</code> points for a
    win, draw, and loss respectively.
    <h3>Penalty Shootout</h3>
    If teams are level after 120 minutes, the game will go to a penalty shootout.
    Both teams will receive <code>+1</code> points due to finishing the regular play level.
    The winning team in the shootout will recieve <code>+2</code> points for a <code>Penalties Win</code>
    to make up the total of <code>+3</code> points for a win.
    <h3>Extra points</h3>
    Teams will receive an extra <code>+1</code> point for a <code>Goal</code> or a <code>Clean Sheet</code>.
    They will receive <code>-1</code> point for any <code>Red Card</code> a player in their team receives.
  </div>
</section>

</main>

<script>
function show(id, btn) {{
  document.querySelectorAll('section').forEach(s => s.classList.remove('visible'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('visible');
  btn.classList.add('active');
}}
function toggleBreakdown(el) {{
  el.querySelector('.breakdown').classList.toggle('open');
}}
</script>
</body>
</html>
"""


def main():
    member_scores = build_member_scores()

    html = HTML_TEMPLATE.format(
        updated          = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC"),
        leaderboard_html = build_leaderboard_html(member_scores),
        results_html     = build_results_html(),
        fixtures_html    = build_fixtures_html(),
        standings_html   = build_standings_html(),
        scoring_key_html = build_scoring_key_html(),
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"✅  Generated {OUTPUT_FILE}")
    ranked = sorted(member_scores.items(), key=lambda x: -x[1]["total"])
    print("\nCurrent leaderboard:")
    for i, (m, d) in enumerate(ranked, 1):
        print(f"  {i}. {m}: {d['total']} pts")


if __name__ == "__main__":
    main()
