# /usr/bin/env python
import json

from app.server import app

filename = "../sdk/openapi.json"
with open(filename, "w") as f:
    json.dump(app.openapi_schema, f, indent=4)
    print(f"> Saved to {filename}")
