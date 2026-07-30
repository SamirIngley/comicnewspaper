import boto3
import io 
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo


# no need to delete because writing a file w the same name to the bucket will replace it
def delete_s3_objects(event, context):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(event['bucket_name'])

    bucket.objects.all().delete()

    return {
        'statusCode': 200,
        'body': json.dumps(f'All objects in bucket {event['bucket_name']} have been deleted')
        }

def image_filename():
    today = datetime.now(ZoneInfo("America/Los_Angeles"))
    year = today.strftime('%Y')
    month = today.strftime('%m')
    day = today.strftime('%d')

    daily_file_name = f"image-{year}-{month}-{day}.png"
    return daily_file_name



def s3_request(bucket_name, index_html, error_html, image_file): 
    s3 = boto3.client('s3')
    bucket_name = str(bucket_name)

    s3.put_object(
        Bucket=bucket_name,
        Key='index.html',
        Body=index_html,
        ContentType='text/html',
        CacheControl= 'max-age=0, must-revalidate, no-cache', # Force revalidation for HTML
    )

    s3.put_object(
        Bucket=bucket_name,
        Key='error.html',
        Body=error_html,
        ContentType='text/html',
        CacheControl= 'max-age=0, must-revalidate, no-cache', # Force revalidation for HTML
    )

    image_data = image_file.image_bytes

    pil_image = Image.open(io.BytesIO(image_data))

    buffer = io.BytesIO()

    pil_image.save(buffer, format="PNG")
    buffer.seek(0)

    image_file = image_filename()

    s3.put_object(
        Bucket=bucket_name,
        Key=image_file,
        Body=buffer,
        ContentType='image/png',
        CacheControl= 'max-age=0, must-revalidate, no-cache', # Force revalidation for HTML
    )

    return 

