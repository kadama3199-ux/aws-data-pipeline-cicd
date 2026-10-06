import boto3
import csv
import io
import json

stepfunctions = boto3.client("stepfunctions")
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("pipeline_control")


def lambda_handler(event, context):

    for record in event["Records"]:

        # SQS message contains S3 event
        s3_event = json.loads(record["body"])

        # Get S3 information
        s3_record = s3_event["Records"][0]["s3"]

        bucket = s3_record["bucket"]["name"]
        key = s3_record["object"]["key"]

        print(f"Processing file: s3://{bucket}/{key}")

        response = table.get_item(
            Key={
                "pipeline_id": "orders"
            }
        )

        item = response.get("Item")

        if item and item.get("last_file") == key and item.get("status") == "SUCCESS":
            print(f"File already processed: {key}")
            continue

        print(f"Processing file: s3://{bucket}/{key}")

        # Check file format
        if not key.lower().endswith((".csv", ".txt")):
            print("ERROR: Unsupported file format")
            continue

        # Read file from S3
        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        content = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(content))

        rows = list(reader)

        print(f"Columns: {reader.fieldnames}")
        print(f"Row count: {len(rows)}")

        # Empty file check
        if not rows:
            print("ERROR: File is empty")
            continue

        # Required columns
        required_columns = [
            "CustomerID",
            "CustomerName",
            "Country",
            "Email",
            "Phone"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in reader.fieldnames
        ]

        if missing_columns:
            print(f"ERROR: Missing columns: {missing_columns}")
            continue

        # CustomerID validation
        invalid_rows = [
            row
            for row in rows
            if not row["CustomerID"].strip()
        ]

        if invalid_rows:
            print(
                f"ERROR: {len(invalid_rows)} rows "
                "have empty CustomerID"
            )
            continue

        print("SUCCESS: CSV passed basic validation")

        # Update DynamoDB
        table.update_item(
            Key={
                "pipeline_id": "orders"
            },
            UpdateExpression="""
                SET last_file = :file,
                    #status = :status
            """,
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":file": key,
                ":status": "PROCESSING"
            }
        )

        print("DynamoDB pipeline_control updated successfully")

        execution = stepfunctions.start_execution(
        stateMachineArn="arn:aws:states:us-east-1:736865445555:stateMachine:order_processing_step_func",
        input=json.dumps({
            "pipeline_id": "orders",
            "bucket": bucket,
            "key": key
        })
        )

    print(f"Step Functions started: {execution['executionArn']}")

    return {
        "statusCode": 200,
        "message": "File processed successfully"
    }
