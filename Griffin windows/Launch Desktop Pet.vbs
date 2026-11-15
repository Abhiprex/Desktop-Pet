Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = baseDir
q = Chr(34)
cmd = q & "C:\Python314\pythonw.exe" & q & " " & q & baseDir & "\run_pet.pyw" & q
WshShell.Run cmd, 0, False
