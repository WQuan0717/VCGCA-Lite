param(
    [string]$PythonPath = (Join-Path $env:USERPROFILE '.conda\envs\vcgca-lite\python.exe')
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw '找不到 vcgca-lite 环境。请先按 README 创建环境，或通过 -PythonPath 指定该环境的 python.exe。'
}

& $PythonPath (Join-Path $PSScriptRoot 'main.py')
exit $LASTEXITCODE
