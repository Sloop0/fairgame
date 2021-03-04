$Host.UI.RawUI.WindowTitle = "Amazon Bot"
pipenv run python destroybots.py
$LogPath = "G:\nvidia-bot\"
$Folders = Get-Childitem $LogPath -dir -r | Where-Object {$_.name -like "*.profile-amz-*"} # Your keyword name directories
foreach ($Folder in $Folders) 
{
    $Item =  $Folder.FullName
    Write-Output $Item
    Remove-Item $Item -Force -Recurse -ErrorAction SilentlyContinue
}
pipenv run python app.py amazon --shipping-bypass --delay 2 --p GkfUmwX3DrJiiE
Exit