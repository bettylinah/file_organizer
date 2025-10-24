# 🗂️ File Organizer

A simple yet powerful Python script that automatically organizes files in a given folder into categories like **Documents**, **Images**, **Videos**, **Music**, and more.

---

## 🚀 Features
- Automatically sorts files by their extension.
- Creates neatly structured folders for each category.
- Prevents overwriting by renaming duplicates.
- Supports **undo** to reverse all file moves.
- Logs all activity in `organized_output/organize_log.json`.

---

## 🧠 How It Works
When you run the script, it:
1. Scans your target folder (e.g., `sample_files`).
2. Detects each file’s type (image, document, video, etc.).
3. Creates subfolders inside `organized_output/`.
4. Moves each file into its matching category.

---

## ⚙️ Usage

### ▶️ To Organize Files
```bash
python organize.py sample_files

## To Undo the last Organization

python organize.py --undo

##FOLDER STRUCTURE

file_organizer/
│
├── organized_output/
├── sample_files/
├── organize.py/
├── README.md


# example output

Moved: photo.png -> Images/
Moved: notes.pdf -> Documents/

--- summary ---
Documents: 1
Images: 1
Total files scanned: 2
Skipped: 0
Log saved to: organized_output/organize_log.json


#Demo

![Demo](demo.gif)

#Author

Linah Jhope
Built with ❤️ using Python.
GitHub: @bettylinah


# License

This project is open-source and available under the MIT License

