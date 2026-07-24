import json
from image_generator import generate_image

from s3_handler import s3_request 


def lambda_handler(event, context):

    index_page = None
    error_page = None
    image = generate_image()

    with open('site_html/site_index.html', 'rb') as f:
        data = f.read()
        index_page = data

    with open('site_html/site_error.html', 'rb') as f:
        data = f.read()
        error_page = data

    # no need to delete, s3 replaces files if they have the same name
    # delete_s3_objects("comicnewspaper")

    s3_request("www.comicnewspaper.com", index_page, error_page, image)

    return {
        'statusCode': 200,
        'body': 'Great success! Files pushed to S3'
    }

    