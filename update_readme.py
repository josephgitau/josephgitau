import requests
from datetime import datetime

username = "Joseph_gitau"
url = f"https://api.zindi.africa/v1/users/{username}"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# Fetch user data
r = requests.get(url, headers=headers)
data = r.json()['data']

# Use GitHub avatar as fallback if no Zindi avatar
avatar = data.get('big_avatar') or "https://github.com/josephgitau.png?size=200"
country = (data.get('country') or 'Kenya').replace(' ', '%20')

# Format stats in a table (avatar left, stats right)
stats_md = f"""
<div align="center">

## 📈 Live Zindi Stats

<table>
<tr>
<td width="250" align="center">
  <img src="{avatar}" width="200" style="border-radius:50%;"/>
</td>
<td>

![Rank](https://img.shields.io/badge/🏆%20Rank-{data['rank']}-blueviolet?style=for-the-badge)<br>
![Points](https://img.shields.io/badge/⭐%20Points-{data['points']}-ff69b4?style=for-the-badge)<br>
![Best Rank](https://img.shields.io/badge/🥇%20Best%20Rank-{data['best_rank']}-brightgreen?style=for-the-badge)<br>
![Country](https://img.shields.io/badge/🌍%20Country-{country}-orange?style=for-the-badge)<br><br>

<!-- 🏅 Medals -->
<div style="display:flex;justify-content:center;gap:25px;margin-top:15px;">
  <img src="https://img.shields.io/badge/🥇%20Gold-{data['user_medals_summary_gold_count']}-FFD700?style=for-the-badge" height="60"/>
  <img src="https://img.shields.io/badge/🥈%20Silver-{data['user_medals_summary_silver_count']}-C0C0C0?style=for-the-badge" height="60"/>
  <img src="https://img.shields.io/badge/🥉%20Bronze-{data['user_medals_summary_bronze_count']}-CD7F32?style=for-the-badge" height="60"/>
</div>

</td>
</tr>
</table>

<br>

🔗 **[View full profile on Zindi →](https://zindi.africa/users/Joseph_gitau)**

_Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_

</div>
"""

# Update README.md
with open("readme.md", "r", encoding="utf-8") as f:
    readme = f.read()

start_marker = "<!--ZINDI_STATS_START-->"
end_marker = "<!--ZINDI_STATS_END-->"
before = readme.split(start_marker)[0]
after = readme.split(end_marker)[-1]
new_readme = f"{before}{start_marker}\n{stats_md}\n{end_marker}{after}"

with open("readme.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print(f"✅ Zindi stats updated for {username} — Rank: {data['rank']}, Points: {data['points']}")
