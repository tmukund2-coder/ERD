# ERD Repository (bigER + VS Code)

This repository is for students to submit Entity‑Relationship Diagrams (ERDs) using the bigER VS Code extension.

## Prerequisites
- VS Code installed
- Git installed and a GitHub account
- Java 11+ runtime (JDK recommended)
- VS Code extension: BIGER Modeling Tool (`BIGModelingTools.erdiagram`)

### Install Java quickly
- macOS (Homebrew): `brew install --cask temurin17`
- Windows (winget): `winget install --id EclipseAdoptium.Temurin.17.JDK -e`
- Verify: `java -version` (shows 11+)

## Submission (No PRs/Merges)
You will submit your ERD via a GitHub Issue — no forks or pull requests required.

1) Create your ERD in VS Code
- Ensure bigER extension is installed and Java works: `java -version` shows 11+.
- Create a file at the repo root, for example: `Firstname_Lastname.erd`.
- Use Command Palette → “New Sample ER Model” to start, or write your own.
- Open the diagram from the editor toolbar or press Ctrl/⌘+O.

2) Submit via GitHub Issue
- Go to: https://github.com/BADM554/ERD/issues → “New issue”.
- Choose “ERD Submission” template (if available) or open a blank issue.
- Title: `Submission: Firstname Lastname`.
- Attach your `.erd` file by dragging it into the issue body.
- Provide any requested details (name, section, email) and click “Submit new issue”.

3) Updates/Resubmissions
- If you need to resubmit, open a new issue with the updated `.erd` attached.

## Optional: Git one‑time setup (only if you plan to use Git locally)
Run once in a VS Code terminal:
```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Notes
- You do not need to fork or open a pull request for submissions.
- Place your `.erd` file(s) at the repository root when working locally.
- Keep filenames consistent with the convention `Firstname_Lastname.erd` unless instructed otherwise.

## Troubleshooting
- bigER inactive or no diagram: ensure the file ends with `.erd` and the extension is enabled.
- Java not found: install JDK 11+ (see above) and restart VS Code.

## Quick local view (added files)

I added two files to this repository to make it easy to view the ER diagram locally without VS Code or any extension:

- `university.mmd` — a Mermaid-format ER diagram converted from `university_crowsfoot.erd`.
- `erd_viewer.html` — a simple HTML page that embeds the Mermaid diagram (loads Mermaid from CDN) so you can open the diagram in any browser.

How to open the diagram in your browser

1. Open the repository folder in Finder and double-click `erd_viewer.html`, or run from the terminal (macOS):

```bash
open erd_viewer.html
```

2. The page will render the ER diagram using the Mermaid CDN. If you prefer an image file (PNG/SVG), you can export `university.mmd` with Mermaid's CLI tool:

```bash
# install mermaid CLI (one-time)
npm install -g @mermaid-js/mermaid-cli

# render to PNG
mmdc -i university.mmd -o university.png

# or render to SVG
mmdc -i university.mmd -o university.svg
```

Alternative: import the data into dbdiagram.io by converting to SQL/DBML (I can generate DBML or SQL for you if you'd like).

If anything doesn't render or you want a different style (colors, labels, multiplicities preserved exactly from the original `.erd`), tell me and I can refine the Mermaid mapping or produce SQL/DBML exports.
