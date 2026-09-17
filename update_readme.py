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


profile = find_user("legacy")
if profile is None:
    raise RuntimeError(f"Could not find {USERNAME} on the Zindi leaderboard API")

profile_detail = get_json(f"/users/{USERNAME}").get("data", {})

country = profile.get("country") or {}
country_name = country.get("name") or "Kenya"
country_iso = (country.get("iso_code") or profile.get("countrycode") or "KE").upper()

# The country filter makes the current API include the user's country rank.
all_time = find_user("legacy", country_name) or profile

season_payload = get_json("/seasonal_leaderboards")
season_key = season_payload.get("meta", {}).get("default_leaderboard")
season_rows = season_payload.get("data", [])
season = next((row for row in season_rows if row.get("key") == season_key), None)
if season is None and season_rows:
    season = season_rows[0]
    season_key = season.get("key")
if not season_key:
    raise RuntimeError("Could not find the active Zindi seasonal leaderboard")

season_name = (season or {}).get("name") or season_key
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
country_name = html.escape(country_name)
country_flag = html.escape(country.get("emoji_flag") or "🌍")
country_iso = html.escape(country_iso)
season_name = html.escape(season_name)
season_url = (
    f"{LEADERBOARD_URL}?leaderboard={quote(str(season_key), safe='')}"
    f"&country={quote(country_iso, safe='')}"
)
all_time_url = f"{LEADERBOARD_URL}?leaderboard=all-time&country={quote(country_iso, safe='')}"
season_share_url = seasonal.get("rank_share_url")
share_link = (
    f' · <a href="{html.escape(season_share_url, quote=True)}">Share {season_name} rank</a>'
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

<p><sub>All-Time rewards long-term consistency. Seasonal shows current form and resets annually.</sub></p>

<img src="{avatar}" width="110" alt="Joseph Gitau on Zindi"/>

<table>
<thead>
<tr><th>Leaderboard</th><th>Global</th><th>{country_flag} {country_name} rank</th><th>Points</th></tr>
</thead>
<tbody>
<tr><td><strong>🏆 All-Time</strong></td><td><strong>{format_rank(all_time.get("rank"))}</strong></td><td><strong>{format_rank(all_time.get("country_rank"))}</strong></td><td>{format_number(all_time.get("points"))}</td></tr>
<tr><td><strong>⚡ {season_name}</strong></td><td><strong>{format_rank(seasonal.get("rank"))}</strong></td><td><strong>{format_rank(seasonal.get("country_rank"))}</strong></td><td>{format_number(seasonal.get("points"))}</td></tr>
</tbody>
</table>

<p>🏅 <strong>Career medals:</strong> {gold} gold · {silver} silver · {bronze} bronze</p>
<p><strong>Best global rank:</strong> {best_rank} · <strong>Activity:</strong> {competitions} competitions · {hackathons} hackathons · {submissions} submissions</p>

<p><a href="{all_time_url}">All-Time leaderboard</a> · <a href="{season_url}">{season_name} leaderboard</a> · <a href="{PROFILE_URL}">Zindi profile</a>{share_link}</p>

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
