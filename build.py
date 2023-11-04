import subprocess

import subprocess

# Replace 'your_app.py' with the main script of your Tkinter application
main_script = 'invoicegen.py'

# Create an executable using PyInstaller
subprocess.call(['pyinstaller', '--onefile', '--windowed', '--add-data', 'images;images', main_script])

