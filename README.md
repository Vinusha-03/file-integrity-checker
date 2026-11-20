# File Integrity Checker (Python)

A beginner-friendly cybersecurity project that monitors files for unauthorized changes using **SHA-256 hashing**.

## What it detects

- Modified files
- Newly added files
- Deleted files

## How it works

1. Run `init` to calculate SHA-256 hashes for files in a directory.
2. The hashes are saved in `.integrity_baseline.json`.
3. Run `check` later to compare the current files with the saved baseline.
4. The program reports any additions, deletions, or modifications.

## Requirements

- Python 3.8 or later
- No third-party packages required

## Setup

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/file-integrity-checker.git
cd file-integrity-checker
```

## Usage

Create a folder to monitor and add a few test files:

```bash
mkdir sample_files
echo "Original content" > sample_files/example.txt
```

Create the initial baseline:

```bash
python integrity_checker.py init sample_files
```

Check for changes:

```bash
python integrity_checker.py check sample_files
```

Try modifying a file:

```bash
echo "This file was changed" >> sample_files/example.txt
python integrity_checker.py check sample_files
```

Try adding or deleting a file and run `check` again.

## Example output

```text
[+] Baseline created: sample_files/.integrity_baseline.json
[+] Files recorded: 1

[!] Changes detected:
  [MODIFIED] example.txt
```

## Project structure

```text
file-integrity-checker/
├── integrity_checker.py
├── README.md
└── .gitignore
```

## Concepts learned

- Cryptographic hashing (SHA-256)
- File handling with `pathlib`
- Comparing data and detecting changes
- JSON data storage
- Command-line arguments with `argparse`
- Basic security monitoring

## Important security note

The baseline file must be protected. If an attacker can modify both the monitored files and the baseline, they may be able to hide changes. For stronger protection, store or sign the baseline separately and keep it somewhere the monitored user cannot modify.

This is a learning project, not a replacement for a professional File Integrity Monitoring (FIM) system.

## License

MIT
