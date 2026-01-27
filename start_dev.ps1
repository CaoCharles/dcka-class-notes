# Add Git to PATH (if not present)
$env:PATH += ";C:\Program Files\Git\bin"
# Add uv to PATH (found at .local/bin)
$env:PATH += ";$env:USERPROFILE\.local\bin"

# Install/Sync dependencies
Write-Host "Syncing dependencies with uv..."
uv sync

# Load env vars from .env
if (Test-Path .env) {
    Get-Content .env | Foreach-Object {
        if ($_ -match '=') {
            $name, $value = $_.Split('=', 2)
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Start Backend on Port 8001
Write-Host "Starting Backend Server on Port 8001..."
Start-Job -ScriptBlock {
    param($env:GEMINI_API_KEY)
    uv run uvicorn backend.chat_server:app --reload --port 8001
} -ArgumentList $env:GEMINI_API_KEY

# Start MkDocs on Port 8000
Write-Host "Starting MkDocs on Port 8000..."
uv run mkdocs serve
