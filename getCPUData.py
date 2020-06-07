# Autores: Rafael, Luis, Guilherme
#
#

import psutil
import psycopg2
import os
from datetime import datetime


con = psycopg2.connect(
          host='localhost',
          database='postgres',
          user='postgres',
          password='postgres'
 )


cpuUsage = psutil.cpu_percent(interval=0.5)

process = psutil.Process(os.getpid())
mem = process.memory_percent()

date = datetime.now()

cur = con.cursor()

cur.execute("INSERT INTO data (date, resource, value, mem) VALUES (%s,'cpu/mem', %s, %s)", [date, cpuUsage, mem])
con.commit()
