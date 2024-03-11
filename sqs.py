import boto3
import uuid
from credentials import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class SQS_Client:
    
    def __init__(self) -> None:

        self.q_url = "https://sqs.ap-south-1.amazonaws.com/212267546873/q-mail"

        self.client = boto3.client(
            'sqs', 
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            region_name = 'ap-south-1'
        )
        print(f"[x] connected to SQS client.")
    

    def publish(self, messageAttributes: dict) -> dict:

        messageBody = f"uuid - {uuid.uuid4().__str__()}"

        res = self.client.send_message(
            QueueUrl = self.q_url,
            MessageBody = messageBody,
            MessageAttributes = messageAttributes
        )

        print("[x] message posted to 'qmail'")
        return res

    
    def consoom(self) -> list:

        messages = self.client.receive_message(
            QueueUrl = self.q_url,
            MaxNumberOfMessages = 5,
            WaitTimeSeconds = 10,  # polls the queue every 5 seconds (maintains persistent connection for 5 seconds)
            MessageAttributeNames = ['All']
        )

        if 'Messages' not in messages: 
            return []
        
        to_process = []
    
        for msg in messages['Messages']:
            # print(msg['Body'], msg['MessageAttributes'], sep='\n')
            to_process.append( msg['MessageAttributes'] )

            self.client.delete_message(QueueUrl = self.q_url, ReceiptHandle = msg['ReceiptHandle'])
            # print(f"[x] message deleted.")
            # print(f"#- -# #- -# #- -# #- -# #- -# #- -# #- -# #- -# #- -#\n")
        
        return to_process