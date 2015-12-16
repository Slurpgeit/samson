#!/usr/bin/env python

from lib.core import Spammert
from lib.functions import *

def main():
  args = parse_args()
  spammert = Spammert(args)
  parse_recipients(spammert)
  send_loop(spammert)

if __name__ == '__main__':
  main()