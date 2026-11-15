import os
import sys
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
ico_path = os.path.join(base_dir, "pet.ico")
exe_target = os.path.join(base_dir, "Desktop Pet.exe")
target_script = os.path.join(base_dir, "run_pet.pyw")
pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.isfile(pythonw_exe):
    pythonw_exe = sys.executable

main_target = exe_target if os.path.isfile(exe_target) else pythonw_exe
main_args = "" if os.path.isfile(exe_target) else f'"{target_script}"'

ps_code = f"""
$wsh = New-Object -ComObject WScript.Shell

# 1. Project directory shortcut
$projectLnk = Join-Path '{base_dir}' 'Launch Desktop Pet.lnk'
$s1 = $wsh.CreateShortcut($projectLnk)
$s1.TargetPath = '{main_target}'
$s1.Arguments = '{main_args}'
$s1.WorkingDirectory = '{base_dir}'
$s1.IconLocation = '{ico_path},0'
$s1.Description = 'Cozy Desktop Pet (Griffin)'
$s1.Save()
Write-Output "Updated in project: $projectLnk"

# 2. User Desktop shortcut
$desktopDir = 'C:\\Users\\abhip\\Desktop'
try {{
    $desktopLnk = Join-Path $desktopDir 'Cozy Desktop Pet.lnk'
    $s2 = $wsh.CreateShortcut($desktopLnk)
    $s2.TargetPath = '{main_target}'
    $s2.Arguments = '{main_args}'
    $s2.WorkingDirectory = '{base_dir}'
    $s2.IconLocation = '{ico_path},0'
    $s2.Description = 'Cozy Desktop Pet (Griffin)'
    $s2.Save()
    Write-Output "Updated on Desktop: $desktopLnk"
}} catch {{
    Write-Output "Error writing to Desktop: $_"
}}
"""

ps_file = os.path.join(base_dir, "make_shortcut.ps1")
with open(ps_file, "w", encoding="utf-8") as f:
    f.write(ps_code)

res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_file], capture_output=True, text=True)
print("Returncode:", res.returncode)
print("Output:", res.stdout.strip())
if res.stderr.strip():
    print("Error:", res.stderr.strip())

if os.path.exists(ps_file):
    os.remove(ps_file)
