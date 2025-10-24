import os
import shutil
import argparse
import json
from datetime import datetime

# ----------------- Configuration -----------------
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv", ".pptx"],
    "Music": [".mp3", ".wav", ".ogg"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Archives": [".zip", ".tar", ".gz", ".rar"],
    "Scripts": [".py", ".js", ".sh"]
}
DEFAULT_OUTPUT = "organized_output"
LOG_FILENAME = "organize_log.json"   # stored inside the output folder
# -------------------------------------------------

def ensure_dir(path):
    """Create directory if it doesn't exist (safe)."""
    os.makedirs(path, exist_ok=True)

def get_category_for_extension(ext):
    """Return the category name for a file extension, or None if unknown."""
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return None

def unique_dest_path(dest_dir, filename):
    """
    If filename already exists in dest_dir, append a number before the extension.
    Example: file.txt -> file(1).txt -> file(2).txt
    """
    base, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1
    while os.path.exists(os.path.join(dest_dir, candidate)):
        candidate = f"{base}({counter}){ext}"
        counter += 1
    return os.path.join(dest_dir, candidate)

def write_log(output_folder, log_entries):
    """Write list of log entries to the logfile inside output_folder."""
    ensure_dir(output_folder)
    log_path = os.path.join(output_folder, LOG_FILENAME)
    # If existing log, append to existing list
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if isinstance(existing, list):
                    log_entries = existing + log_entries
        except Exception:
            # if log is corrupted, overwrite with new entries
            pass
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_entries, f, indent=2, ensure_ascii=False)

def load_log(output_folder):
    """Load and return the log list from the logfile. Returns [] if none."""
    log_path = os.path.join(output_folder, LOG_FILENAME)
    if not os.path.exists(log_path):
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def undo_moves(output_folder):
    """
    Undo moves recorded in the log file.
    Moves each recorded destination back to its original source location.
    After successful undo, the log file is removed.
    """
    log = load_log(output_folder)
    if not log:
        print("No log entries found to undo.")
        return

    # We'll reverse the log to undo in reverse order
    failed = []
    for entry in reversed(log):
        src = entry.get("src")   # original path before move
        dest = entry.get("dest") # where it was moved to
        if not dest or not src:
            continue
        # If dest exists, move it back
        if os.path.exists(dest):
            # Ensure parent folder for src exists
            parent = os.path.dirname(src)
            ensure_dir(parent)
            try:
                shutil.move(dest, src)
                print(f"Restored: {dest} -> {src}")
            except Exception as e:
                print(f"Failed to restore {dest} -> {src}: {e}")
                failed.append(entry)
        else:
            print(f"Skipped (missing destination): {dest}")

    # If nothing failed, remove the log
    if not failed:
        try:
            os.remove(os.path.join(output_folder, LOG_FILENAME))
            print("Undo complete. Log removed.")
        except Exception:
            print("Undo complete, but failed to remove log file.")
    else:
        # write back only failed entries
        write_log(output_folder, list(reversed(failed)))
        print("Undo finished with some failures. Remaining failed entries saved to log.")

def organize(source_folder, output_folder=DEFAULT_OUTPUT, dry_run=False):
    """
    Scan source_folder and move files into categorized subfolders in output_folder.
    If dry_run is True, it will only print what it would do.
    This function also returns a list of log entries (for undo).
    """
    moved_entries = []   # each entry: {"timestamp":..., "src":..., "dest":...}
    counts = {}          # counts per category
    skipped = 0
    total = 0

    # Check source exists
    if not os.path.exists(source_folder):
        print(f"Source folder does not exist: {source_folder}")
        return []

    ensure_dir(output_folder)

    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)

        # Skip directories; handle only files
        if os.path.isdir(file_path):
            # skip
            continue

        total += 1
        ext = os.path.splitext(filename)[1].lower()
        category = get_category_for_extension(ext) or "Others"

        dest_dir = os.path.join(output_folder, category)
        ensure_dir(dest_dir)

        dest_path = unique_dest_path(dest_dir, filename)

        if dry_run:
            print(f"[DRY RUN] Would move: {file_path} -> {dest_path}")
            # For dry run we do not record movements
            continue

        # Try moving the file
        try:
            shutil.move(file_path, dest_path)
            print(f"Moved: {filename} -> {category}/")
            # record for log and counts
            timestamp = datetime.now().isoformat()
            moved_entries.append({
                "timestamp": timestamp,
                "src": file_path,
                "dest": dest_path
            })
            counts[category] = counts.get(category, 0) + 1
        except Exception as e:
            print(f"Failed to move {filename}: {e}")
            skipped += 1

    # Print summary
    print("\n--- summary ---")
    if counts:
        for cat, cnt in counts.items():
            print(f"{cat}: {cnt}")
    print(f"Total files scanned: {total}")
    print(f"Skipped (failed or directories): {skipped}")

    # Save log entries for undo if we actually moved files
    if moved_entries:
        write_log(output_folder, moved_entries)
        print(f"\nLog saved to: {os.path.join(output_folder, LOG_FILENAME)}")
        print("You can undo this run with: python organize.py --undo")
    else:
        print("\nNo files were moved (dry run or nothing to move).")

    return moved_entries

def parse_args():
    parser = argparse.ArgumentParser(description="Organize files by type.")
    parser.add_argument("source", nargs="?", default="sample_files",
                        help="Source folder to organize (default: sample_files)")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT,
                        help=f"Output folder (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't move files; just show what would happen")
    parser.add_argument("--undo", action="store_true",
                        help="Undo the last organize run (uses the log file)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # If user asked for undo, do that and exit
    if args.undo:
        undo_moves(args.output)
    else:
        # Run organize (dry-run if requested)
        entries = organize(args.source, args.output, dry_run=args.dry_run)
        # If it was a real run and entries were produced, we already wrote the log inside organize
        # (so nothing more is required here).
