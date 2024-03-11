from sqs import SQS_Client
from mail import send_mail


sqs_client = SQS_Client()

while True:
    messages = sqs_client.consoom()
    print(f"[x] recieved [{len(messages)}] messages to process")
    
    for msg in messages:
        send_mail(
            recv_addr = msg['recv_addr']['StringValue'],
            subject = msg['mail_subject']['StringValue'],
            body = msg['mail_body']['StringValue']
        )