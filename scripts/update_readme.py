import json
import re

with open("data.json") as f:
    data = json.load(f)

monthly = data["monthly"]
members = data["members"]

months = [e["month"] for e in monthly]
issues = [e["issues_triaged"] for e in monthly]
member_counts = [e["members"] for e in monthly]

max_issues = max(issues + [10])
max_members = max(member_counts + [5])

months_str = ", ".join(months)
issues_str = ", ".join(str(v) for v in issues)
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

rows = "\n".join(
    f"| {m['name']} | [{m['github']}](https://github.com/{m['github']}) | {m['issues_triaged']} |"
    for m in members
)
members_table = f"| Name | GitHub | Issues Triaged |\n|---|---|---|\n{rows}"

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
    r'\| Name \| GitHub \| Issues Triaged \|.*?(?=\n---|\Z)',
    members_table + "\n",
    readme, flags=re.DOTALL
)

with open("README.md", "w") as f:
    f.write(readme)

print("README.md updated.")
