param(
    [Parameter(Mandatory = $true)]
    [string]$AppHost,

    [int]$Users = 10,
    [int]$RampMilliseconds = 100,
    [int]$HoldSeconds = 30
)

$ErrorActionPreference = "Stop"

if ($Users -lt 1 -or $Users -gt 250) {
    throw "Users debe estar entre 1 y 250."
}

$cookieFile = Join-Path $env:TEMP "streamlit-load-test-cookies.txt"
$healthUrl = "https://$AppHost/_stcore/health"
$streamUrl = "wss://$AppHost/~/+/_stcore/stream"

& curl.exe -L -sS -c $cookieFile -b $cookieFile --max-time 30 -o NUL $healthUrl
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo iniciar la sesion anonima de Streamlit."
}

$cookieContainer = [System.Net.CookieContainer]::new()
$csrfToken = ""

Get-Content -LiteralPath $cookieFile | ForEach-Object {
    $line = $_ -replace "^#HttpOnly_", ""
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split "`t"
        if ($parts.Length -ge 7) {
            if ($parts[0] -eq $AppHost) {
                $cookieContainer.Add(
                    [System.Net.Cookie]::new($parts[5], $parts[6], "/", $parts[0])
                )
            }
            if ($parts[5] -eq "_streamlit_csrf") {
                $csrfToken = $parts[6]
            }
        }
    }
}

if (-not $csrfToken) {
    throw "No se obtuvo el token CSRF de Streamlit."
}

if (-not ("StreamlitLoadRunner" -as [type])) {
    Add-Type -Language CSharp -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.WebSockets;
using System.Threading;
using System.Threading.Tasks;

public sealed class StreamlitSessionResult
{
    public int Id { get; set; }
    public bool Connected { get; set; }
    public bool ReceivedData { get; set; }
    public long ConnectMilliseconds { get; set; }
    public long FirstMessageMilliseconds { get; set; }
    public long BytesReceived { get; set; }
    public int MessagesReceived { get; set; }
    public string Error { get; set; }
}

public static class StreamlitLoadRunner
{
    private static async Task<StreamlitSessionResult> RunOne(
        int id,
        Uri streamUri,
        CookieContainer cookies,
        string csrfToken,
        int delayMilliseconds,
        int holdSeconds)
    {
        var result = new StreamlitSessionResult { Id = id, Error = "" };
        if (delayMilliseconds > 0)
            await Task.Delay(delayMilliseconds);

        using (var socket = new ClientWebSocket())
        {
            socket.Options.Cookies = cookies;
            socket.Options.AddSubProtocol("streamlit");
            socket.Options.AddSubProtocol(csrfToken);
            socket.Options.SetRequestHeader("Origin", "https://" + streamUri.Host);

            try
            {
                var stopwatch = Stopwatch.StartNew();
                using (var connectCts = new CancellationTokenSource(TimeSpan.FromSeconds(30)))
                {
                    await socket.ConnectAsync(streamUri, connectCts.Token);
                }

                result.Connected = socket.State == WebSocketState.Open;
                result.ConnectMilliseconds = stopwatch.ElapsedMilliseconds;

                var rerunMessage = new byte[] { 0x5A, 0x00 };
                await socket.SendAsync(
                    new ArraySegment<byte>(rerunMessage),
                    WebSocketMessageType.Binary,
                    true,
                    CancellationToken.None);

                var buffer = new byte[65536];
                var endAt = DateTime.UtcNow.AddSeconds(holdSeconds);

                while (socket.State == WebSocketState.Open && DateTime.UtcNow < endAt)
                {
                    var remaining = endAt - DateTime.UtcNow;
                    using (var receiveCts = new CancellationTokenSource(remaining))
                    {
                        try
                        {
                            var received = await socket.ReceiveAsync(
                                new ArraySegment<byte>(buffer),
                                receiveCts.Token);

                            if (received.MessageType == WebSocketMessageType.Close)
                                break;

                            result.MessagesReceived++;
                            result.BytesReceived += received.Count;

                            if (!result.ReceivedData)
                            {
                                result.ReceivedData = true;
                                result.FirstMessageMilliseconds = stopwatch.ElapsedMilliseconds;
                            }
                        }
                        catch (OperationCanceledException)
                        {
                            break;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                result.Error = ex.GetBaseException().Message;
            }

            try
            {
                if (socket.State == WebSocketState.Open)
                {
                    await socket.CloseAsync(
                        WebSocketCloseStatus.NormalClosure,
                        "load test complete",
                        CancellationToken.None);
                }
            }
            catch
            {
            }
        }

        return result;
    }

    public static StreamlitSessionResult[] Run(
        string streamUrl,
        CookieContainer cookies,
        string csrfToken,
        int users,
        int rampMilliseconds,
        int holdSeconds)
    {
        var uri = new Uri(streamUrl);
        var tasks = new List<Task<StreamlitSessionResult>>();

        for (var i = 0; i < users; i++)
        {
            tasks.Add(RunOne(
                i + 1,
                uri,
                cookies,
                csrfToken,
                i * rampMilliseconds,
                holdSeconds));
        }

        return Task.WhenAll(tasks).GetAwaiter().GetResult();
    }
}
"@
}

$startedAt = Get-Date
$results = [StreamlitLoadRunner]::Run(
    $streamUrl,
    $cookieContainer,
    $csrfToken,
    $Users,
    $RampMilliseconds,
    $HoldSeconds
)
$elapsed = (Get-Date) - $startedAt

$connected = @($results | Where-Object Connected)
$received = @($results | Where-Object ReceivedData)
$failed = @($results | Where-Object { -not $_.Connected -or -not $_.ReceivedData })

$summary = [pscustomobject]@{
    Users = $Users
    Connected = $connected.Count
    ReceivedData = $received.Count
    Failed = $failed.Count
    AverageConnectMs = if ($connected.Count) {
        [math]::Round(($connected | Measure-Object ConnectMilliseconds -Average).Average)
    } else { 0 }
    MaxConnectMs = if ($connected.Count) {
        ($connected | Measure-Object ConnectMilliseconds -Maximum).Maximum
    } else { 0 }
    AverageFirstMessageMs = if ($received.Count) {
        [math]::Round(($received | Measure-Object FirstMessageMilliseconds -Average).Average)
    } else { 0 }
    MaxFirstMessageMs = if ($received.Count) {
        ($received | Measure-Object FirstMessageMilliseconds -Maximum).Maximum
    } else { 0 }
    TotalMegabytesReceived = [math]::Round(
        (($results | Measure-Object BytesReceived -Sum).Sum / 1MB),
        2
    )
    ElapsedSeconds = [math]::Round($elapsed.TotalSeconds, 1)
}

$summary | Format-List

if ($failed.Count) {
    Write-Output "Primeros fallos:"
    $failed |
        Select-Object -First 10 Id, Connected, ReceivedData, Error |
        Format-Table -AutoSize
    exit 1
}
