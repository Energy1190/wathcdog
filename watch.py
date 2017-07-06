import os
import sys
import time
import logging
from docker import Client
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def wait_overs():
	while not os.path.exists('/data/GID/gid.num'):
		time.sleep(2)

	while not os.path.exists('/data/GID/gid.ready'):
		time.sleep(2)

def get_group(name):
    x = []
    cmd = 'getent group "{0}"'.format(name)
    cli = Client(base_url='unix://tmp/docker.sock')
    id = cli.inspect_container('/samba')['Id']
    proc = cli.exec_create(id, cmd)
    print('DEBUG', file=sys.stdout)
    for i in cli.exec_start(proc['Id'], stream=False).decode('utf-8').split(sep='\n'):
        x.append(i)
    print('Cmd:', cmd, file=sys.stdout)
    print('Answer:', x, file=sys.stdout)
    return str(''.join(x)).split(sep=':')[2]

def set_chown(num, path):
    return os.system('chown -R :{0} {1}'.format(num, path))

def set_chmod(path):
    return os.system('chmod 775 {0}'.format(path))

class Handler(FileSystemEventHandler):
    def __init__(self, num=None, path=None, simple=False):
        FileSystemEventHandler.__init__(self)
        self.num = num
        self.path = path
		self.simple = simple

    def on_created(self, event):
		if not self.simple and self.path:
			set_chmod(self.path)
			set_chown(self.num, self.path)
        print(event, file=sys.stdout)

    def on_deleted(self, event):
        print(event)

    def on_moved(self, event):
        print(event)

def main(num, path):
    event_handler = Handler(num, path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    observer.join()

def start(path, group):
    num = get_group(group)
    main(num, path)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		wait_overs()
		if os.path.exists('/data/GID/watch.ready'):
			n = int(str(open('/data/GID/watch.ready', 'r').read()).replace('\n', ''))
		else:
			n = 0
		open('/data/GID/watch.ready', 'w+').write(str(int(n + 1)))
		print('I\'m start watch to:', sys.argv[1], sys.argv[2], file=sys.stdout)
		start(sys.argv[1], sys.argv[2])
	else:
		main(None, '/data')