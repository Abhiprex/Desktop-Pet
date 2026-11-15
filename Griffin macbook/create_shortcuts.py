import os
import subprocess

base_dir = r"D:\Personal Project\desktop pet macbook"
ico_path = os.path.join(base_dir, "pet.ico")
exe_target = os.path.join(base_dir, "Desktop Pet.exe")

ps_code = f"""
$wsh = New-Object -ComObject WScript.Shell
$projectLnk = Join-Path '{base_dir}' 'Launch Desktop Pet.lnk'
$s1 = $wsh.CreateShortcut($projectLnk)
$s1.TargetPath = '{exe_target}'
$s1.WorkingDirectory = '{base_dir}'
$s1.IconLocation = '{ico_path},0'
$s1.Description = 'Cozy Desktop Pet (Griffin) - Mac Project'
$s1.Save()
Write-Output "Created shortcut: $projectLnk"
"""

ps_file = os.path.join(base_dir, "make_shortcut.ps1")
with open(ps_file, "w", encoding="utf-8") as f:
    f.write(ps_code)

res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_file], capture_output=True, text=True)
print(res.stdout.strip())
if os.path.exists(ps_file):
    os.remove(ps_file)
