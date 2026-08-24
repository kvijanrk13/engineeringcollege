param(
    [string]$BaseUrl = "https://engineeringcollege.onrender.com"
)

$ErrorActionPreference = "Stop"
$results = [System.Collections.Generic.List[object]]::new()

function Add-TestResult {
    param([string]$Id, [string]$Description, [bool]$Passed, [string]$Actual)
    $results.Add([pscustomobject]@{
        ID = $Id
        Test = $Description
        Status = if ($Passed) { "PASS" } else { "FAIL" }
        Actual = $Actual
    })
}

$homeHeaders = curl.exe -s -I "$BaseUrl/aeclibrary/"
$homeStatus = [regex]::Match(($homeHeaders -join "`n"), "HTTP/\S+\s+(\d{3})").Groups[1].Value
$homeLocation = [regex]::Match(($homeHeaders -join "`n"), "(?im)^location:\s*(.+)$").Groups[1].Value.Trim()
Add-TestResult "LIVE_01" "Anonymous library access is protected" `
    ($homeStatus -eq "302" -and $homeLocation.StartsWith("/aeclibrary/student/signup/")) `
    "HTTP $homeStatus; Location $homeLocation"

$documentation = curl.exe -s -L "$BaseUrl/aeclibrary/documentation/"
$docText = $documentation -join "`n"
Add-TestResult "LIVE_02" "Documentation endpoint is available" `
    ($docText.Contains("Week 6 - Unit Testing and Integration Testing")) `
    "Week 6 heading present: $($docText.Contains('Week 6 - Unit Testing and Integration Testing'))"
Add-TestResult "LIVE_03" "Week 7 white-box section is deployed" `
    ($docText.Contains("A. White-Box Testing")) `
    "White-box heading present: $($docText.Contains('A. White-Box Testing'))"
Add-TestResult "LIVE_04" "Week 7 black-box section is deployed" `
    ($docText.Contains("B. Black-Box Testing")) `
    "Black-box heading present: $($docText.Contains('B. Black-Box Testing'))"

$results | Format-Table -AutoSize
$failed = @($results | Where-Object Status -eq "FAIL").Count
Write-Output "TOTAL=$($results.Count) PASSED=$($results.Count - $failed) FAILED=$failed"
if ($failed -gt 0) { exit 1 }
