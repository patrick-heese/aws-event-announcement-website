import json
import boto3
import os

sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

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
        body = json.loads(event['body'])
        email = body.get('email')
        if not email:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Email not provided'})
            }

        sns_client = boto3.client('sns')
        sns_client.subscribe(
            TopicArn=sns_topic_arn,
            Protocol='email',
            Endpoint=email
        )

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Subscription successful!'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }
