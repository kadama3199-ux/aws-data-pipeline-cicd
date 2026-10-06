import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda handler function for processing incoming data pipeline events.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    records_processed = 0
    if isinstance(event, dict) and "records" in event:
        records_processed = len(event["records"])
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Data pipeline processed successfully!",
            "records_processed": records_processed
        })
    }
