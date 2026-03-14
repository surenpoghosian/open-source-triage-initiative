# NOTIFICATION: THE AUTHOR USED ARTIFICIAL INTELLIGENCE FOR THE GENERATION OF THE SCRIPT BELOW
# IT SERVES AS A NICE WAY TO REPRESENT THE DATA AND THE RESULTS OF CONTRIBUTIONS
# THERE IS NO INTENT OF PERSONIFICATION OF A SYNTHETICALLY INITIATED PIECE OF SOFTWARE
import json
import re
from collections import defaultdict

with open("data.json") as f:
    data = json.load(f)

members = data["members"]
triaged_issues = data.get("issues", [])
projects = data.get("projects", [])

issues_by_month = defaultdict(int)
for i in triaged_issues:
    issues_by_month[i["date"]] += 1

members_by_month = defaultdict(int)
for m in members:
    members_by_month[m["joined"]] += 1

all_months_set = set(issues_by_month) | set(members_by_month)
monthly_order = [e["month"] for e in data.get("monthly", [])]
for mo in sorted(all_months_set):
    if mo not in monthly_order:
        monthly_order.append(mo)

months = monthly_order
monthly_issues = [issues_by_month.get(m, 0) for m in months]

cumulative_members = []
running = 0
for m in months:
    running += members_by_month.get(m, 0)
    cumulative_members.append(running)

member_counts = cumulative_members


total_issues_triaged = len(triaged_issues)
active_members = len(members)

import urllib.parse

def quickchart_url(title, labels, values):
    max_val = max(values + [1])
    chart = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": title,
                "data": values,
                "fill": False,
                "tension": 0.3
            }]
        },
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "ticks": {"stepSize": 1},
                    "max": max_val + 1
                }
            },
            "plugins": {"legend": {"display": False}}
        }
    }
    encoded = urllib.parse.quote(json.dumps(chart), safe="")
    return f"https://quickchart.io/chart?c={encoded}&backgroundColor=white"

issues_chart = f"![Issues Triaged]({quickchart_url('Issues Triaged', months, monthly_issues)})"
members_chart = f"![Members]({quickchart_url('Members', months, member_counts)})"

def member_issue_count(github):
    return len([i for i in triaged_issues if i["triaged_by"] == github])

summary_rows = "\n".join(
    f"| {m['name']} | [{m['github']}](https://github.com/{m['github']}) | {member_issue_count(m['github'])} |"
    for m in members
)
summary_table = f"| Name | GitHub | Issues Triaged |\n|---|---|---|\n{summary_rows if summary_rows else '| — | — | — |'}"

members_detail = ""
for m in members:
    github = m["github"]
    member_issues = [i for i in triaged_issues if i["triaged_by"] == github]
    count = member_issue_count(github)
    rows = "\n".join(
        f"| [{i['id']}]({i['url']}) | {i['title']} | {i['project']} | {i['date']} | {i['outcome']} |"
        for i in member_issues
    )
    table = f"| Issue | Title | Project | Date | Outcome |\n|---|---|---|---|---|\n{rows if rows else '| — | — | — | — | — |'}"
    members_detail += f"### [{m['name']}](https://github.com/{github})\nJoined: {m['joined']} · Issues triaged: {count}\n\n{table}\n\n"

members_block = f"{summary_table}\n\n{members_detail.strip()}"

links_lines = ["- [research.am](https://research.am)"] + [
    f"- [{p['name']}]({p['url']})" for p in projects
]
links_block = "\n".join(links_lines)

projects_covered = ", ".join(p["name"] for p in projects) if projects else "—"

with open("README.md") as f:
    readme = f.read()

readme = re.sub(
    r'Issues triaged over time:\n\n!\[.*?\]\(.*?\)',
    f'Issues triaged over time:\n\n{issues_chart}',
    readme, flags=re.DOTALL
)
readme = re.sub(
    r'Total members over time:\n\n!\[.*?\]\(.*?\)',
    f'Total members over time:\n\n{members_chart}',
    readme, flags=re.DOTALL
)
readme = re.sub(
    r'\| Projects covered \|.*?\|',
    f'| Projects covered | {projects_covered} |',
    readme
)
readme = re.sub(
    r'\| Issues triaged \|.*?\|',
    f'| Issues triaged | {total_issues_triaged} |',
    readme
)
readme = re.sub(
    r'\| Active members \|.*?\|',
    f'| Active members | {active_members} |',
    readme
)
readme = re.sub(
    r'(## Members\n\n).*?(\n## )',
    lambda m: m.group(1) + members_block + "\n\n" + m.group(2).lstrip("\n"),
    readme, flags=re.DOTALL
)
readme = re.sub(
    r'(## Links\n).*',
    f'## Links\n{links_block}',
    readme, flags=re.DOTALL
)

with open("README.md", "w") as f:
    f.write(readme)

print("README.md updated.")
