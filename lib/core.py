class Spammert:
  def __init__(self, args):
    self.recipients = []
    self.args = args
    self.parse_args()
    self.reset_message()
    self.accepted_send = False

  def parse_args(self):
    self.recipients_file = self.args.r
    self.subject = self.args.s
    self.template_file = self.args.t
    self.mail_server = self.args.c
    self.mail_port = self.args.p
    self.priority = self.args.P
    self.variable_file = self.args.v
    self.starttls = self.args.e
    self.username = self.args.u
    self.password = self.args.w
    self.encryption = self.args.x
    self.attachment_dir = self.args.a
    self.image_dir = self.args.i
    self.from_address = self.args.f
    self.from_name = self.args.n
    if not self.from_name:
        self.from_name = self.from_address
    
  def reset_message(self):
    self.message = None
    self.message_alternative = None
    self.message_related = None
