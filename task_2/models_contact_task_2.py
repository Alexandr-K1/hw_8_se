from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from datetime import datetime

class Contact(Document):
    fullname = StringField(required=True)
    email = EmailField(required=True, unique=True)
    message_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)