## 1. Ensure your Lambda's execution role has these permissions:

## 🔐 Required IAM Permissions

Add this policy to your Lambda execution role:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::image-non-sized-1",
                "arn:aws:s3:::image-non-sized-1/*",
                "arn:aws:s3:::image-sized-1", 
                "arn:aws:s3:::image-sized-1/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:ap-south-1:804937851364:image-resizing-topic"
        }
    ]
}
```
![image](https://github.com/user-attachments/assets/e45ad81b-1e3c-4123-8e59-862b95a48416)

   - Go to IAM → Roles
   - Select your Lambda execution role
   - Click "Add permissions" → "Create inline policy"
   - Paste the above JSON


## 2. Set these environment variables in your Lambda configuration:

  - SOURCE_BUCKET
  - DESTINATION_BUCKET
  - SNS_TOPIC_ARN
  - IMAGE_QUALITY (optional)
  - MAX_WIDTH (optional)
  - MAX_HEIGHT (optional)

## 3. We have to add layer 
   - May be you can think , why ?
   - It's because for resize the image we upload in our source S3 bucket , We need a python library called pillow in our code to resize the image . We can manually add Pillow library also, But it's very time consuming and you have to do lot more , Instead of manually adding pillow library we are going to use layers for Some easy action.
   - You can copy the arn from below
   - `arn:aws:lambda:ap-south-1:770693421928:layer:Klayers-p39-pillow:1`
