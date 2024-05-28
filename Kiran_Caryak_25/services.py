import shutil
from typing import cast
import subprocess
import signal


service_names = ['scrapyd', 'gunicorn']


def start_process(name: str):
    return subprocess.Popen([cast(str, shutil.which(name))], stdin=subprocess.PIPE)


def main():
    processes = [start_process(name) for name in service_names]

    def sigint_handler(*_):
        for process in processes:
            process.send_signal(signal.SIGINT)

    def sigterm_handler(*_):
        for process in processes:
            process.terminate()

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    for process in processes:
        process.communicate()


if __name__ == '__main__':
    main()
