# This script installs VS Code extensions from a list in extensions.txt
$extensions = Get-Content -Path "extensions.txt"
foreach ($extension in $extensions) {
    if ($extension) {
        Write-Host "Installing extension: $extension"
        code --install-extension $extension
    }
}
Write-Host "All extensions installed."
