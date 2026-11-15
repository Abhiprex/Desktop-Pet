Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

If fso.FileExists(ScriptDir & "\Desktop Pet.exe") Then
    WshShell.CurrentDirectory = ScriptDir
    WshShell.Run Chr(34) & ScriptDir & "\Desktop Pet.exe" & Chr(34), 0, False
ElseIf fso.FileExists("C:\Python314\pythonw.exe") Then
    WshShell.CurrentDirectory = ScriptDir
    WshShell.Run Chr(34) & "C:\Python314\pythonw.exe" & Chr(34) & " " & Chr(34) & ScriptDir & "\run_pet.pyw" & Chr(34), 0, False
Else
    WshShell.CurrentDirectory = ScriptDir
    WshShell.Run "pythonw.exe " & Chr(34) & ScriptDir & "\run_pet.pyw" & Chr(34), 0, False
End If
