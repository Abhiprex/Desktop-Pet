import os
import subprocess

base_dir = r"D:\Personal Project\desktop pet macbook"
app_dir = os.path.join(base_dir, "Desktop Pet.app")
ico_file = os.path.join(base_dir, "pet.ico")

# 1. Setup desktop.ini for Desktop Pet.app so Windows File Explorer shows the icon too!
ini_path = os.path.join(app_dir, "desktop.ini")
if not os.path.exists(ini_path):
    with open(ini_path, "w", encoding="utf-8") as f:
        f.write(f"""[.ShellClassInfo]
IconResource={ico_file},0
[ViewState]
Mode=
Vid=
FolderType=Generic
""")
    subprocess.run(["attrib", "+h", "+s", ini_path], check=False)
    subprocess.run(["attrib", "+r", app_dir], check=False)
print("desktop.ini configured for Desktop Pet.app")

# 2. Compile Desktop Pet.exe in desktop pet macbook with embedded pet.ico
cs_file = os.path.join(base_dir, "Launcher.cs")
exe_file = os.path.join(base_dir, "Desktop Pet.exe")

cs_code = """
using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Forms;

namespace DesktopPetLauncher
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string pyScript = Path.Combine(baseDir, "run_pet.py");
            if (!File.Exists(pyScript))
            {
                pyScript = Path.Combine(baseDir, "main.py");
            }

            string pythonExe = @"C:\\Python314\\pythonw.exe";
            if (!File.Exists(pythonExe))
            {
                pythonExe = @"C:\\Python314\\python.exe";
            }
            if (!File.Exists(pythonExe))
            {
                string pathEnv = Environment.GetEnvironmentVariable("PATH") ?? "";
                foreach (string dir in pathEnv.Split(';'))
                {
                    string candidate = Path.Combine(dir.Trim(), "pythonw.exe");
                    if (File.Exists(candidate)) { pythonExe = candidate; break; }
                    candidate = Path.Combine(dir.Trim(), "python.exe");
                    if (File.Exists(candidate)) { pythonExe = candidate; break; }
                }
            }

            if (!File.Exists(pythonExe))
            {
                MessageBox.Show("Python was not found on your system. Please install Python 3 to run Desktop Pet.", "Desktop Pet", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = pythonExe;
            psi.Arguments = "\\"" + pyScript + "\\"";
            psi.WorkingDirectory = baseDir;
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;

            try
            {
                Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error starting Desktop Pet: " + ex.Message, "Desktop Pet", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
"""

with open(cs_file, "w", encoding="utf-8") as f:
    f.write(cs_code)

csc_exe = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
cmd = [
    csc_exe,
    "/target:winexe",
    f"/win32icon:{ico_file}",
    f"/out:{exe_file}",
    "/reference:System.Windows.Forms.dll",
    cs_file
]
res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(cs_file):
    os.remove(cs_file)

if os.path.exists(exe_file):
    print("SUCCESS: Desktop Pet.exe compiled for macbook folder:", os.path.getsize(exe_file), "bytes")
else:
    print("FAILED to compile Desktop Pet.exe in macbook folder")
