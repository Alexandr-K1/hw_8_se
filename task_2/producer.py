import json
import pika
from faker import Faker
from mongoengine import connect
from datetime import datetime

from task_2.models_contact_task_2 import Contact

connect(db="hw_8", host="mongodb+srv://Krasnozhon:1212@cluster1.ckj3z.mongodb.net/")

credentials = pika.PlainCredentials("guest", "guest")
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue="email_queue", durable=True)

fake = Faker('uk-Ua')


def generate_contacts_and_send_to_queue(count: int):
    for _ in range(count):
        contact = Contact(
            fullname = fake.name(),
            email = fake.email(),
            created_at = datetime.now()
        )
        contact.save()

        message = {
            "contact_id": str(contact.id),
            "sent_at": datetime.now().isoformat()
        }

        channel.basic_publish(exchange="", routing_key="email_queue", body=json.dumps(message).encode())
        print(f"[x] Sent contact ID and timestamp: {message}")

    print("[+] All contacts have been added to the queue.")


if __name__ == '__main__':
    try:
        generate_contacts_and_send_to_queue(10)
    finally:
        connection.close()