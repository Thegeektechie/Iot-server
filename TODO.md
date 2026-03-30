# IoT Backend Signal Reception Fix

## Current Status
✅ Plan approved by user  
⏳ Implementation in progress  

## Tasks

### 1. Backend Fixes
- [x] Create TODO.md ✅
- [x] **Edit `app/api/v1/sensor.py`** ✅
  - ✅ Import logger
  - ✅ Fix `decrypt_payload` → `decrypt_value`
  - ✅ Add request logging (method, path, body)
  - ✅ **TEMP:** Support plain JSON input (no encryption required)
  - ✅ Log successful store updates
  - ✅ Fix deque type error (removed setdefault)
- [⏳] **Edit `app/services/sensor_service.py`** 
  - Handle plain dict data (no decrypt) or encrypted str
- [ ] Test endpoint with curl

### 2. Testing & Verification
- [ ] Start server: `python run.py`
- [ ] Test POST /sensor: `curl -X POST ...`
- [ ] Verify SSE receives data in dashboard
- [ ] Check logs for incoming requests

### 3. Frontend Notes (Separate Repo)
- Update `lib/api.ts` `sendSensorData()` to encrypt payload
- Use backend `encrypt_value()` logic or equivalent

## Next Command
Edit `app/api/v1/sensor.py`
