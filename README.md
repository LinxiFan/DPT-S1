# DPT-S1 script

## Required libs

- Willus' [K2pdfopt](http://www.willus.com/k2pdfopt/)

Note: v2.36 crashes on OS X Sierra with error message "killed: 9". Use v2.35 instead. 

- Watchdog: for monitoring file system change

## Installation 

`pip install dpts1`

## Usage

```
dpts1 <DPT-S1-destination-folder> <Mendeley-folder> <other-folders ...>
```

- `DPT-S1-destination-folder`: to which the adjusted PDF files will be copied.

- `Mendeley-folder`: will not trigger if a new file is added (i.e. trigger_on_create=False). Only triggers if a file is renamed, because Mendeley auto-renames pdfs in its monitored directory. 

- `other-folders`... : any number of other folders to be monitored. Will trigger on new files. 
