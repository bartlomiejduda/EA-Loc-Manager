# EA-Loc-Manager
Tool for parsing LOC files from EA games.<br>
It allows to extract texts from almost any EA game that uses EA localization files.<br>
It's designed to help with translation projects.<br><br>
LOC file format description can be found on [RE Wiki](https://rewiki.miraheze.org/wiki/EA_Games_LOC).

## Dependencies

* **[ReverseBox](https://github.com/bartlomiejduda/ReverseBox)**


## How to Build on Windows

1. Download and install  **[Python 3.11.6](https://www.python.org/downloads/release/python-3116/)**. Remember to add Python to PATH during installation
2. Download project's source code and unpack it
3. Go to the directory containing source code
   - ```cd <directory_path>```
4. Create virtualenv and activate it
   - ```python -m venv my_env```
   - ```.\my_env\Scripts\activate.bat```
5. Install all libraries from requirements.txt file
   - ```pip install -r requirements.txt```
6. Run the main script file
   - ```python ea_loc_manager.py <arguments>```
   
   
# Usage

<pre>
EA Loc Manager v1.0

options:
  -h, --help            show this help message and exit
  -e loc_file_path ini_file_path, --export loc_file_path ini_file_path
                        Export from LOC file
  -i ini_file_path loc_file_path, --import ini_file_path loc_file_path
                        Import to LOC file
  -enc {utf8,utf16,latin-1}, --encoding {utf8,utf16,latin-1}
                        Encoding to use (default: latin-1)
</pre>


# LOC formats support table

Table below isn't complete. It contains only some example games that I was able to test.
If you know any other EA game that is supported by my tool, please let me know on GitHub's
"Issues" tab.

| Game Title                                      | Export support      | Import support     |
|-------------------------------------------------|---------------------|--------------------|
| Harry Potter and the Chamber of Secrets (PS2)   | <center>✔️</center> | <center>❌</center> |
| Medal Of Honor: European Assault (XBOX Classic) | <center>✔️</center> | <center>❌</center> |
| NHL 07 (PSP)                                    | <center>✔️</center> | <center>❌</center> |
| SSX 3 (PS2)                                     | <center>❌</center>  | <center>❌</center> |
| SSX On Tour (PS2)                               | <center>✔️</center> | <center>❌</center> |
| SSX Tricky (PS2)                                | <center>✔️</center> | <center>❌</center> |


# Badges
![GitHub](https://img.shields.io/github/license/bartlomiejduda/EA-Loc-Manager?style=plastic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub repo size](https://img.shields.io/github/repo-size/bartlomiejduda/EA-Loc-Manager?style=plastic)
![GitHub all releases](https://img.shields.io/github/downloads/bartlomiejduda/EA-Loc-Manager/total)
![GitHub last commit](https://img.shields.io/github/last-commit/bartlomiejduda/EA-Loc-Manager?style=plastic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/bartlomiejduda/EA-Loc-Manager?style=plastic)
