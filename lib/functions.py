import argparse
import sys
import os
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email import Encoders
from email.MIMEBase import MIMEBase
from email.mime.image import MIMEImage

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', metavar='<recipients file>', required=True, help='Recipients file')
  parser.add_argument('-s', metavar='<subject>', required=True, help='Subject')
  parser.add_argument('-t', metavar='<template file>', required=True, help='Template file (without extension)')
  parser.add_argument('-f', metavar='<sender address>', help='Sender address to use', required=True)
  parser.add_argument('-c', metavar='<server>', help='Outgoing server to use', default='127.0.0.1')
  parser.add_argument('-p', metavar='<port>', help='Port to use', default=25, type=int)
  parser.add_argument('-P', help='Send high priority', action='store_true')
  parser.add_argument('-v', metavar='<variable file>', help='Variable file')
  parser.add_argument('-e', help='Enable STARTTLS', action='store_true')
  parser.add_argument('-u', metavar='<username>', help='Username')
  parser.add_argument('-w', metavar='<password>', help='Password')
  parser.add_argument('-x', help='Use SSL/TLS', action='store_true')
  parser.add_argument('-a', metavar='<attachment dir>', help='Directory containing files to attach')
  parser.add_argument('-i', metavar='<image dir>', help='Directory containing images to embed')
  parser.add_argument('-n', metavar='<sender name>', help='Sender name to use (defaults to address if not set)')

  args = parser.parse_args()
  return args

def exit_error(error):
  print 'Error: %s' % error
  sys.exit()

def parse_recipients(self):
  if not os.path.isfile(self.recipients_file):
    exit_error('recipients file "%s" does not exist' % self.recipients_file)

  with open(self.recipients_file) as f:
    for line in f:
      recipient = line.strip().split(';')
      self.recipients.append({'email':recipient[0].strip(), 'id':recipient[1].strip()})
 
def compose_mail(self):
  if self.attachment_dir:
    if not os.path.exists(self.attachment_dir):
      exit_error('attachment directory "%s" not found' % (self.attachment_dir))

    for file_name in os.listdir(self.attachment_dir):
      file_path = '%s/%s' % (self.attachment_dir, file_name)
      
      if os.path.isfile(file_path):
        attachment = MIMEBase('application',"octet-stream")
        with open(file_path,'rb') as f:
          attachment.set_payload(f.read())

        Encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_path))
        self.message.attach(attachment)

def process_variables(self, data, var_file, replacements):
  if var_file:  
    with open(var_file, 'r') as f:
      for line in f:
        if line[0] != '#':
          error = False
          try:
            find, replace = line.strip().split('=', 1)
          except ValueError:
            error == True

          if self.image_dir:
            image_name = '%s/%s' % (self.image_dir, replace)

            if os.path.isfile(image_name):
              replace = 'cid:%s' % ('.'.join(replace.split('.')[:-1]))

          if error == False:
            data = data.replace(find, replace)

  for k,v in replacements.iteritems():
    data = data.replace(k,v)

  return data

def embed_images(self):
  if self.image_dir:
    if not os.path.exists(self.image_dir):
      exit_error('image directory "%s" not found' % (self.image_dir))

    for file_name in os.listdir(self.image_dir):
      file_path = '%s/%s' % (self.image_dir, file_name)

      if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
          image = MIMEImage(f.read())

        image.add_header('Content-Id', '.'.join(file_name.split('.')[:-1]))
        self.message_related.attach(image)

def add_attachments(self):
  if self.attachment_dir:
    if not os.path.exists(self.attachment_dir):
      exit_error('attachment directory "%s" not found' % (self.attachment_dir))

    for file_name in os.listdir(self.attachment_dir):
      file_path = '%s/%s' % (self.attachment_dir, file_name)
      
      if os.path.isfile(file_path):
        attachment = MIMEBase('application',"octet-stream")
        with open(file_path,'rb') as f:
          attachment.set_payload(f.read())

        Encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_path))
        self.message.attach(attachment)

def init_message(self):
  self.message = MIMEMultipart()
  self.message_alternative = MIMEMultipart('alternative')
  self.message_related = MIMEMultipart('related')

  self.message['From'] = '"%s" <%s>' % (self.from_name, self.from_address)
  self.message['Subject'] = self.subject
  if self.priority:
    self.message['X-Priority'] = '1 (Highest)'
    self.message['X-MSMail-Priority'] = 'High'
    self.message['Importance'] = 'High'

def send_loop(self):
  template_txt = '%s.txt' % self.template_file
  template_html = '%s.html' % self.template_file

  if not os.path.isfile(template_txt) and not os.path.isfile(template_html):
    exit_error('template not found (%s or %s)' % (template_txt, template_html))

  with open(self.recipients_file,'r') as f:
    for line in f:
      if  not line.strip():
        continue

      init_message(self)
      
      replacements = {}
      var_list = line.strip().split(';')
      recipient = var_list[0]
      self.message['To'] = recipient

      for k,v in enumerate(var_list):
        replacements.update({'[[%s]]' % k:'%s' % v})

      if os.path.isfile(template_txt):
        with open(template_txt,'r') as f:
          data_txt = f.read()

        if self.variable_file:
          var_file = '%s.txt' % (self.variable_file)
        else:
          var_file = None
  
        data_txt = process_variables(self, data_txt, var_file, replacements)

        txt_part = MIMEText(data_txt, 'plain')
        self.message_alternative.attach(txt_part)

      if os.path.isfile(template_html):
        with open(template_html,'r') as f:
          data_html = f.read()
        
        if self.variable_file:
          var_file = '%s.html' % (self.variable_file)
        else:
          var_file = None

        data_html = process_variables(self, data_html, var_file, replacements)
        
        html_part = MIMEText(data_html, 'html')
        self.message_related.attach(html_part)
        embed_images(self)

      build_message(self)
      show_accept_prompt(self)

      if self.encryption:
        mail_server = smtplib.SMTP_SSL(self.mail_server, self.mail_port)
        mail_server.ehlo()
      else:
        mail_server = smtplib.SMTP(self.mail_server, self.mail_port)
        mail_server.ehlo()
        if self.starttls:
          mail_server.starttls()
          mail_server.ehlo()

      if self.username and self.password:
        mail_server.login(self.username, self.password)

      send_ok = 0
      send_fail = 0
      sys.stdout.write('Sending to: "%s".. ' % (recipient))
      sys.stdout.flush()
      try:
        mail_server.sendmail(self.message['From'], recipient, self.message.as_string())
        sys.stdout.write('[OK]\n')
        sys.stdout.flush()
        send_ok += 1
      except Exception as e:
        sys.stdout.write('[FAIL] (%s)\n' % e)
        sys.stdout.flush()
      self.reset_message()

def build_message(self):
  self.message.attach(self.message_alternative)
  self.message.attach(self.message_related)
  add_attachments(self)

def show_accept_prompt(self):
  if not self.accepted_send:
    prompt = """[Samson spammer]
========================================
= Message example                      =
========================================
%s                                   
========================================
Start spammer? (n): """ % self.message
    if not raw_input(prompt).strip().lower() == 'y':
      exit_error('Aborted by user.')
    else:
      self.accepted_send = True
