import fcntl
import logging
import os
from pathlib import Path
import shlex
import signal
import subprocess


logger = logging.getLogger(__name__)

class Watchdog():
    _running: bool = False
    _restart: bool = False
    _process: subprocess.Popen | None = None

    def __init__(self, path: Path, command: str | None = None, args: list[str] | None = None):
        if not path.is_dir():
            raise ValueError("path must be a directory")
        self._path: Path = path
        self._command = shlex.split(command) if command is not None else None
        self._args = args

    def reload(self, *args, **kwargs):
        self._restart = True
    
    def build_command(self):
        if self._command is not None:
            return self._command + self._args, None
        else:
            env = os.environ
            env["PYTHONPATH"] = f"{self._path.as_posix()}:{env.get('PYTHONPATH')}" 
            return ["python3", "-m", self._path.stem] + self._args, env

    def _start_process(self):
        while self._running:
            command, env = self.build_command()
            logger.info("Starting process %s", " ".join(command))
            self._process = subprocess.Popen(command, env=env)
            while not self._restart:
                try:
                    self._process.wait(1)
                except subprocess.TimeoutExpired:
                    continue
                logger.info("Process terminated itself with return code %d", self._process.poll())
                return
            logger.info("Stopping process")
            self._process.terminate()
            self._process.wait()
            logger.info("Stopped process")
            del self._process
            self._restart = False

    def run(self):
        self._running = True
        signal.signal(signal.SIGIO, self.reload)
        module_fd = os.open(self._path, os.O_RDONLY)
        fcntl.fcntl(module_fd, fcntl.F_NOTIFY, fcntl.DN_CREATE | fcntl.DN_DELETE | fcntl.DN_MODIFY | fcntl.DN_RENAME | fcntl.DN_MULTISHOT)
        self._start_process()
