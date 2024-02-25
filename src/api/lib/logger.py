import datetime as dt

from api.lib.config import DEV


def log(message: str):
  print(f'{dt.datetime.now()}: {message}')


def debug(message: str):
  if DEV:
    log(message)
