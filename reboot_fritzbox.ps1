<#
.SYNOPSIS
    Reboot an AVM FRITZ!Box router via the TR-064 SOAP API (Windows / PowerShell).

.DESCRIPTION
    Standalone Windows equivalent of the generated reboot_fritzbox.sh curl script.
    Sends a single DeviceConfig1:Reboot SOAP command using HTTP Digest auth.
    No Python, no extra modules required - works with the PowerShell that ships
    with Windows 10/11.

    PREREQUISITE: TR-064 must be enabled on the FRITZ!Box:
      Heimnetz > Netzwerk > Netzwerkeinstellungen >
      "Zugriff fuer Anwendungen zulassen"
      (Home Network > Network > Network Settings > "Allow access for applications")

.NOTES
    Fill in the placeholders below before running. After you enter a real
    password this file holds it in plain text - do NOT commit it to git.

    Run it via the included reboot_fritzbox.cmd (double-click), or directly:
      powershell -NoProfile -ExecutionPolicy Bypass -File .\reboot_fritzbox.ps1
#>

# ============================================================
#  Fill in your data (placeholders)
# ============================================================
$FritzBoxHost     = "fritz.box"              # hostname or IP, e.g. 192.168.178.1
$FritzBoxPort     = 49000                    # TR-064 port (default: 49000)
$FritzBoxUser     = "admin"                  # leave "admin" if no user is configured
$FritzBoxPassword = "<YOUR_PASSWORD_HERE>"   # your FRITZ!Box password
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "===================================================="
Write-Host "  FritzBox Reboot (PowerShell/TR-064)"
Write-Host "  Target: ${FritzBoxHost}:${FritzBoxPort}"
Write-Host "===================================================="
Write-Host ""

if ($FritzBoxPassword -eq "<YOUR_PASSWORD_HERE>" -or [string]::IsNullOrWhiteSpace($FritzBoxPassword)) {
    Write-Host "  [ERROR] No password set."
    Write-Host "  Please edit this script and fill in `$FritzBoxPassword."
    Write-Host ""
    exit 1
}

$confirm = Read-Host "  Are you sure you want to reboot your FritzBox? (yes/no)"
if ($confirm -ne "yes" -and $confirm -ne "y") {
    Write-Host "  Aborted."
    exit 0
}

Write-Host ""
Write-Host "  -> Sending reboot command to $FritzBoxHost ..."

$soapBody = '<?xml version="1.0" encoding="utf-8"?>' +
    '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"' +
    ' xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">' +
    '<s:Body>' +
    '<u:Reboot xmlns:u="urn:dslforum-org:service:DeviceConfig:1"/>' +
    '</s:Body>' +
    '</s:Envelope>'

$uri = "http://${FritzBoxHost}:${FritzBoxPort}/upnp/control/deviceconfig"

# Don't send "Expect: 100-continue" (curl omits it for a body this small;
# some servers stall waiting on it).
[System.Net.ServicePointManager]::Expect100Continue = $false

# TR-064 uses HTTP Digest auth - CredentialCache forces the Digest scheme.
$cache = New-Object System.Net.CredentialCache
$cache.Add([Uri]$uri, "Digest", (New-Object System.Net.NetworkCredential($FritzBoxUser, $FritzBoxPassword)))

$request = [System.Net.HttpWebRequest]::Create($uri)
$request.Method = "POST"
$request.Credentials = $cache
$request.ContentType = "text/xml; charset=utf-8"
$request.Headers.Add("SOAPACTION", "urn:dslforum-org:service:DeviceConfig:1#Reboot")

$bytes = [System.Text.Encoding]::UTF8.GetBytes($soapBody)
$request.ContentLength = $bytes.Length

try {
    $stream = $request.GetRequestStream()
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Close()

    $response = $request.GetResponse()
    $code = [int]$response.StatusCode
    $response.Close()

    if ($code -eq 200) {
        Write-Host ""
        Write-Host "  [OK] FritzBox reboot triggered successfully."
        Write-Host "  The router will restart now. This takes about 1-2 minutes."
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "  [ERROR] Unexpected response (HTTP $code)."
        Write-Host ""
        exit 1
    }
}
catch [System.Net.WebException] {
    $resp = $_.Exception.Response
    $code = if ($resp) { [int]$resp.StatusCode } else { 0 }
    Write-Host ""
    if ($code -eq 401) {
        Write-Host "  [ERROR] Authentication failed (HTTP 401)."
        Write-Host "  Please check the username and password in this script."
    } elseif ($code -eq 0) {
        Write-Host "  [ERROR] Could not reach $FritzBoxHost`:$FritzBoxPort."
        Write-Host "  Check the host/IP and that TR-064 is enabled on your FritzBox."
    } else {
        Write-Host "  [ERROR] Unexpected response (HTTP $code)."
        Write-Host "  Make sure TR-064 is enabled on your FritzBox."
    }
    Write-Host ""
    exit 1
}
