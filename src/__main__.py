import threading
from time import sleep
import typer
from src.datastore import DataStore
from src.server import Server

REDIS_DEFAULT_PORT = 6380

def check_expiry(datastore):
   while True:
      datastore.auto_check_expiry()
      sleep(0.1)

def main(port=None):
  if port == None:
    port = REDIS_DEFAULT_PORT
  else:
    port = int(port)

  print(f"Starting PyRedis on port: {port}")

  datastore = DataStore()
  expiration_monitor = threading.Thread(target=check_expiry, args=(datastore,))
  expiration_monitor.start()
  server = Server(port, datastore)
  server.run()

if __name__ == "__main__":
    typer.run(main)
