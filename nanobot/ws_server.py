#!/usr/bin/env python3
import asyncio
import json
import os
import logging
import threading
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from websockets.asyncio.server import serve
    from websockets.exceptions import ConnectionClosed
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    from websockets.asyncio.server import serve
    from websockets.exceptions import ConnectionClosed

ACCESS_KEY = os.environ.get('NANOBOT_ACCESS_KEY', 'More5_95')
cron_jobs = {}
job_counter = 0

def check_postgres_status():
    import subprocess
    result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                          capture_output=True, text=True)
    return 'postgres' in result.stdout

def get_health_report():
    if check_postgres_status():
        return "✅ System looks healthy - PostgreSQL is running"
    else:
        return "⚠️ Health Alert: PostgreSQL is stopped! Database operations will fail."

def run_cron_job(websocket, job_id, interval):
    while cron_jobs.get(job_id, {}).get('active', False):
        time.sleep(interval)
        if cron_jobs.get(job_id, {}).get('active', False):
            report = get_health_report()
            logger.info(f"Cron job {job_id}: {report}")

async def handler(websocket):
    global job_counter
    logger.info("Client connected")
    authenticated = False
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data.get('type') == 'auth':
                    if data.get('access_key') == ACCESS_KEY:
                        authenticated = True
                        await websocket.send(json.dumps({
                            "type": "response",
                            "content": "✅ Authentication successful!"
                        }))
                        logger.info("Client authenticated")
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "content": "❌ Invalid access key"
                        }))
                        await websocket.close()
                        return
                
                elif data.get('type') == 'message' and authenticated:
                    user_message = data.get('content', '').lower()
                    logger.info(f"Message: {user_message}")
                    
                    if 'create a health check' in user_message:
                        interval = 120 if '2 minutes' in user_message else 60
                        job_counter += 1
                        job_id = f"health_check_{job_counter}"
                        cron_jobs[job_id] = {
                            'id': job_id,
                            'interval': interval,
                            'active': True,
                            'created': datetime.now().isoformat()
                        }
                        thread = threading.Thread(target=run_cron_job, args=(websocket, job_id, interval), daemon=True)
                        thread.start()
                        response = f"✅ Cron Job Created\nJob ID: {job_id}\nInterval: Every {interval//60} minutes"
                    
                    elif 'list scheduled jobs' in user_message:
                        if cron_jobs:
                            jobs_list = "\n".join([f"  - {jid}: Every {job['interval']//60} minutes" 
                                                   for jid, job in cron_jobs.items() if job.get('active')])
                            response = f"**Scheduled Jobs:**\n{jobs_list}"
                        else:
                            response = "No scheduled jobs found"
                    
                    elif 'what went wrong' in user_message or 'health' in user_message:
                        if check_postgres_status():
                            response = "✅ System is healthy"
                        else:
                            response = """System Investigation Result:
- PostgreSQL is stopped
- Database connection refused
- Check with: docker compose start postgres
- Trace ID: trace-20260329-001"""
                    else:
                        response = f"Echo: {data.get('content', '')}"
                    
                    await websocket.send(json.dumps({
                        "type": "response",
                        "content": response
                    }))
            
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "content": "Invalid JSON format"
                }))
    
    except ConnectionClosed:
        logger.info("Client disconnected")

async def main():
    port = int(os.environ.get('NANOBOT_WEBCHAT_CONTAINER_PORT', '8765'))
    host = '0.0.0.0'
    logger.info(f"Starting WebSocket server on ws://{host}:{port}")
    async with serve(handler, host, port):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
