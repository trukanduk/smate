import sublime, sublime_plugin
import threading
import json
import os
import tempfile
import subprocess
import re
import socket

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

try:
    from ScriptingBridge import SBApplication
except ImportError:
    SBApplication = None

settings = sublime.load_settings('smate.sublime-settings')
server = None
server_thread = None
server_running = False
server_lock = threading.Event()

def _log(msg):
    print("[smate] {0}".format(msg))

class _SmateServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    pass

class _SmateConnectionHandler(socketserver.BaseRequestHandler):
    sftp_dir_re = re.compile(r'.*sublime-sftp-browse-\d{10}$')

    @staticmethod
    def _is_good_dir(path, hostname):
        if not _SmateConnectionHandler.sftp_dir_re.match(os.path.basename(path)):
            return False

        return os.path.isfile(os.path.join(path, hostname, 'sftp-config.json'))

    def handle(self):
        self.data = None

        _log('New connection from ' + str(self.client_address))
        data_file = self.request.makefile('r')
        text_data = data_file.read()
        _log(text_data)

        self.data = json.loads(text_data)

        if self.data.get('action', None) == 'open':
            sublime.set_timeout(self._open_file, 0)
        else:
            _log('unknow action "{action}"'.format(action=self.data.get('action', None)))

    def _open_file(self):
        if self.data == None or 'filepath' not in self.data:
            _log('Broken connection')
            return

        hostname = self.data.get('hostname', settings.get('default_sftp_server'))
        if hostname == None:
            _log('Unknown sftp_server')
            return

        tempdir = tempfile.gettempdir()
        sftp_dir = None
        for dirname in os.listdir(tempdir):
            full_path = os.path.join(tempdir, dirname)
            if _SmateConnectionHandler._is_good_dir(full_path, hostname) and \
               (sftp_dir == None or full_path > sftp_dir):
                sftp_dir = full_path

        if sftp_dir == None:
            _log('Alive sftp dir not found')
            return

        got_file = os.path.join(sftp_dir, hostname) + self.data['filepath']
        _log('Sftp dir is {dir}, will write to {file}'.format(dir=sftp_dir, file=got_file))

        if not os.path.isdir(os.path.dirname(got_file)):
            os.makedirs(os.path.dirname(got_file))

        if not os.path.isfile(got_file):
            out = open(got_file, 'w')
            if 'file_data' in self.data:
                out.write(self.data['file_data'])
            out.close()
            created = True
        else:
            created = False

        if len(sublime.windows()) == 0:
            sublime.run_command('new_window')
        sublime.active_window().open_file(got_file)

        if created and (settings.get('force_sync_on_download', True) or 'file_data' not in self.data):
            sublime.active_window().run_command('sftp_download_file')

        if sublime.platform() == 'osx':
            if SBApplication:
                subl_window = SBApplication.applicationWithBundleIdentifier_("com.sublimetext.2")
                subl_window.activate()
            else:
                os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Sublime Text" to true' ''')
        elif sublime.platform() == 'linux':
            subprocess.call("wmctrl -xa 'sublime_text.sublime-text-2'", shell=True)

        self.data = None

def _server_serve():
    global server, server_lock
    while True:
        server_lock.wait()
        _log("Server is starting...")
        server.serve_forever()
        _log("Server is down")

def _run_server():
    global server, server_lock, server_thread

    if server_lock.is_set():
        _log("Server is already running!")
        return

    host = settings.get('host', 'localhost')
    port = settings.get('port', 52693)
    ip = socket.gethostbyname(host)

    if server == None or server.server_address != (ip, port):
        server = _SmateServer((host, port), _SmateConnectionHandler)

    if server_thread == None:
        server_thread = threading.Thread(target=_server_serve)
        server_thread.daemon = True
        server_thread.start()

    server_lock.set()
    _log("Started server on {host}:{port}".format(host=host, port=port))

def _stop_server():
    global server, server_lock

    if not server_lock.is_set():
        _log("Server is not running")
        return

    _log("Shutdowning server")
    server_lock.clear()
    server.shutdown()

def _restart_server():
    _stop_server()
    _run_server()

class SmateRunServerCommand(sublime_plugin.WindowCommand):
    def run(self):
        _run_server()

class SmateStopServerCommand(sublime_plugin.WindowCommand):
    def run(self):
        _stop_server()

class SmateRestartServerCommand(sublime_plugin.WindowCommand):
    def run(self):
        _restart_server()

def plugin_loaded():
    _restart_server()

if (int(sublime.version())<3000):
    plugin_loaded()
