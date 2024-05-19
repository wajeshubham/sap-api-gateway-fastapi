# Installation

```bash
pip install -r requirements.txt
```

# Usage

```bash
fastapi dev main.py
```

# Request Flow

```
Start
  |
  V
Incoming Request
  |
  V
Request enters Middleware
  |
  V
Check Request Counter for Threshold
  |
  |---------------------------------------|
  |                                       |
  | (Counter < Threshold)                 | (Counter == Threshold)
  |                                       |
  |                                       V
  |                                 Trigger Async Email Task to Send Notification
  |                                       |
  |---------------------------------------|
  |
  V
Forward Request to SAP System
  |
  V
Receive Response from SAP System
  |
  V
Return Response to Client
  |
  V
End
```
