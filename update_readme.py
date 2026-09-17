import html
from datetime import UTC, datetime
from urllib.parse import quote

import requests


API_BASE = "https://api.zindi.world/v1"
USERNAME = "Joseph_gitau"
PROFILE_URL = f"https://zindi.world/users/{USERNAME}"
LEADERBOARD_URL = "https://zindi.world/community"

session = requests.Session()
session.headers.update(
    {
        "Accept": "application/json",
        "User-Agent": "josephgitau-profile-readme/2.0",
    }
)


def get_json(path, params=None):
    response = session.get(f"{API_BASE}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def find_user(leaderboard_type, country=None):
    params = {
        "page": 0,
        "per_page": 50,
        "query": USERNAME,
        "leaderboard_type": leaderboard_type,
    }
    if country:
        params["country"] = country

    rows = get_json("/users", params).get("data", [])
    return next(
        (row for row in rows if row.get("username", "").lower() == USERNAME.lower()),
        None,
    )


def format_number(value):
    return "—" if value is None else f"{int(value):,}"


def format_rank(value):
    return "—" if value is None else f"#{int(value):,}"


def badge_part(value):
    # Shields uses a double hyphen to preserve hyphens inside a label or value.
    return quote(str(value), safe="").replace("-", "--")


def badge(label, value, color):
    label_text = badge_part(label)
    value_text = badge_part(value)
    return f"https://img.shields.io/badge/{label_text}-{value_text}-{color}?style=for-the-badge"


profile = find_user("legacy")
if profile is None:
    raise RuntimeError(f"Could not find {USERNAME} on the Zindi leaderboard API")

profile_detail = get_json(f"/users/{USERNAME}").get("data", {})

country = profile.get("country") or {}
country_name_raw = country.get("name") or "Kenya"
country_iso_raw = (country.get("iso_code") or profile.get("countrycode") or "KE").upper()

# The country filter makes the current API include the user's country rank.
all_time = find_user("legacy", country_name_raw) or profile

season_payload = get_json("/seasonal_leaderboards")
season_key = season_payload.get("meta", {}).get("default_leaderboard")
season_rows = season_payload.get("data", [])
season = next((row for row in season_rows if row.get("key") == season_key), None)
if season is None and season_rows:
    season = season_rows[0]
    season_key = season.get("key")
if not season_key:
    raise RuntimeError("Could not find the active Zindi seasonal leaderboard")

season_name_raw = (season or {}).get("name") or season_key
seasonal_payload = get_json(
    f"/seasonal_leaderboards/{quote(season_key, safe='')}/seasonal_leaderboard_rankings",
    {"page": 0, "per_page": 50, "query": USERNAME},
)
seasonal_rows = seasonal_payload.get("data", [])
seasonal = next(
    (
        row
        for row in seasonal_rows
        if (row.get("competitor") or {}).get("username", "").lower()
        == USERNAME.lower()
    ),
    None,
)
if seasonal is None:
    seasonal = {}

avatar = (
    profile.get("avatar")
    or (seasonal.get("competitor") or {}).get("avatar")
    or "https://github.com/josephgitau.png?size=200"
)
avatar = html.escape(avatar, quote=True)
country_name = html.escape(country_name_raw)
country_flag = html.escape(country.get("emoji_flag") or "🌍")
country_iso = html.escape(country_iso_raw)
season_name = html.escape(season_name_raw)
season_url = (
    f"{LEADERBOARD_URL}?leaderboard={quote(str(season_key), safe='')}"
    f"&country={quote(country_iso_raw, safe='')}"
)
all_time_url = f"{LEADERBOARD_URL}?leaderboard=all-time&country={quote(country_iso_raw, safe='')}"
season_share_url = seasonal.get("rank_share_url")
share_link = (
    f'<a href="{html.escape(season_share_url, quote=True)}">'
    f'<img src="{badge("SHARE", f"{season_name_raw} RANK", "6F4BDD")}" alt="Share {season_name} rank"/></a>'
    if season_share_url
    else ""
)

gold = format_number(all_time.get("user_medals_summary_gold_count"))
silver = format_number(all_time.get("user_medals_summary_silver_count"))
bronze = format_number(all_time.get("user_medals_summary_bronze_count"))
best_rank = format_rank(profile_detail.get("best_rank") or all_time.get("rank"))
competitions = format_number(profile_detail.get("count_of_competitions"))
hackathons = format_number(profile_detail.get("count_of_hackathons"))
submissions = format_number(profile_detail.get("count_of_submissions"))
updated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

stats_md = f"""
<div align="center">

## 🏁 Zindi Leaderboard Snapshot

<p><sub>Two leaderboards. One competitive dashboard.</sub></p>

<img src="{avatar}" width="130" alt="Joseph Gitau on Zindi"/><br>
<strong>{USERNAME}</strong> · {country_flag} {country_name}

<table>
<tr><th>Leaderboard</th><th>Global</th><th>{country_flag} {country_name} rank</th><th>Points</th></tr>
<tr>
<td align="center" width="50%">
<a href="{all_time_url}"><img src="{badge("ALL-TIME", "LONG GAME", "0A66C2")}" alt="All-Time leaderboard"/></a><br><br>
<img src="{badge("GLOBAL", format_rank(all_time.get("rank")), "0A66C2")}" alt="All-Time global rank"/><br>
<img src="{badge(country_name_raw, format_rank(all_time.get("country_rank")), "00B4D8")}" alt="All-Time country rank"/><br>
<img src="{badge("POINTS", format_number(all_time.get("points")), "111827")}" alt="All-Time points"/>
</td>
<td align="center" width="50%">
<a href="{season_url}"><img src="{badge(season_name_raw, "CURRENT FORM", "6F4BDD")}" alt="Seasonal leaderboard"/></a><br><br>
<img src="{badge("GLOBAL", format_rank(seasonal.get("rank")), "6F4BDD")}" alt="Seasonal global rank"/><br>
<img src="{badge(country_name_raw, format_rank(seasonal.get("country_rank")), "F28C28")}" alt="Seasonal country rank"/><br>
<img src="{badge("POINTS", format_number(seasonal.get("points")), "00A86B")}" alt="Seasonal points"/>
</td>
</tr>
</table>

<p>
<img src="{badge("GOLD", gold, "FFD700")}" alt="Gold medals"/>
<img src="{badge("SILVER", silver, "A9A9A9")}" alt="Silver medals"/>
<img src="{badge("BRONZE", bronze, "CD7F32")}" alt="Bronze medals"/>
</p>

<p>
<img src="{badge("BEST RANK", best_rank, "228B22")}" alt="Best global rank"/>
<img src="{badge("COMPETITIONS", competitions, "0088CC")}" alt="Competitions"/>
<img src="{badge("SUBMISSIONS", submissions, "111827")}" alt="Submissions"/>
</p>

<p><a href="{all_time_url}"><img src="{badge("VIEW", "ALL-TIME", "0A66C2")}" alt="View All-Time leaderboard"/></a>
<a href="{season_url}"><img src="{badge("VIEW", season_name_raw, "6F4BDD")}" alt="View seasonal leaderboard"/></a>
<a href="{PROFILE_URL}"><img src="{badge("OPEN", "ZINDI PROFILE", "F28C28")}" alt="Open Zindi profile"/></a>
{share_link}</p>

<sub>Snapshot refreshed: {updated_at} · Country: {country_name}</sub>

</div>
"""

with open("readme.md", "r", encoding="utf-8") as file:
    readme = file.read()

start_marker = "<!--ZINDI_STATS_START-->"
end_marker = "<!--ZINDI_STATS_END-->"
if start_marker not in readme or end_marker not in readme:
    raise RuntimeError("README is missing the Zindi stats markers")

before = readme.split(start_marker, 1)[0]
after = readme.split(end_marker, 1)[1]
new_readme = f"{before}{start_marker}\n{stats_md}\n{end_marker}{after}"

with open("readme.md", "w", encoding="utf-8") as file:
    file.write(new_readme)

print(
    f"Zindi stats updated for {USERNAME}: "
    f"all-time {format_rank(all_time.get('rank'))}, "
    f"{season_name} {format_rank(seasonal.get('rank'))}"
)
