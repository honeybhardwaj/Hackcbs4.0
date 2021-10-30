from secret import SID, AUTH
from twilio.rest import Client


class SendMessage:
    def __init__(self):
        self.client = Client(SID, AUTH)
        self.to = "whatsapp:+918700619766"
        self.from_ = "whatsapp:+14155238886"

    def send_message(self, message):
        print(f"Sending message {message}")
        message = self.client.messages.create(to=self.to, from_=self.from_, body=message)


if __name__ == "__main__":
    sendMessage = SendMessage()
    sendMessage.send_message("Hello World! Message from twilio!")