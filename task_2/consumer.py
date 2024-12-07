import json
import os
import sys

import pika
from mongoengine import connect
from task_2.models_contact_task_2 import Contact

connect(db="hw_8", host="mongodb+srv://Krasnozhon:1212@cluster1.ckj3z.mongodb.net/")


def send_email(contact):
    print(f"Sending email to {contact.fullname} <{contact.email}>...")
    print(f"Email sent to {contact.fullname} <{contact.email}>")


def main():
    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue="email_queue", durable=True)

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body.decode())
            contact_id = message.get("contact_id")
            print(f" [x] Received contact ID: {contact_id}")

            contact = Contact.objects(id=contact_id).first()
            if contact and not contact.message_sent:
                send_email(contact)
                contact.message_sent = True
                contact.save()
                print(f" [x] Contact {contact_id} updated as message sent.")
            else:
                print(f" [x] Contact {contact_id} not found or message already sent.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[!] Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue="email_queue", on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)