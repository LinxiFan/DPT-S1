#!/usr/bin/env python3

"""
@author: jimfan
"""
PDF_EXE = 'bin/k2pdfopt-mac-2.35'
MONITOR_INTERVAL = 1
MONITOR_DELAY = 7 # wait after the first event arrives


import os
import sys
import time
import logging
from collections import deque
from subprocess import Popen, PIPE
from watchdog.events import PatternMatchingEventHandler, FileMovedEvent, EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED
from watchdog.observers import Observer
from dpts1.tk_utils import entry_prompt

logging.basicConfig(level=logging.INFO,
        # format='%(asctime)s %(levelname)s> %(message)s'
        format='%(asctime)s> %(message)s', datefmt='%H:%M:%S')
PDF_EXE = os.path.join(os.path.dirname(__file__), PDF_EXE)

# No need to chdir if `pip install -e .`
# current_dir = os.path.dirname(sys.argv[0]) 
# if current_dir: # avoid empty string
#     os.chdir(current_dir) # change to own dir

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
    proc = Popen([PDF_EXE, in_pdf, '-mode', 'tm', '-x', '-o', out_pdf, '-om', '{0},{0},{0},{0}'.format(margin)], stdin=PIPE)
    proc.communicate(input=b'\n')


def pop_collapse_deque(event_deque):
    # collapse multiple consecutive renaming
    # if nothing to collapse, pop the left most
    pop_i = 0 # pop until (exclusive)
    while pop_i + 1 < len(event_deque):
        older = event_deque[pop_i]
        newer = event_deque[pop_i + 1]
        if (older.event_type == EVENT_TYPE_MOVED
            and newer.event_type == EVENT_TYPE_MOVED
            and older.dest_path == newer.src_path):
            pop_i += 1
        else:
            break

    if pop_i > 0:
        start = event_deque[0]
        end = event_deque[pop_i]
        collapsed = FileMovedEvent(start.src_path, end.dest_path)
        for i in range(pop_i + 1):
            event_deque.popleft()
        logging.info('Collapsing {} renaming events into {}'
                     .format(pop_i + 1, collapsed))
        return collapsed
    else:
        return event_deque.popleft()

# global var that records the last entered folder name
last_default_dir = None

def process_event(event, dpts1_dir):
    # dpts1_dir: DPT-S1 dir to copy pdf to
    # hold a lock so that no events can be triggered when we process files
    global event_lock
    event_lock = True
    # get path of the file of interest
    if event.event_type == EVENT_TYPE_MOVED:
        title = 'Renamed'
        if not event.dest_path.endswith('.pdf'):
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
    dpt_parent_dir, dpt_default_child_dir = os.path.split(os.path.normpath(dpts1_dir))
    global last_default_dir
    if last_default_dir:
        default = last_default_dir
    else:
        default = dpt_default_child_dir
    response = entry_prompt(os.path.basename(pdf), default=default)
    if response:
        child_dir = last_default_dir = response
        old_dir, old_file = os.path.split(pdf)
        trim_pdf(pdf, os.path.join(dpt_parent_dir, child_dir, old_file))
    else:
        logging.warning('User cancelled.')
    # release the lock when we are done
    event_lock = False
    
# ==================== MAIN ====================
# First path defaults to pdf working dir. Add Mendeley path from the second one. 
assert len(sys.argv) >= 3, 'must have at least two paths, first for DPT-S1, second for Mendeley (trigger_on_create=False), and all the rest (if any) for other folders to be watched (trigger_on_create=True)'
assert os.path.isfile(PDF_EXE), PDF_EXE + ' cannot be found.'

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

delay = MONITOR_DELAY
try:
    while True:
        time.sleep(MONITOR_INTERVAL)
        if event_deque:
            if delay > 0:
                delay -= 1
                continue
            event = pop_collapse_deque(event_deque)
            process_event(event, dpts1_dir)
        delay = MONITOR_DELAY

except KeyboardInterrupt:
    [observer.stop() for observer in observers]
[observer.join() for observer in observers]
