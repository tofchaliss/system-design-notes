import re
import os
from collections import defaultdict

BASE_DIR = "concepts"
OUTPUT = "README.md"

def github_anchor(text):
    text = text.strip().lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text

def process_file(filepath):
    anchors_seen = defaultdict(int)
    toc = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r'^\s*(#{1,6})\s+(.*)', line)
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

            indent = "  " * max(0, level - 2)
            rel_path = filepath.replace("\\", "/")

            toc.append(f"{indent}- [{title}]({rel_path}#{anchor})")

    return toc

all_sections = []

for file in sorted(os.listdir(BASE_DIR)):
    if file.endswith(".md"):
        filepath = os.path.join(BASE_DIR, file)

        section_title = file.replace(".md", "").replace("-", " ").title()
        all_sections.append(f"## {section_title}\n")

        toc = process_file(filepath)
        all_sections.extend(toc)
        all_sections.append("")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("# 📚 System Design Notes\n\n")
    f.write("\n".join(all_sections))