import anvil.server

@anvil.server.callable
def ping():
  return "pong"
