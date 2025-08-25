import json
import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
sns = boto3.client('sns')

bucket_name = os.environ.get('BUCKET_NAME')
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
events_file_key = 'events.json'

def lambda_handler(event, context):
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }

    try:
        new_event = json.loads(event['body'])
        title = new_event.get('title')
        description = new_event.get('description')
        date = new_event.get('date')

        if not title or not description or not date:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing event title, date, or description'})
            }

        # Load existing events
        try:
            response = s3.get_object(Bucket=bucket_name, Key=events_file_key)
            events_data = json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                events_data = []
            else:
                raise

        events_data.append(new_event)

        # Save updated events
        s3.put_object(
            Bucket=bucket_name,
            Key=events_file_key,
            Body=json.dumps(events_data, indent=2),
            ContentType='application/json'
        )

        # Publish SNS message
        message = f"New Event Created: {title}\nDescription: {description}"
        sns.publish(TopicArn=sns_topic_arn, Message=message, Subject="New Event Announcement")

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Event created successfully!'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }
