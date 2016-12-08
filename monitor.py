import os
import sys
import time
import logging
from tkinter import Tk, Toplevel, messagebox as mbox
from collections import deque
from subprocess import Popen, PIPE
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED
from watchdog.observers import Observer

logging.basicConfig(level=logging.INFO,
        # format='%(asctime)s %(levelname)s> %(message)s'
        format='%(asctime)s> %(message)s', datefmt='%H:%M:%S')

f_expand = os.path.expanduser

event_deque = deque()
event_lock = False

class PdfEventHandler(PatternMatchingEventHandler):
    def __init__(self, *args, trigger_on_create=True, **kwargs):
        # if trigger_on_create=True, create event will also trigger pdf trimming
        super(PdfEventHandler, self).__init__(*args,  
                    patterns=['*.pdf'], ignore_directories=True, **kwargs)
        self.trigger_on_create = trigger_on_create

    # Tkinter cannot launch here because of OS Sierra bug
    def add_event(self, event):
        global event_deque, event_lock
        if False and event_lock: # disabled
            logging.info('event_lock in action, ignore this event.')
        else:
            logging.info('added to event queue.')
            event_deque.append(event)

    def on_moved(self, event):
        logging.info(event)
        self.add_event(event)

    def on_created(self, event):
        if self.trigger_on_create:
            logging.info(event)
            self.add_event(event)
        else:
            logging.warning('trigger_on_create=False: {} ignored'.format(event))

    def on_deleted(self, event):
        logging.info(event)

    def on_modified(self, event):
        logging.info(event)


def trim_pdf(in_pdf, out_pdf, margin=0.15):
    # calls Willus' k2pdfopt to trim the whitespaces
    in_pdf = f_expand(in_pdf)
    out_pdf = f_expand(out_pdf)
    # tm: trim mode, x: exit on completion, om: output margin (inch)
    proc = Popen(['bin/k2pdfopt-mac-2.35', in_pdf, '-mode', 'tm', '-x', '-o', out_pdf, '-om', '{0},{0},{0},{0}'.format(margin)], stdin=PIPE)
    proc.communicate(input=b'\n')


def get_root(center=True):
    # return Tkinter root panel that always stays on the front
    # http://stackoverflow.com/questions/3375227/how-to-give-tkinter-file-dialog-focus
    root = Tk()
    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    if center:
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        w, h = w // 2, h // 2
    else:
        w, h = 0, 0
    root.geometry('0x0+{}+{}'.format(w, h))
    # Show window again and lift it to top so it can get focus,
    # otherwise dialogs will end up behind the terminal.
    root.deiconify()
    root.lift()
    root.focus_force()
    return root


tk_root = get_root(False)
def process_event(event, dpts1_dir):
    # dpts1_dir: DPT-S1 dir to copy pdf to
    # hold a lock so that no events can be triggered when we process files
    global event_lock
    event_lock = True
    # get path of the file of interest
    if event.event_type == EVENT_TYPE_MOVED:
        title = 'Renamed'
        if not event.src_path.endswith('.pdf'):
            # might be a download file, not a real pdf
            logging.warning('Move event not actually a pdf renaming. Ignored.')
            event_lock = False
            return 
        pdf = event.dest_path
    elif event.event_type == EVENT_TYPE_CREATED:
        title = 'Created'
        pdf = event.src_path
    else:
        raise ValueError('Unknown event: {}'.format(event))
    assert pdf.endswith('.pdf'), pdf + ' must be a pdf file.'
    # ask user whether to process this event or not
    response = mbox.askyesno(title, pdf, parent=tk_root)
    if response:
        old_dir, old_file = os.path.split(pdf)
        trim_pdf(pdf, os.path.join(dpts1_dir, old_file))
    else:
        logging.warning('User cancelled.')
    # release the lock when we are done
    event_lock = False
    
# ==================== MAIN ====================
# First path defaults to pdf working dir. Add Mendeley path from the second one. 
assert len(sys.argv) >= 3, 'must have at least two paths, first for DPT-S1, second for Mendeley (trigger_on_create=False), and all the rest (if any) for other folders to be watched (trigger_on_create=True)'
dpts1_dir, *paths = sys.argv[1:]
logging.info('DPT-S1 box sync dir: ' + dpts1_dir)
observers = []
for i, path in enumerate(paths):
    # first dir is Mendeley, only trigger on move. 
    event_handler = PdfEventHandler(trigger_on_create=(i > 0))
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    observers.append(observer)
    if i == 0:
        logging.info('Mendeley observer (trigger_on_create=False) started in ' + path)
    else:
        logging.info('Normal observer started in ' + path)

try:
    while True:
        time.sleep(2)
        if event_deque:
            event = event_deque.popleft()
            process_event(event, dpts1_dir)
except KeyboardInterrupt:
    [observer.stop() for observer in observers]
[observer.join() for observer in observers]
