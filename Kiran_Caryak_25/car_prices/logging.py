import logging
from io import StringIO
import atexit
import logging
import json
from car_prices.ipc_socket import Client


class LogHandler(logging.StreamHandler):
    def __init__(self, spider):
        self.file = StringIO()
        super().__init__(self.file)

        self.setFormatter(logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s'))
        self.setLevel(logging.DEBUG)
        self.spider = spider

        logging.getLogger().addHandler(self)
        atexit.register(self.at_exit)

    def at_exit(self):
        final_log = self.file.getvalue()

        if self.spider.database is not None:
            self.spider.database.handle['logs' + ('_test' if self.spider.testing else '')].insert_one({
                'batch_com': self.spider.batch_com,
                'batch_id': self.spider.batch_id,
                'text': final_log,
            })

        if self.spider.socket_file:
            timeout = 600

            with Client() as client:
                client.connect(self.spider.socket_file, timeout)
                message = json.dumps({
                    'result': self.spider.final_result,
                    'log': final_log,
                }, default=str)
                client.send(message, timeout)
