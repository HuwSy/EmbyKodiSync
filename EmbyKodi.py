#!/usr/bin/env python
import sqlite3
import os
import time
from datetime import datetime

print("stopping services")
os.system('/storage/.kodi/addons/service.system.docker/bin/docker stop emby')
os.system('systemctl stop kodi')
time.sleep(5)

print("connecting db k")
conK = sqlite3.connect('/storage/.kodi/userdata/Database/MyVideos119.db')
curK = conK.cursor()

print("connecting db e")
conE = sqlite3.connect('/storage/.emby/data/library.db')
curE = conE.cursor()

print("selecting db k")
curK.execute("select strPath || strFilename path, playcount, f.idfile, b.timeinseconds from files f join path p on p.iDpath = f.idPath left join bookmark b on b.idfile = f.idfile where path like '%' order by path;")
print("selecting db e")
curE.execute("select path, playcount, m.userdatakeyid, u.playbackPositionTicks from mediaitems m left join userdatas u on m.userdatakeyid = u.userdatakeyid where path like '%' order by path;")

print("stubing dbs")
p = {}
d = {}
k = {}
e = {}

print("looping dbs")
for rowK in curK:
  r = rowK[0].lower()
  if str(rowK[3]) == "None":
    d[r] = 0
  else:
    d[r] = rowK[3] * 10000000
  if str(rowK[1]) == 'None':
    p[r] = 0
  else:
    p[r] = rowK[1]
  k[r] = rowK[2]
  print(rowK)

for rowE in curE:
  r = rowE[0].lower()
  if str(rowE[3]) == "None":
    if not r in d:
      d[r] = 0
  else:
    if r in d:
      if p[r] < rowE[1]:
        d[r] = rowE[3]
      elif p[r] > rowE[1]:
        d[r] = d[r]
      elif rowE[3] > d[r]:
        d[r] = rowE[3]
    else:
      d[r] = rowE[3]
  if str(rowE[1]) == 'None':
    if not r in p:
      p[r] = 0
  else:
    if r in p:
      if rowE[1] > p[r]:
        p[r] = rowE[1]
    else:
      p[r] = rowE[1]
  e[r] = rowE[2]
  print(rowE)

for key in k:
  print('update files set playcount = ' + str(p[key]) + ' where idfile = ' + str(k[key]) + ';')
  if d[key] > 0:
    tot = conK.total_changes
    curK.execute('update bookmark set timeinseconds = ' + str(d[key]/10000000) + ' where idfile = ' + str(k[key]) + ' and type = 1;')
    conK.commit()
    if tot == conK.total_changes:
      curK.execute('insert into bookmark (idfile,timeInSeconds,player,type) values (' + str(k[key]) + ',' + str(d[key]/10000000) + ',"VideoPlayer",1);')
  else:
    curK.execute('delete from bookmark where idfile = ' + str(k[key]) + ' and type = 1;')
  if p[key] > 0:
    #curK.execute('update files set lastPlayed = "' + str(datetime.now())[:19] + '" where idfile = ' + str(k[key]) + ' and lastPlayed is null;')
    curK.execute('update files set playcount = ' + str(p[key]) + ' where idfile = ' + str(k[key]) + ';')
  else:
    curK.execute('update files set lastPlayed = null, playcount = null where idfile = ' + str(k[key]) + ';')
  conK.commit()
  print(conK.total_changes)

for key in e:
  played = '0'
  if p[key] > 0:
    played = '1'
  try:
    print('insert or ignore into userdatas values (' + str(e[key]) + ',1,0,' + played + ',' + str(p[key]) + ',0,0,0,0,0,0,0);')
    curE.execute('insert or ignore into userdatas values (' + str(e[key]) + ',1,0,' + played + ',' + str(p[key]) + ',0,' + str(d[key]) + ',0,0,0,0,0);')
    conE.commit()
  finally:
    print('update userdatas set played = ' + played + ', playcount = ' + str(p[key]) + ' where userdatakeyid = ' + str(e[key]) + ';')
    curE.execute('update userdatas set played = ' + played + ', playcount = ' + str(p[key]) + ', playbackPositionTicks = ' + str(d[key]).split('.')[0] + ' where userdatakeyid = ' + str(e[key]) + ';')
    conE.commit()
  print(conE.total_changes)

curK.close()
conK.close()
curE.close()
conE.close()

print("starting apps")
time.sleep(5)
os.system('systemctl start kodi')
os.system('/storage/.kodi/addons/service.system.docker/bin/docker start emby')

