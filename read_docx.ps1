[System.Reflection.Assembly]::LoadWithPartialName('System.IO.Compression.FileSystem') | Out-Null
$zip = [System.IO.Compression.ZipFile]::OpenRead('Module5_Review (2).docx')
$entry = $zip.GetEntry('word/document.xml')
$stream = $entry.Open()
$reader = New-Object System.IO.StreamReader($stream)
$xmlText = $reader.ReadToEnd()
$stream.Close()
$zip.Close()

# Clean XML tags to get plaintext
$cleanText = [regex]::Replace($xmlText, '<[^>]+>', ' ')
# Condense multiple whitespaces/newlines into clean spacing
$cleanText = [regex]::Replace($cleanText, '\s+', ' ')
Write-Output $cleanText
