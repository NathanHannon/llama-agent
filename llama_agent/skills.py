import os
import glob
from pathlib import Path


def get_skills_dir():
    """Returns the path to the global .agents/skills directory."""
    return Path.home() / ".agents" / "skills"


def scan_skills():
    """Scans ~/.agents/skills for SKILL.md files and returns metadata."""
    skills_dir = get_skills_dir()
    skills = {}

    if not skills_dir.exists():
        return skills

    for skill_file in skills_dir.glob("*/SKILL.md"):
        try:
            content = skill_file.read_text(encoding="utf-8")
            # Simple frontmatter parser
            name = None
            description = None

            if content.startswith("---"):
                _, frontmatter, _ = content.split("---", 2)
                for line in frontmatter.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if key == "name":
                            name = value
                        elif key == "description":
                            description = value

            # Fallback if frontmatter parses weirdly or is missing
            if not name:
                name = skill_file.parent.name
            if not description:
                description = "No description provided."

            skills[name] = {
                "name": name,
                "description": description,
                "path": str(skill_file),
            }
        except Exception as e:
            print(f"Error loading skill {skill_file}: {e}")
            continue

    return skills
