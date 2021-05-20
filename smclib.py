import serial
import sys
import glob
import serial.tools.list_ports
import fw_status

global ser


def serial_ports():
    '''
    :return: list comname which connected
    '''
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


block_list = [str(i) for i in range(16)]


def strconvert(response):
    global ERROR
    response = response.decode('utf-8')
    if response != '' and ser.isOpen():
        response = response.split('|')
    else:
        ERROR.append(f'Некоректный ответ с порта {ser.name}')
        return '0'
    return str(int(response[4], 16))


def ch_connect(name):
    '''
    :param name: comname
    :return: true if connect is successful
    '''
    global ser
    try:
        ser = serial.Serial(
            port=name.upper(),
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=2,
            timeout=0.1,
            writeTimeout=1,
        )
        return True
    except:
        return False


def ch_disconnect():
    '''
    close from com port
    '''
    global ERROR
    if ser.isOpen():
        ser.close()


def command(nblock, register, cmd, data):
    """
    :param nblock: номер блока
    :param register: номер регистра
    :param cmd: команда чтения/запись
    :param data: слово состояния
    """
    global ser
    mode = ''
    STX = '%c' % 2
    HSC = '%c' % 0x7c
    bl = '%02x' % nblock
    Reg = '%03x' % register
    if cmd.upper() == 'R':
        mode = '%c' % 0x52
    elif cmd.upper() == 'W':
        mode = '%c' % 0x57
    ENQ = '%c' % 5
    DATA = '%04x' % data
    ETX = '%c' % 3
    request = f'{STX}{HSC}{bl}{HSC}{Reg}{HSC}{mode}{HSC}' \
              f'{DATA}{HSC}{ENQ}{HSC}{ETX}'.encode('utf-8')
    # print('Request is:  ', request)
    ser.write(request)
    mes = ser.readline()
    return mes


def reply(bl_number):
    '''
    :param bl_number: number of block
    :param com_name: name com port
    :return: dict 16 bit
    '''
    global ERROR
    try:
        if ser.isOpen:
            req = command(int(bl_number), 0, "R", 0)
            req = strconvert(req)
            req = str(bin(int(req)))[2:]
            req = '%016d' % int(req)
            req = list(req)[::-1]
            ch_disconnect()
    except:
        req = ['0'] * 16
    res = dict(firstbit=req[0],
               twobit=req[1],
               threebit=req[2],
               fourbit=req[3],
               fivebit=req[4],
               sixbit=req[5],
               sevenbit=req[6],
               eightbit=req[7],
               ninebit=req[8],
               tenbit=req[9],
               elevenbit=req[10],
               twentybit=req[11],
               thirtybit=req[12],
               fourteenbit=req[13],
               fifteenbit=req[14],
               sixteenbit=req[15],
               bl_number=str(bl_number),
               )
    return res


def pre_parse(mes):
    if mes != '':
        mes = mes.split('|')[4]
        mes = int(str(bin(int(mes)))[2:])
        mes = '%016d' % mes
        mes = str(mes)
        p = [int(i) for i in mes][::-1]
        resp = []
        for k in range(len(p)):
            if p[k] == 1:
                resp.append(k)
    else:
        resp = [16]
    return resp


def parse(mes):
    mes = pre_parse(mes)
    answer = []
    for m in mes:
        answer.append(fw_status.d[m])
    message = ' '.join(answer)
    return message


def parse_st(message):
    message = message.decode()
    mes = message.split('|')[4]
    return int(mes, 16)