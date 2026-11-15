"""
Compiles a native Windows PE GUI executable 'Desktop Pet.exe' with embedded pet.ico.
Uses built-in Windows .NET Framework C# compiler (csc.exe).
"""
import os
import subprocess
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
cs_file = os.path.join(base_dir, "Launcher.cs")
exe_file = os.path.join(base_dir, "Desktop Pet.exe")
ico_file = os.path.join(base_dir, "pet.ico")

cs_code = """
using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Forms;

namespace PuppyAndCatLauncher
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string pywScript = Path.Combine(baseDir, "run_pet.pyw");
            if (!File.Exists(pywScript))
            {
                pywScript = Path.Combine(baseDir, "main.py");
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
                MessageBox.Show("Python was not found on your system. Please install Python 3 to run Puppy & Cat Desktop Pets.", "Puppy & Cat Desktop Pets", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = pythonExe;
            psi.Arguments = "\\"" + pywScript + "\\"";
            psi.WorkingDirectory = baseDir;
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;

            try
            {
                Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error starting Puppy & Cat Desktop Pets: " + ex.Message, "Puppy & Cat Desktop Pets", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
"""

with open(cs_file, "w", encoding="utf-8") as f:
    f.write(cs_code)

csc_exe = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not os.path.exists(csc_exe):
    csc_exe = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"

cmd = [
    csc_exe,
    "/target:winexe",
    f"/win32icon:{ico_file}",
    f"/out:{exe_file}",
    "/reference:System.Windows.Forms.dll",
    cs_file
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("CSC return code:", res.returncode)
if res.stdout.strip():
    print("CSC output:", res.stdout.strip())
if res.stderr.strip():
    print("CSC error:", res.stderr.strip())

if os.path.exists(cs_file):
    os.remove(cs_file)

if os.path.exists(exe_file) and res.returncode == 0:
    print(f"SUCCESS: Created '{exe_file}' ({os.path.getsize(exe_file)} bytes) with icon!")
else:
    print("FAILED to create Desktop Pet.exe")
    sys.exit(1)
