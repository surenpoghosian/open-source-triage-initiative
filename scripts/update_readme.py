import json
import re

with open("data.json") as f:
    data = json.load(f)

monthly = data["monthly"]
members = data["members"]

months = [e["month"] for e in monthly]
monthly_issues = [e["issues_triaged"] for e in monthly]
member_counts = [e["members"] for e in monthly]

max_issues = max(monthly_issues + [10])
max_members = max(member_counts + [5])

months_str = ", ".join(months)
issues_str = ", ".join(str(v) for v in monthly_issues)
members_str = ", ".join(str(v) for v in member_counts)

issues_chart = f"""```mermaid
xychart-beta
    title "Issues Triaged"
    x-axis [{months_str}]
    y-axis 0 --> {max_issues + 5}
    line [{issues_str}]
```"""

members_chart = f"""```mermaid
xychart-beta
    title "Members"
    x-axis [{months_str}]
    y-axis 0 --> {max_members + 5}
    line [{members_str}]
```"""

summary_rows = "\n".join(
    f"| {m['name']} | [{m['github']}](https://github.com/{m['github']}) | {m['issues_triaged']} |"
    for m in members
)
summary_table = f"| Name | GitHub | Issues Triaged |\n|---|---|---|\n{summary_rows if summary_rows else '| — | — | — |'}"

members_detail = ""
for m in members:
    github = m["github"]
    member_issues = [i for i in issues if i["triaged_by"] == github]
    rows = "\n".join(
        f"| [{i['id']}]({i['url']}) | {i['title']} | {i['project']} | {i['date']} | {i['outcome']} |"
        for i in member_issues
    )
    table = f"| Issue | Title | Project | Date | Outcome |\n|---|---|---|---|---|\n{rows if rows else '| — | — | — | — | — |'}"
    members_detail += f"### [{m['name']}](https://github.com/{github})\nJoined: {m['joined']} · Issues triaged: {m['issues_triaged']}\n\n{table}\n\n"

members_block = f"{summary_table}\n\n{members_detail.strip()}"

with open("README.md") as f:
    readme = f.read()

readme = re.sub(
    r'Issues triaged over time:\n\n```mermaid.*?```',
    f'Issues triaged over time:\n\n{issues_chart}',
    readme, flags=re.DOTALL
)
readme = re.sub(
    r'Total members over time:\n\n```mermaid.*?```',
    f'Total members over time:\n\n{members_chart}',
    readme, flags=re.DOTALL
)
readme = re.sub(
    r'(## Members\n\n).*?(\n## )',
    lambda m: m.group(1) + members_block + "\n\n" + m.group(2).lstrip("\n"),
    readme, flags=re.DOTALL
)

with open("README.md", "w") as f:
    f.write(readme)

print("README.md updated.")
