import json
from datetime import datetime

def write_output(data, filename):
    with open(filename, "w") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }, f, indent=2)
