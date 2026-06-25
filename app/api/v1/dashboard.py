from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.store.memory_store import device_store

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return f"""
    <html>
    <head>
        <title>IoT Command Center</title>
        <style>
            body {{
                background: #000;
                color: #00ff00;
                font-family: monospace;
                padding: 20px;
            }}

            .container {{
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 20px;
            }}

            .panel {{
                border: 1px solid #00ff00;
                padding: 10px;
            }}

            button {{
                background: black;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                margin: 5px;
                cursor: pointer;
            }}

            textarea {{
                width: 100%;
                background: black;
                color: #00ff00;
                border: 1px solid #00ff00;
            }}

            #terminal {{
                height: 400px;
                overflow-y: auto;
                white-space: pre-wrap;
            }}

            img {{
                margin-top: 10px;
            }}
        </style>
    </head>

    <body>

        <h2>IoT COMMAND CENTER</h2>

        <div class="container">

            <!-- LEFT PANEL -->
            <div class="panel">
                <h3>CONTROL</h3>

                <p><b>Backend URL:</b></p>
                <p id="backend-url"></p>

                <button onclick="loadDevices()">Connected Devices</button>
                <button onclick="loadRecords()">View Records</button>
                <button onclick="clearTerminal()">Clear Terminal</button>
                <button onclick="clearRecords()">Clear Records (Realtime)</button>


                <hr>

                <h4>QR Builder</h4>
                <button onclick="generateQR()">Generate QR</button>
                <div id="qr"></div>

                <hr>

                <div id="info"></div>


            </div>

            <!-- RIGHT PANEL -->
            <div class="panel">
                <h3>TERMINAL</h3>
                <div id="terminal"></div>
            </div>

        </div>

        <script>
            const terminal = document.getElementById("terminal");

            function log(message) {{
                terminal.innerHTML += message + "\\n";
                terminal.scrollTop = terminal.scrollHeight;
            }}

            // Backend URL
            const baseUrl = window.location.origin;
            document.getElementById("backend-url").innerText = baseUrl;

            // STREAM CONNECTION (REAL-TIME)
            // Use absolute URL so iOS browsers don't break when page origin differs.
            const evt = new EventSource(baseUrl + "/api/v1/stream");


            evt.onmessage = function(event) {{
                const data = JSON.parse(event.data);

                log(`
> DEVICE: ${{data.device}}
> TIME: ${{data.record.timestamp}}
> DATA: ${{JSON.stringify(data.record.data, null, 2)}}
---------------------------`);
            }};

            evt.onerror = function() {{
                log("> STREAM ERROR: connection lost...");
            }};

            // LOAD DEVICES
            async function loadDevices() {{
                try {{
                    const res = await fetch('/api/v1/devices');
                    const data = await res.json();

                    document.getElementById("info").innerHTML =
                        "<pre>" + JSON.stringify(data, null, 2) + "</pre>";

                    log("> DEVICES LOADED");
                }} catch (err) {{
                    log("> ERROR loading devices");
                }}
            }}

            // LOAD RECORDS
            async function loadRecords() {{
                try {{
                    const res = await fetch('/api/v1/records');
                    const data = await res.json();

                    document.getElementById("info").innerHTML =
                        "<pre>" + JSON.stringify(data, null, 2) + "</pre>";

                    log("> RECORDS LOADED");
                }} catch (err) {{
                    log("> ERROR loading records");
                }}
            }}

            // CLEAR TERMINAL
            function clearTerminal() {{
                terminal.innerHTML = "";
            }}

            // CLEAR RECORDS (Realtime / SSE source)
            async function clearRecords() {{
                try {{
                    const res = await fetch('/api/v1/records', {{
                        method: 'DELETE',
                    }});
                    const data = await res.json();
                    document.getElementById("info").innerHTML =
                        "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
                    log("> RECORDS CLEARED");
                    terminal.innerHTML = "";
                }} catch (err) {{
                    log("> ERROR clearing records");
                }}
            }}


            // QR GENERATOR
            // IMPORTANT: Frontend QRScanner expects RAW server URL string (must start with http/https).
            async function generateQR() {{
                const qrData = baseUrl; // e.g. "http://localhost:8000" (NO JSON)

                const qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" 
                    + encodeURIComponent(qrData);

                document.getElementById("qr").innerHTML =
                    `<img src="${{qrUrl}}" />`;

                log("> QR GENERATED");
            }}




        </script>

    </body>
    </html>
    """
# EXISTING APIs (UNCHANGED)

@router.get("/api/v1/devices")
def get_devices():
    return {
        "devices": list(device_store.store.keys())
    }


@router.get("/api/v1/records")
def get_records():
    return device_store.store