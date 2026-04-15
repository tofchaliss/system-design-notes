import re
from collections import defaultdict

INPUT = "concepts/components.md"
OUTPUT = "README.md"

def github_anchor(text):
    text = text.strip().lower()

    # normalize unicode dashes
    text = text.replace("–", "-").replace("—", "-")

    # remove punctuation except hyphen
    text = re.sub(r'[^a-z0-9\s-]', '', text)

    # replace spaces with hyphen
    text = re.sub(r'\s+', '-', text)

    return text

anchors_seen = defaultdict(int)
toc = []

with open(INPUT, "r", encoding="utf-8") as f:
    for line in f:
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if not match:
            continue

        level = len(match.group(1))
        title = match.group(2).strip()

        if level == 1:
            continue

        base = github_anchor(title)

        count = anchors_seen[base]
        anchor = f"{base}-{count}" if count > 0 else base
        anchors_seen[base] += 1

        indent = "  " * (level - 1)
        toc.append(f"{indent}- [{title}](concepts/components.md#{anchor})")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("# 📚 Components Index\n\n")
    f.write("\n".join(toc))
