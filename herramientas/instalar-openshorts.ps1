# Instala y arranca OpenShorts (https://github.com/mutonby/openshorts) en Windows.
#
# Uso: abre PowerShell en la carpeta donde quieras instalarlo y ejecuta
#   powershell -ExecutionPolicy Bypass -File instalar-openshorts.ps1
#
# Qué hace:
#   1. Comprueba Git y Docker Desktop; si falta alguno, lo instala con winget.
#   2. Descarga OpenShorts en .\openshorts, fijado a la versión revisada (commit 7e3468c, 18-11-2026).
#   3. Lo arranca con Docker y abre el panel (http://localhost:5175) cuando esté listo.

$ErrorActionPreference = "Stop"
$Repo = "https://github.com/mutonby/openshorts.git"
$CommitRevisado = "7e3468c"
$Panel = "http://localhost:5175"
$Destino = Join-Path (Get-Location) "openshorts"

function Paso($t) { Write-Host "`n==> $t" -ForegroundColor Cyan }
function Tiene($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function RefrescarPath {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

if (-not (Tiene "winget")) {
    Write-Host "No encuentro winget. Instala 'App Installer' desde Microsoft Store y vuelve a ejecutar este script." -ForegroundColor Red
    exit 1
}

# 1. Git
Paso "Comprobando Git"
if (Tiene "git") {
    Write-Host "Git ya está instalado: $(git --version)"
} else {
    Write-Host "Git no está instalado. Instalando…"
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    RefrescarPath
    if (-not (Tiene "git")) { Write-Host "Git se instaló, pero esta ventana aún no lo ve. Cierra PowerShell, ábrelo de nuevo y repite." -ForegroundColor Yellow; exit 1 }
}

# 2. Docker Desktop
Paso "Comprobando Docker Desktop"
if (-not (Tiene "docker")) {
    Write-Host "Docker Desktop no está instalado. Instalando (puede pedir permisos de administrador)…"
    winget install --id Docker.DockerDesktop -e --source winget --accept-package-agreements --accept-source-agreements
    Write-Host ""
    Write-Host "Docker Desktop instalado. Ahora:" -ForegroundColor Yellow
    Write-Host "  1) REINICIA el PC (Docker necesita WSL2)."
    Write-Host "  2) Abre Docker Desktop una vez y acepta los términos."
    Write-Host "  3) Vuelve a ejecutar este script."
    exit 0
}
Write-Host "Docker ya está instalado: $(docker --version)"

# Docker tiene que estar corriendo
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Desktop no está abierto. Intentando abrirlo…"
    $exe = Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"
    if (Test-Path $exe) { Start-Process $exe }
    $ok = $false
    for ($i = 0; $i -lt 36; $i++) {
        Start-Sleep -Seconds 5
        docker info *> $null
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
    }
    if (-not $ok) { Write-Host "Docker no arrancó en 3 minutos. Ábrelo a mano, espera a que diga 'Engine running' y repite." -ForegroundColor Red; exit 1 }
}
Write-Host "Docker está corriendo."

# 3. Descargar OpenShorts
Paso "Descargando OpenShorts en $Destino"
if (Test-Path (Join-Path $Destino ".git")) {
    Write-Host "Ya existe; actualizo el código."
    git -C $Destino fetch origin
} else {
    git clone $Repo $Destino
}
git -C $Destino checkout $CommitRevisado
if ($LASTEXITCODE -ne 0) { Write-Host "No pude fijar la versión revisada." -ForegroundColor Red; exit 1 }

# 4. Arrancar con Docker
Paso "Construyendo y arrancando contenedores (la primera vez tarda 10-20 min)"
Push-Location $Destino
try {
    docker compose up --build -d
    if ($LASTEXITCODE -ne 0) { throw "docker compose falló" }
} finally { Pop-Location }

# 5. Esperar al panel y abrirlo
Paso "Esperando a que el panel responda en $Panel"
$listo = $false
for ($i = 0; $i -lt 120; $i++) {
    try {
        $r = Invoke-WebRequest -Uri $Panel -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) { $listo = $true; break }
    } catch { }
    Start-Sleep -Seconds 5
}
if ($listo) {
    Write-Host "Panel listo. Abriendo el navegador…" -ForegroundColor Green
    Start-Process $Panel
    Write-Host ""
    Write-Host "Siguiente paso: en el panel ve a Settings y pega tu clave gratuita de Gemini"
    Write-Host "(https://aistudio.google.com/app/apikey). Las demás claves son opcionales."
    Write-Host "Para apagarlo:  cd openshorts ; docker compose down"
} else {
    Write-Host "El panel no respondió en 10 minutos. Revisa los registros con:" -ForegroundColor Yellow
    Write-Host "  cd openshorts ; docker compose logs --tail 50"
}
