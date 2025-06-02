import json
import requests


def lambda_handler(event, context):
    records = event.get('Records', [])

    ses_record = records[0].get('ses', {})
    message_id = ses_record.get('mail', {}).get('messageId', "")

    print("Message Id : ", message_id)
    print("Request Id : ", context.aws_request_id)

    # API URL
    url = 'https://prateekgupta.pythonanywhere.com/process_emails?message_id='+message_id

    # Make the POST request
    response = requests.get(url)

    # Print the response
    print('Status Code :', response.status_code)

