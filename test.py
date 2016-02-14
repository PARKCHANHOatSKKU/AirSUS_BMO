import curses
import time
import sys
import random
import serial
import traceback

pos1=3
pos2=22
pos11=pos1+14
pos22=pos2+10
#base setting for ncurses
screen = curses.initscr()
curses.curs_set(0)
screen.border(0)
screen.nodelay(True)
#END setting
#base str setting
screen.addstr(0, 3, "Air_sus control system form AMLAB")
screen.addstr(2, pos1, "Front_Left")
screen.addstr(2, pos2, "Front_Right")
screen.addstr(6, pos1, "Rear_Left")
screen.addstr(6, pos2, "Rear_Right")
screen.addstr(11, pos1, "BRK_P")
screen.addstr(14, pos1, "ACC_Th")
screen.addstr(17, pos1, "STR_Ag")
screen.addstr(11, pos2, "GPS")
screen.addstr(14, pos2, "ACC_z")
screen.addstr(17, pos2, "ACC_x")
screen.addstr(20, pos2, "Roll")
screen.addstr(23, pos2, "Pitch")
#base str setting end
screen.refresh()

def show_progress_FL(num):
    win1 = curses.newwin(3,16,3,pos1-1)
    win1.border(0)
    progB=' '
    for i in range(1,num+1):
        progB+='#'
    win1.addstr(1,0,progB)
    win1.refresh()

def show_progress_FR(num):
    win2 = curses.newwin(3,16,3,pos2-1)
    win2.border(0)
    progB=' '
    for i in range(1,num+1):
        progB+='#'
    win2.addstr(1,0,progB)
    win2.refresh()

def show_progress_RL(num):
    win3 = curses.newwin(3,16,7,pos1-1)
    win3.border(0)
    progB=' '
    for i in range(1,num+1):
        progB+='#'
    win3.addstr(1,0,progB)
    win3.refresh()

def show_progress_RR(num):
    win4 = curses.newwin(3,16,7,pos2-1)
    win4.border(0)
    progB=' '
    for i in range(1,num+1):
        progB+='#'
    win4.addstr(1,0,progB)
    win4.refresh()

def send_command(serial_port, cmd_msg):
    cmd_msg = '@' + cmd_msg.strip()
    crc = 0
    for c in cmd_msg:
        crc = crc^ord(c)
    serial_port.write(cmd_msg + '*%02X'%crc + '\r\n')
    #
    # wait for response 
    #    
    if(cmd_msg != '@trig'):
        while(True):
            line = serial_port.readline().strip()
            if(line[0] == '~'):
                return line


def parse_data_message_rpyimu(data_message):
    # $RPYIMU,39,0.42,-0.31,-26.51,-0.0049,-0.0038,-1.0103,-0.0101,0.0014,-0.4001,51.9000,26.7000,11.7000,41.5*1F
    
    data_message = (data_message.split('*')[0]).strip() # discard crc field  
    fields = [x.strip() for x in data_message.split(',')]
    
    if(fields[0] != '$RPYIMU'):
        return None
    
    sequence_number, roll, pitch, yaw, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, temperature = (float(x) for x in fields[1:])
    return (int(sequence_number), roll, pitch, yaw, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, temperature)
    
def read_data(serial_device):
    send_command(serial_port,'trig')
    line = serial_port.readline().strip()
    items = parse_data_message_rpyimu(line)
    return items

#
# set serial Device
#
if(len(sys.argv) < 2):
    serial_device = '/dev/ttyACM0'
else : 
    serial_device = sys.argv[1]
try:
    serial_port = serial.Serial(serial_device, 115200, timeout=1.0)
except serial.serialutil.SerialException:
    traceback.print_exc()
#
# Get version 
#
rsp = send_command(serial_port, 'version') 

#
# Data transfer mode : ASCII, TRIGGER 
#
rsp = send_command(serial_port, 'mode,AT')

#
# Select output message type 
#
rsp = send_command(serial_port, 'asc_out,RPYIMU')
#

while screen.getch() != ord('q'):
    timeb=time.time()
    #screen.addstr(20,pos1, str(timeb))
    show_progress_FL(random.randint(1,14))
    show_progress_FR(random.randint(1,14))
    show_progress_RL(random.randint(1,14))
    show_progress_RR(random.randint(1,14))
    itemss=read_data(serial_device)
    sequence_number, roll, pitch, yaw, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, temperature = itemss
    #data insert
    screen.addstr(15,pos2+6,str(accel_z))
    screen.addstr(18,pos2+6,str(accel_x))
    screen.addstr(21,pos2+6,str(roll))
    screen.addstr(24,pos2+6,str(pitch))
    #data insert END
    time.sleep(0.05)
    screen.refresh()

serial_port.close()
curses.endwin()
