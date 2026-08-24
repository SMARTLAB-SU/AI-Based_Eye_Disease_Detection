$ws = New-Object -ComObject WScript.Shell

# Desktop shortcut
$dest1 = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop", "VisionAI.lnk")
$sc1 = $ws.CreateShortcut($dest1)
$sc1.TargetPath = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop", "VisionAI", "VisionAI.exe")
$sc1.WorkingDirectory = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop", "VisionAI")
$sc1.Save()

# OneDrive Desktop shortcut if it exists
$oneDriveDesktop = [System.IO.Path]::Combine($env:USERPROFILE, "OneDrive", "Desktop")
if (Test-Path $oneDriveDesktop) {
    $dest2 = [System.IO.Path]::Combine($oneDriveDesktop, "VisionAI.lnk")
    $sc2 = $ws.CreateShortcut($dest2)
    $sc2.TargetPath = [System.IO.Path]::Combine($oneDriveDesktop, "VisionAI", "VisionAI.exe")
    $sc2.WorkingDirectory = [System.IO.Path]::Combine($oneDriveDesktop, "VisionAI")
    $sc2.Save()
}
