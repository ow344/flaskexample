from models import Changelog, db
from config import Config
from email.message import EmailMessage
import smtplib

class ChangeService:
    def __init__(self, object):
        self.object = object
    def __enter__(self):
        self.current_dict = self.object.__dict__.copy()
    def __exit__(self, exc_type, exc_value, traceback):
        new_dict = self.object.__dict__
        changes = self.compare(self.current_dict, new_dict)
        if changes:
            for change in changes:
                self.record_change(
                    user_id=4,
                    object_type=self.object.__class__.__name__,
                    object_id=self.object.id,
                    attribute_changed=change['attribute_changed'],
                    old_value=change['old_value'],
                    new_value=change['new_value']
                )

    def compare(self, current_dict, new_dict):
        changes = []
        for key in current_dict:
            if key[0] != '_':
                if current_dict[key] != new_dict[key]:
                    changes.append({
                        'attribute_changed': key,
                        'old_value': current_dict[key],
                        'new_value': new_dict[key]
                    })
        return changes

    def record_change(self, user_id, object_type, object_id, attribute_changed, old_value, new_value):
        change = {
            'user_id': user_id,
            'object_type': object_type,
            'object_id': object_id,
            'attribute_changed': attribute_changed,
            'old_value': old_value,
            'new_value': new_value
        }
        change = Changelog(**change)
        print(change)
        db.session.add(change)
        db.session.commit()

def send_email(name, position, schoolname):
    sender, pw, recipients = Config.EMAIL_INFO.split('/')
    # Send to multiple recipients together
    message = f"Automated message from HR site. \n New Request to recruit from {name} for the position of {position} at {schoolname}. Please review. \n\n"
    email = EmailMessage()
    email["From"] = sender
    email["To"] = recipients
    email["Subject"] = f"HR Update ({schoolname})"
    email.set_content(message)
    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(sender, pw)
    smtp.sendmail(sender, recipients, email.as_string())
    smtp.quit()


if __name__ == "__main__":
    send_email("Test user", "Test role")