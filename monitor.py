import os
import sys
import time
import logging
from tkinter import messagebox as mbox
from collections import deque
from subprocess import Popen, PIPE

from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED
from watchdog.observers import Observer

logging.basicConfig(level=logging.INFO)
f_expand = os.path.expanduser

event_deque = deque()
event_lock = False

class PaperEventHandler(PatternMatchingEventHandler):
    # Tkinter cannot go here because of OS Sierra bug
    def add_event(self, event):
        global event_deque, event_lock
        if event_lock:
            logging.info('event_lock in action, ignore this event.')
        else:
            logging.info('added to event queue.')
            event_deque.append(event)

    def on_moved(self, event):
        logging.info(event)
        self.add_event(event)

    def on_created(self, event):
        logging.info(event)
        self.add_event(event)

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


# dpts1_dir: DPT-S1 dir to copy pdf to
def process_event(event, dpts1_dir):
    # hold a lock so that no events can be triggered when we process files
    global event_lock
    event_lock = True
    # get path of the file of interest
    if event.event_type == EVENT_TYPE_MOVED:
        title = 'Renamed'
        pdf = event.dest_path
    elif event.event_type == EVENT_TYPE_CREATED:
        title = 'Created'
        pdf = event.src_path
    else:
        raise ValueError('Unknown event: {}'.format(event))
    assert pdf.endswith('.pdf'), pdf + ' must be a pdf file.'
    # ask user whether to process this event or not
    response = mbox.askyesno(title, pdf)
    if response:
        old_dir, old_file = os.path.split(pdf)
        trim_pdf(pdf, os.path.join(dpts1_dir, old_file))
    # release the lock when we are done
    event_lock = False
    
# First path defaults to pdf working dir. Add Mendeley path from the second one. 
assert len(sys.argv) >= 3, 'must have at least two paths, first for DPT-S1 and second (and all the rest) for Mendeley'
dpts1_dir, *paths = sys.argv[1:]
observers = []
for path in paths:
    event_handler = PaperEventHandler(patterns=['*.pdf'],
                                      ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    observers.append(observer)
    logging.info('Observer started in ' + path)

try:
    while True:
        time.sleep(2)
        if event_deque:
            event = event_deque.popleft()
            process_event(event, dpts1_dir)
except KeyboardInterrupt:
    [observer.stop() for observer in observers]
[observer.join() for observer in observers]
