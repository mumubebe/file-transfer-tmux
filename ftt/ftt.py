from subprocess import run, PIPE
import uuid
import time
import base64

SIZE_BULK = 83


def get_between(s, start_sub, end_sub):
    try:
        return s.split(start_sub, 1)[1].split(end_sub, 1)[0]
    except IndexError:
        return ""


class TmuxTransfer:
    def __init__(self, frwindow, towindow, frpane, topane, frfile, tofile):
        self.frwindow = frwindow
        self.towindow = towindow
        self.frpane = frpane
        self.topane = topane
        self.frfile = frfile
        self.tofile = tofile

    def send_keys(self, pane, cmd, idx):
        run(
            [
                "tmux",
                "send-keys",
                "-t",
                str(pane),
                f"{cmd} ; echo '#END{idx}' #START{idx}",
                "Enter",
            ]
        )

    def tosend_keys(self, cmd, idx):
        self.send_keys(self.topane, cmd, idx)

    def frsend_keys(self, cmd, idx):
        self.send_keys(self.frpane, cmd, idx)

    def get_buffer(self):
        res = run(["tmux", "show-buffer"], stdout=PIPE)
        res = res.stdout.decode().replace("\n", "").replace("\t", "")
        return res

    def capture_buffer(self, pane):
        run(["tmux", "capture-pane", "-S", "-" , "-t", str(pane)])

    def id(self):
        return uuid.uuid4().hex

    def get_text(self, pane, idx):
        """Get a specific output text
        Each send_key command has a idx which is wrapped around the output.
        """
        self.capture_buffer(pane)
        buf = self.get_buffer()
        return get_between(buf, f"#START{idx}", f"#END{idx}")

    def check_file(self, path):
        """Check if file exists or if we can access it"""
        idx = self.id()
        self.frsend_keys(f"ls {path}", idx)

        time.sleep(0.1)
        r = self.get_text(self.frpane, idx)
        if "cannot access" in r:
            return False

        return True

    def save_file(self, path, data):
        """Save file to reciever
        Outputs buffered data by sending multiple small parts by echoing to file        
        """
        i = 0
        s = 173
        tmpfile = self.id()

        while True:
            idx = self.id()
            batch = data[i : i + s]
            self.tosend_keys(f"echo '{batch}' >> /tmp/{tmpfile}", idx)

            i += s
            if i > len(data):
                break
        
        self.tosend_keys(f"base64 -d /tmp/{tmpfile} > {path}", idx)
        self.tosend_keys(f"rm /tmp/{tmpfile}", idx)

    def transfer(self, fpath, tpath):
        data = self.fetch_file(fpath)
        self.save_file(tpath, data)

    def fetch_file(self, file):
        """Fetch file content to memory
        Decode file to base64 and output parts to tmux buffer
        """
        
        idx = self.id()
        self.frsend_keys(f"base64 {file} | wc -l", idx)
        nlines = int(self.get_text(self.frpane, idx))
        
        buf = ""
        pointer = SIZE_BULK
        bulk = SIZE_BULK
        last = ""
        while True:
            idx = self.id()
            self.frsend_keys(
                f"base64 {file} | head -n {pointer} | tail -n {bulk}", idx
            )
            time.sleep(0.1)
            r = self.get_text(self.frpane, idx)

            buf += r
            if pointer == nlines:
                break

            # Last bulk
            if (pointer + SIZE_BULK) >= nlines:
                bulk = nlines - pointer
                pointer = nlines 
            else:
                pointer += bulk
        return buf

    def has_base64(self):
        """Checks if sender has base64 binary installed"""
        idx = self.id()
        self.frsend_keys("which base64", idx)
        time.sleep(0.1)
        if len(self.get_text(self.frpane, idx).strip()) > 0:
            return True

        return False


trans = TmuxTransfer(0, 0, 2, 1, 0, 0)

trans.transfer("seq", "/tmp/lol2")
