import sys

def main():
    raw_commits = sys.stdin.read().strip().split('END_OF_COMMIT')
    commits = [parse_commit(raw_commit) for raw_commit in raw_commits if raw_commit.strip()]

    print("| Commit | Summary | Details |")
    print("| --- | --- | --- |")

    for commit in commits:
        # Convert line breaks in the commit body to bullet points
        body_lines = commit['body'].split('\n')
        body_markdown = ' <br> '.join(f"* {line}" for line in body_lines if line.strip()) if commit['body'] else ''
        # Escape markdown pipe characters in body and title
        title = escape_markdown(commit['title'])
        print(f"| `{commit['hash']}` | {title} | {body_markdown} |")

def parse_commit(raw_commit):
    """Parse the raw commit string into a dict with hash, title, and body."""
    parts = raw_commit.strip().split('\n', 2)
    return {
        'hash': parts[0][:7],  # Shorten the commit hash
        'title': parts[1],
        'body': parts[2] if len(parts) > 2 else ''
    }

def escape_markdown(text):
    """Escape markdown special characters."""
    return text.replace('|', '\\|')

if __name__ == "__main__":
    main()
