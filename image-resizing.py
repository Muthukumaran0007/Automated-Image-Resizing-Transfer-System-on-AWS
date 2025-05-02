import os
import boto3
from PIL import Image
from io import BytesIO

# Initialize AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

# Configuration - using environment variables
SOURCE_BUCKET = os.getenv('SOURCE_BUCKET', 'image-non-sized-1')
DESTINATION_BUCKET = os.getenv('DESTINATION_BUCKET', 'image-sized-1')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', 'arn:aws:sns:ap-south-1:804937851364:image-resizing-topic')
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', 75))
MAX_WIDTH = int(os.getenv('MAX_WIDTH', 1024))
MAX_HEIGHT = int(os.getenv('MAX_HEIGHT', 1024))

def lambda_handler(event, context):
    """Main Lambda handler function for image resizing service."""
    if 'Records' in event:
        # Handle batch S3 events
        for record in event['Records']:
            process_s3_object(record)
    else:
        # Handle direct invocation
        process_s3_object(event)
    return {'statusCode': 200, 'body': 'Processing completed'}

def process_s3_object(record):
    """Process a single S3 object from an event record."""
    try:
        # Validate event structure
        if not all(key in record.get('s3', {}) for key in ['bucket', 'object']):
            raise ValueError("Invalid S3 event record structure")
            
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Skip processing if object is in destination bucket
        if bucket == DESTINATION_BUCKET:
            return
            
        # Download and process the image
        response = s3.get_object(Bucket=bucket, Key=key)
        processed_image = process_image(
            response['Body'].read(),
            key.split('.')[-1].upper()
        )

        # Upload processed image
        destination_key = f"resized/{os.path.basename(key)}"
        s3.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=destination_key,
            Body=processed_image,
            ContentType=response['ContentType'],
            Metadata=response.get('Metadata', {})
        )

        # Send success notification
        notify_success(
            f"Image {key} processed\n"
            f"Original: s3://{bucket}/{key}\n"
            f"Resized: s3://{DESTINATION_BUCKET}/{destination_key}"
        )
        
    except Exception as e:
        notify_failure(f"Failed to process {key}: {str(e)}")
        raise

def process_image(image_data, format, quality=IMAGE_QUALITY):
    """Process the image with resizing and compression."""
    with Image.open(BytesIO(image_data)) as img:
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)
        output = BytesIO()
        img.save(output, format=format, quality=quality, optimize=True)
        return output.getvalue()

def notify_success(message):
    """Send success notification."""
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject='Image Processing Success'
    )

def notify_failure(error_message):
    """Send failure notification."""
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=error_message,
        Subject='Image Processing Failed'
    )
