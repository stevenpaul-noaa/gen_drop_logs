import os
import sys
import datetime

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
#scandirname = filedialog.askdirectory(initialdir='E:/AVAPSDATA/',  title='INPUT SCAN DIRECTORY')
#scandirname = filedialog.askdirectory(initialdir='\\\\10.10.60.240/aoc-storage/SEB-Engineering/AVAPS/Mirrors',  title='INPUT SCAN DIRECTORY')
scandirname = filedialog.askdirectory(initialdir='\\\\10.10.60.240/aoc-storage/AVAPS/Data/Mirrors',  title='INPUT SCAN DIRECTORY')
#scandirname = filedialog.askdirectory(initialdir='.',  title='INPUT SCAN DIRECTORY')
#outdirname = filedialog.askdirectory(initialdir='d:/AVAPS/inventory/drop_logs/',  title='OUTPUT DIRECTORY')
#outdirname = filedialog.askdirectory(initialdir=os.path.expanduser('~')+'/Documents/', title='OUTPUT DIRECTORY')
outdirname = filedialog.askdirectory(initialdir=os.getcwd(), title='OUTPUT DIRECTORY')

from tkinter import simpledialog
start_date = simpledialog.askstring("INPUT", "START DATE:\nYYYYMMDD",
                                initialvalue=datetime.datetime.utcnow().strftime("%Y")+"0101",
                                parent=root)

end_date = simpledialog.askstring("INPUT", "END DATE:\nYYYYMMDD",
                                initialvalue=datetime.datetime.utcnow().strftime("%Y%m%d"),
                                parent=root)

AIRCRAFT = simpledialog.askstring("INPUT", "AIRCRAFT IDENT:\nA = ALL\nH = N42\nI = N43\nN = N49\nO = NOT H, I, OR N",
                                initialvalue='A',
                                parent=root).upper()

flights={}
minis={}
char='-'
for root, dirs, files in os.walk(scandirname, topdown=False):
  sys.stdout.write('\r'+char)
  if char == '-':
    char = '\\'
  elif char == '\\':
    char = '|'
  elif char == '|':
    char = '/'
  elif char == '/':
    char = '-'
    
  mission_folder=os.path.basename(root)
  mission_folder_code=mission_folder[-2]
  if (AIRCRAFT != 'A'):
    if (AIRCRAFT == 'O'):
      if (mission_folder_code=='H' or mission_folder_code=='I' or mission_folder_code=='N'):
        continue
    elif ( AIRCRAFT != mission_folder_code ):
      continue
  
  #print('SCANNING: '+root)
  
  for name in sorted(files):
    if (name[0] == 'D') and (len(name) == 18):
      dateint=int(name[1:9])
      startdateint=int(start_date)
      enddateint=int(end_date)
      if (dateint < startdateint):
        continue
      if (dateint > enddateint):
        continue
      #if (name[1:5] != '2019'):
      #  continue
      
      #print(name)

      if not mission_folder in flights:
        flights[mission_folder]=0
      
      flights[mission_folder]=flights[mission_folder]+1


from datetime import datetime

#run through each FLID
prevmon=''
of=open(outdirname+'/'+datetime.now().strftime("%Y%m%d_%H%M%S_")+'missions_summary.csv',"w")
#of.write('test123\n')
of.write('SCAN DIR,\''+scandirname+'\'\n')
of.write('OUT DIR,\''+outdirname+'\'\n')
of.write('START DATE,\''+start_date+'\'\n')
of.write('END DATE,\''+end_date+'\'\n')
of.write('AIRCRAFT,\''+AIRCRAFT+'\'\n')

for flid in sorted(flights):
    mon=flid[0:6]
    print(flid, flights[flid])
    if mon != prevmon:
        of.write('\n')
    of.write(str(flid)+','+str(flights[flid])+'\n')
    prevmon=mon
of.close()
from tkinter import messagebox
messagebox.showinfo("Information","PROGRAM COMPLETE")