async def dead_letter_handler(workflow_data: dict, error: Exception):
    """Handle failed workflow items."""
    async with httpx.AsyncClient() as client:
        # Store in database
        await client.post(
            f"{N8N_URL}/webhook/dead-letter",
            json={
                "original_data": workflow_data,
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat(),
                "retry_count": workflow_data.get('retry_count', 0)
            }
        )
        
        # Notify admin
        await client.post(
            SLACK_WEBHOOK_URL,
            json={
                "text": f"❌ *Dead Letter Alert*\nWorkflow item failed after all retries.\nError: {str(error)[:200]}"
            }
        )
