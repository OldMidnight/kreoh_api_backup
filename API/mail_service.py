# from flask import current_app
from API.extensions import mail
from API.models import Message, User
from API.token import generate_confirmation_token

class MailService():
  '''
  Service to Manage the email services of Kreoh
  Params:
    mail_type = Determines what email address the message will be sent from
    user_id = if the mail is directed for one user, we can add it to the database
  '''
  def __init__(self, app, sender, user_id):
    with app.app_context():
      self.sender = sender
      self.user = User.query.filter_by(id=user_id).first()

  def send_support_message(self, subject, recipients, body, ticket_id):
    mail.send_message(subject, sender=self.sender, recipients=recipients, body=body)
    msg = Message(user_id=self.user.id, support_ticket_id=ticket_id, sender_name=self.sender[0], sender_address=self.sender[1], subject=subject, body=body)
    msg.add()

  def send_support_confirmation_message(self):
    subject = 'Support Ticket Recieved'
    body = 'Hi {f_name},\nThis is just a confirmation message to say we got your message! All you have to do now is wait and we will get back to you ASAP!\n\nHave a wonderful day,\nKreoh Support'.format(f_name=self.user.f_name)
    mail.send_message(subject=subject, sender=self.sender, recipients=[self.user.email], body=body)
    if self.user:
      msg = Message(user_id=self.user.id, sender_name=self.sender[0], sender_address=self.sender[1], subject=subject, body=body)
      msg.add()

  def send_message(self, subject, recipients, body):
    mail.send_message(subject, sender=self.sender, recipients=recipients, body=body)
    if self.user:
      msg = Message(user_id=self.user.id, sender_name=self.sender[0], sender_address=self.sender[1], subject=subject, body=body)
      msg.add()

  def send_welcome_message(self):
    token = generate_confirmation_token(self.user.email)
    confirm_url = 'http://www.kreoh.com/u/confirm_email/' + token
    subject = 'Welcome To Kreoh!'
    body = 'Hi {f_name},\n\nMy name is Fareed, founder of Kreoh. Allow me use this as an opportunity to welcome you to the Kreoh Community!\n\nIn order for you to fully access all the features of Kreoh, simply follow the link below:\n\n{confirm_url}\n\nIf you need any help setting up simply reply to this email and I will get right back to you.\nIn fact, I would be happy to answer any questions you may have.\n\nAgain, thank you for joining us and welcome aboard!\n\n Best of luck,\nFareed'.format(f_name=self.user.f_name, confirm_url=confirm_url)

    mail.send_message(subject=subject, sender=self.sender, recipients=[self.user.email], body=body)
    if self.user:
      msg = Message(user_id=self.user.id, sender_name=self.sender[0], sender_address=self.sender[1], subject=subject, body=body)
      msg.add()

  def send_email_change_message(self, new_email):
    token = generate_confirmation_token(new_email)
    confirm_url = 'http://www.kreoh.com/u/confirm_email/' + token
    subject = 'Email Change Confirmation'
    body = 'Hi {f_name},\n\nWe have recieved your email change request to:\n {new_email}\n\nFollow the link below to confirm:\n{confirm_url}\n\nThis link will expire in 1 hour. Once accepted your current email will no longer be associated with your Kreoh account.\nIf you did not request this email change or you are not registered with our service, please ignore this email.\n\nKind Regards,\nKreoh Representative\nhttps://Kreoh.com'.format(f_name=self.user.f_name, new_email=new_email, confirm_url=confirm_url)

    mail.send_message(subject=subject, sender=self.sender, recipients=[self.user.email], body=body)
    if self.user:
      msg = Message(user_id=self.user.id, sender_name=self.sender[0], sender_address=self.sender[1], subject=subject, body=body)
      msg.add()

  def send_email_verify_message(self):
    token = generate_confirmation_token(self.user.email)
    confirm_url = 'http://www.kreoh.com/u/confirm_email/' + token
    subject = 'Account Verification'
    body = 'Hi {f_name},\n\nYour almost ready to deploy your website, simply follow the link below to get started:\n{confirm_url}\n\nThis link will expire in 1 hour. Once accepted you will have full access to all the features available with your Kreoh account.\nIf you did not request this activation link or you are not registered with our service, please ignore this email.\n\nKind Regards,\nKreoh Representative\nhttps://Kreoh.com'.format(f_name=self.user.f_name, confirm_url=confirm_url)

    mail.send_message(subject=subject, sender=self.sender, recipients=[self.user.email], body=body)
    if self.user:
      msg = Message(user_id=self.user.id, sender_name=self.sender[0], sender_address=self.sender[1], subject=subject, body=body)
      msg.add()

  def send_password_change_message(self, new_password):
    token = generate_confirmation_token(new_password)
    confirm_url = 'http://www.kreoh.com/u/confirm_password/' + token
    subject = 'Password Change Request'
    body = 'Hi {f_name},\n\nWe have recieved your password change request.\n\nFollow the link below to confirm:\n{confirm_url}\n\nThis link will expire in 1 hour. If you did not request this password change please secure account at https://Kreoh.com/secure_my_account .\n\nKind Regards,\nKreoh Representative\nhttps://Kreoh.com'.format(f_name=self.user.f_name, confirm_url=confirm_url)

    mail.send_message(subject=subject, sender=self.sender, recipients=[self.user.email], body=body)
    if self.user:
      msg = Message(user_id=self.user.id, sender_name=self.sender[0], sender_address=self.sender[1], subject=subject, body=body)
      msg.add()
