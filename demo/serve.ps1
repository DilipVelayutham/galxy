$port = 8080
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
try {
    $listener.Start()
    Write-Host "Server successfully started on http://localhost:$port/"
    $currentDir = $PSScriptRoot
    if (!$currentDir) { $currentDir = Get-Location }
    
    # Identify the parent directory to locate root folder assets
    $parentDir = Split-Path -Parent $currentDir

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $urlPath = $request.Url.LocalPath
        if ($urlPath -eq "/") { $urlPath = "/index.html" }
        
        # Clean path to avoid traversal issues
        $cleanPath = $urlPath.Replace("/", "\").TrimStart("\")
        
        # Routing: if requesting assets, look into parent assets, else look locally
        if ($urlPath.StartsWith("/assets/")) {
            $filePath = Join-Path $parentDir $cleanPath
        } else {
            $filePath = Join-Path $currentDir $cleanPath
        }
        
        if (Test-Path $filePath -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            
            # Simple Mime Mapping
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            switch ($ext) {
                ".html" { $response.ContentType = "text/html; charset=utf-8" }
                ".css"  { $response.ContentType = "text/css; charset=utf-8" }
                ".js"   { $response.ContentType = "application/javascript; charset=utf-8" }
                ".png"  { $response.ContentType = "image/png" }
                ".ico"  { $response.ContentType = "image/x-icon" }
                default { $response.ContentType = "application/octet-stream" }
            }
            
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $response.StatusCode = 404
            $buf = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
            $response.ContentLength64 = $buf.Length
            $response.OutputStream.Write($buf, 0, $buf.Length)
        }
        $response.Close()
    }
} catch {
    Write-Host ("Failed to start listener on port " + $port + ": " + $_.Exception.Message)
} finally {
    $listener.Close()
}
