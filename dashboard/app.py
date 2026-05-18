import re
import os
import subprocess
from flask import Flask, jsonify, render_template

app = Flask(__name__)

ALERT_FILE = os.environ.get('SNORT_ALERT_FILE', '/tmp/snort-log/alert')

ALERT_PATTERN = re.compile(
    r'(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}\.\d+)\s+\[\*\*\]\s+\[\d+:(\d+):\d+\]\s+(.+?)\s+\[\*\*\]'
    r'(?:\s+\[Classification:\s+(.+?)\])?'
    r'(?:\s+\[Priority:\s+(\d+)\])?'
    r'\s+\{(\w+)\}\s+(.+?)\s+->\s+(.+)'
)

ATTACKS = {
    'icmp':    ['ping', '-c', '4', '8.8.8.8'],
    'syn':     ['sudo', 'nmap', '-sS', '8.8.8.8', '-p', '1-50'],
    'telnet':  ['bash', '-c', 'echo q | telnet towel.blinkenlights.nl'],
    'ftp':     ['bash', '-c', 'echo quit | ftp ftp.us.debian.org'],
    'http':    ['curl', '--path-as-is', 'http://example.com/../../../../etc/passwd'],
}

def parse_alerts():
    alerts = []
    if not os.path.exists(ALERT_FILE):
        return alerts
    with open(ALERT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = ALERT_PATTERN.match(line)
            if m:
                alerts.append({
                    'timestamp': m.group(1),
                    'sid':       m.group(2),
                    'message':   m.group(3),
                    'classification': m.group(4) or 'N/A',
                    'priority':  m.group(5) or 'N/A',
                    'protocol':  m.group(6),
                    'src':       m.group(7),
                    'dst':       m.group(8),
                })
    return list(reversed(alerts))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/alerts')
def get_alerts():
    return jsonify(parse_alerts())

@app.route('/api/attack/<name>', methods=['POST'])
def run_attack(name):
    if name not in ATTACKS:
        return jsonify({'error': 'Unknown attack'}), 400
    try:
        subprocess.Popen(ATTACKS[name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return jsonify({'status': 'launched', 'attack': name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
