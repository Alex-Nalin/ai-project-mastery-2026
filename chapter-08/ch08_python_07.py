import asyncpg
import httpx
from datetime import datetime, timedelta

async def check_workflow_health():
    """Check for workflow anomalies and alert if needed."""
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Check for failed workflows in last hour
    failed_count = await conn.fetchval("""
        SELECT COUNT(*) 
        FROM workflow_logs 
        WHERE status = 'error' 
        AND created_at > NOW() - INTERVAL '1 hour'
    """)
    
    if failed_count > 5:
        # Send alert to Slack
        async with httpx.AsyncClient() as client:
            await client.post(
                SLACK_WEBHOOK_URL,
                json={
                    "text": f"🚨 *Workflow Alert*\n{failed_count} workflows failed in the last hour.\nCheck the dashboard for details."
                }
            )
    
    # Check for slow executions
    slow_count = await conn.fetchval("""
        SELECT COUNT(*)
        FROM workflow_logs
        WHERE execution_time_ms > 30000
        AND created_at > NOW() - INTERVAL '1 hour'
    """)
    
    if slow_count > 10:
        async with httpx.AsyncClient() as client:
            await client.post(
                SLACK_WEBHOOK_URL,
                json={
                    "text": f"⚠️ *Performance Alert*\n{slow_count} workflows exceeded 30-second execution time in the last hour."
                }
            )
    
    await conn.close()

# Run every 5 minutes
async def main():
    while True:
        await check_workflow_health()
        await asyncio.sleep(300)
