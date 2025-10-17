import usocket as socket
import gc, json
from time import sleep_ms, time, localtime

# Initialize the slots and closed tickets data
slots = {}
closed_tickets = []

# Helper function to format time
def format_time(ts):
    try:
        lt = localtime(int(ts))
        return "{:02d}:{:02d}:{:02d}".format(lt[3], lt[4], lt[5])
    except:
        return str(ts)

# Function to summarize the slots and their statuses
def summarize():
    total = len(slots)
    occ = sum(1 for s in slots.values() if s.get("occupied"))
    free = total - occ
    return {"total": total, "occupied": occ, "free": free}

# Function to broadcast events to the dashboard (e.g., car entry/exit)
def broadcast_event(msg):
    print("[WEB EVENT]", msg)

# Get the current time in `hh:mm:ss` format
def get_current_time():
    return format_time(time())

# ------------------ HTML ------------------
_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Smart Parking Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Arial', sans-serif;
    background-color: #f4f4f4;
    color: #333;
    padding: 20px;
}
h1 {
    text-align: center;
    font-size: 2.5em;
    color: #4CAF50;
    margin-bottom: 20px;
}
#status {
    font-size: 1.2em;
    margin: 20px 0;
    text-align: center;
    font-weight: bold;
}
#current-time {
    font-size: 1.2em;
    margin: 10px 0;
    text-align: center;
    font-weight: bold;
    color: #000;
}
#slots {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.slot {
    display: inline-block;
    width: 220px;
    height: 150px;
    margin: 10px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    padding: 10px;
    font-size: 1.2em;
    cursor: pointer;
    transition: background 0.3s ease, transform 0.3s ease;
}
.slot:hover {
    transform: translateY(-5px);
}
.occupied {
    background-color: #ffcccc;
}
.free {
    background-color: #ccffcc;
}
table {
    width: 100%;
    margin-top: 20px;
    border-collapse: collapse;
    background-color: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
th {
    background-color: #4CAF50;
    color: white;
}
td {
    font-size: 1em;
}
tr:hover {
    background-color: #f1f1f1;
}
@media (max-width: 768px) {
    #status {
        font-size: 1em;
    }
    .slot {
        width: 180px;
        height: 120px;
    }
    table {
        font-size: 0.9em;
    }
}
</style>
</head>
<body>
<h1>🚗 Smart Parking Dashboard</h1>
<div id="current-time">Current Time: </div>
<div id="status"></div>
<div id="slots"></div>
<h3>Active Tickets</h3>
<table id="active">
    <tr><th>ID</th><th>Slot</th><th>Time-In</th><th>Time-Out</th></tr>
</table>
<h3>Recent Closed Tickets</h3>
<table id="closed">
    <tr><th>ID</th><th>Slot</th><th>Duration</th><th>Fee</th><th>Time-Out</th></tr>
</table>
<script>
function fmt(t){ return new Date(t*1000).toLocaleTimeString(); }

function update() {
    fetch('/data').then(r => r.json()).then(d => {
        const s = d.summary;
        document.getElementById('status').innerHTML = 'Total ' + s.total + ' • Free ' + s.free + ' • Occupied ' + s.occupied;

        // Display current time
        document.getElementById('current-time').innerHTML = 'Current Time: ' + new Date().toLocaleTimeString();
        
        const slotsDiv = document.getElementById('slots');
        slotsDiv.innerHTML = '';
        for (const key in d.slots) {
            let i = d.slots[key];
            const div = document.createElement('div');
            div.className = 'slot ' + (i.occupied ? 'occupied' : 'free');
            div.innerHTML = '<strong>S' + key + '</strong><br>' + (i.occupied ? ('ID: ' + i.id) : 'Free Slot');
            slotsDiv.appendChild(div);
        }

        const act = document.getElementById('active');
        act.innerHTML = '<tr><th>ID</th><th>Slot</th><th>Time-In</th><th>Time-Out</th></tr>';
        for (const k in d.slots) {
            const i = d.slots[k];
            if (i.occupied) {
                const tr = document.createElement('tr');
                // Add current time for Time-In and Time-Out in active tickets
                tr.innerHTML = '<td>' + i.id + '</td><td>S' + k + '</td><td>' + fmt(new Date().getTime()/1000) + '</td><td>' + fmt(new Date().getTime()/1000) + '</td>';
                act.appendChild(tr);
            }
        }

        const clos = document.getElementById('closed');
        clos.innerHTML = '<tr><th>ID</th><th>Slot</th><th>Duration</th><th>Fee</th><th>Time-Out</th></tr>';
        for (const t of d.closed_tickets) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td>' + t.id + '</td><td>S' + t.slot + '</td><td>' + t.duration + '</td><td>$' + t.fee.toFixed(2) + '</td><td>' + t.time_out + '</td>';
            clos.appendChild(tr);
        }
    }).catch(e => console.error('update', e));
}

update();
setInterval(update, 4000);
</script>
</body>
</html>
"""

# ------------------ Server ------------------
def start_server(host="0.0.0.0", port=8080):
    gc.collect()
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    print("🌐 Web Dashboard ready at http://{}:{}".format(host, port))

    while True:
        try:
            conn, addr = s.accept()
            req = conn.recv(1024)
            if not req:
                conn.close()
                continue
            reqs = req.decode()

            if reqs.startswith("GET /data"):
                payload = json.dumps({
                    "slots": slots,
                    "closed_tickets": closed_tickets,
                    "summary": summarize()
                })
                conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n")
                conn.send(payload.encode())
            else:
                conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n")
                conn.send(_HTML.encode())

        except Exception as e:
            print("⚠️ Client error:", e)
        finally:
            try: conn.close()
            except: pass
            gc.collect()

