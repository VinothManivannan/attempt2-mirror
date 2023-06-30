if ($null -ne $env:MSYS2_INSTALL_DIR) {
    $env:PATH = $env:MSYS2_INSTALL_DIR + ";" + $env:PATH
}
else {
    Write-Host "Error: the environment variable `MSYS2_INSTALL_DIR` is not set. It should contain the installation path of msys2 (e.g. 'C:/msys64')."
    exit 1
}