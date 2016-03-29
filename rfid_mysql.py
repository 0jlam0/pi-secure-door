#!/usr/bin/python
import RPi.GPIO as GPIO
import MFRC522
import spi
import signal
import MySQLdb
import datetime
import time

db = MySQLdb.connect(host="localhost",user="root",passwd="password",db="rfid")
cur = db.cursor()

GPIO.setmode(GPIO.BOARD)


continue_reading = True

def buzzer():
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7,1)
    time.sleep(.3)
    GPIO.output(7,0)

def LedOk():
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16,0)
    Relay1()
    time.sleep(1)
    GPIO.output(16,1)

def LedDeny():
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(12,0)
    time.sleep(2)
    GPIO.output(12,1)

def Relay1():
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18,0)
    time.sleep(3)
    GPIO.output(18,1)

#INICIALIZANDO LEDS
#LedOk()
#LedDeny()


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()
    cur.close()
    db.close()

signal.signal(signal.SIGINT, end_read)

MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."
while continue_reading:
  (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
  (status,backData) = MIFAREReader.MFRC522_Anticoll()

   #if status == MIFAReader.MI_OK:
     #print "TAG Detectada!!!"

###SI LEE TARJETA EMPEZAR
  if status == MIFAREReader.MI_OK:
    buzzer()
###OBTIENE EL TAGID
    tag = str(backData[0])+str(backData[1])+str(backData[2])+str(backData[3])+str(backData[4])
    v_userid= cur.execute("select id from users where tagid="+tag)

#OBTENER EL ID CON EL TAGID Y BUSCARLO EN LA LECTORA, ES DECIR, BUSCA QUE EL TAG ESTE ASIGNADO A UN USUARIO Y A LA LECTORA.
    cur.execute("commit")
    cur.execute("select id from users where tagid="+tag)
    row = cur.fetchone()
    
    if not row:
      print "TAG "+str(tag)+" desconocida!"
      print "Guardando registro en la tabla desconocido"
      sql0= '''INSERT INTO desconocido (tagid,nombre_lectora) values (%s,%s)'''
      cur.execute(sql0,(tag,'lectora_site'))
      cur.execute("commit")
      LedDeny()
    
    else:
        cur.execute("commit")
#        cur.execute("select users.id, users.tagid, lectoras.nombre_lectora from users, lectoras where nombre_lectora='lectora_site' and tagid="+tag)
#        sql1='''select userid ,nombre_lectora from lectoras where userid=%s and nombre_lectora=%s'''
        sql1='''select users.id,lectoras.nombre_lectora,users.tagid from users inner join lectoras on users.id=lectoras.userid where userid=%s and nombre_lectora=%s'''
        cur.execute(sql1, (str(row[0]),'lectora_site'))
        row = cur.fetchone()

######
###SI EL ID NO TIENE PERMISO EN LA LECTORA, GUARDAR EL REGISTRO EN BITACORA CON NO ACCESO
        if not row:
#          print "TAG "+str(tag)+" no autorizada en lectora_site!"
          cur.execute("commit")
          cur.execute("select id from users where tagid="+tag)
          row = cur.fetchone()
          print "TAG "+tag+" ---> "+str(row[0])+"---> No autorizada en esta lectora>"
          print "Guardando registro en la bitacora con NO ACCESO"
          sql2= '''INSERT INTO bitacora (userid,nombre_lectora,permiso) values (%s,%s,%s)'''
          cur.execute(sql2, (str(row[0]),'lectora_site','NO'))
          cur.execute("commit")

#      sql1= '''INSERT INTO desconocido (tagid,nombre_lectora) values (%s,%s)'''
#      cur.execute(sql1,(tag,'lectora_site'))
#      cur.execute("commit")

#      sql1= '''INSERT INTO desconocido (tagid, nombre_lectora) values (%s,%s)'''
#      cur.execute(sql1, (tag, 'lectora_site'))
#      cur.execute("commit")
          buzzer()
          LedDeny()
#-----------
        else:
### SI EL TAGID EXISTE EN LA TABLA USERS IMPRIME EL TAGID Y EL ID DEL USUARIO ##
            print "TAG autorizada "+tag+" ---> "+str(row[0])
            print "Guardando registro en la Base de Datos SI ACCESO"
            sql3= '''INSERT INTO bitacora (userid,nombre_lectora,permiso) values (%s,%s,%s)'''
            cur.execute(sql3, (str(row[0]),str(row[1]),'SI'))
            cur.execute("commit")


### BUSCA EL ID DEL USUARIO EN LA TABLA LECTORAS Y TAMBIEN DETECTA SI EL USUARIO TIENE ASIGNADO LA LECTORA PARA INGRESAR
#        cur.execute("commit")
#        sql3='''select * from lectoras where userid=%s and nombre_lectora=%s'''
#        cur.execute(sql3, (row[0], 'lectora_site'))
###SI EL ID DEL USUARIO EXISTE EN LA TABLA LECTORA Y TIENE ASIGNADA LA LECTORA ABRE LA PUERTA Y PRENDE LEDOK
#        row = cur.fetchone()
            LedOk()
            print "yes, abre puerta"
            print str(row[0])+"--> "+str(row[1])+"--lectora"+str(row[2])

#      if not row:
#      print "yes"	
#      print "Guardando registro en la Base de Datos"
#      else:
#      sql2= '''INSERT INTO bitacora (userid,nombre_lectora,permiso) values (%s,%s,%s)'''
#      cur.execute(sql2, (str(row[0]),'lectora_site','si'))
#      cur.execute("commit")
#      LedOk()
#		else:
