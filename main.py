import time
import requests
from smclib import *
import const


def answer_user_bot():
    answer = []
    for key, value in const.com.items():
        try:
            ch_connect(key)
            block = int(value)
            mes = command(block, 0, 'R', 0).decode()
            mes = parse(mes)
            mes_2 = command(block, 345, 'R', 0)
            mes_2 = parse_st(mes_2)
            answer.append(f'<b>{key}:{value}</b>\n{mes}'
                          f'<i>Число пропущенных стартов:</i> {mes_2}\n')
            command(block, 345, 'W', 0)
            ch_disconnect()
        except:
            answer.append(f'{key}:{value}\nОшибка подключения\n')
    ch_disconnect()
    message = '\n'.join(answer)
    data = {
        'chat_id': const.MY_ID,
        'text': message,
        'parse_mode': 'HTML',
    }
    url = const.URL.format(
        token=const.TOKEN,
        method=const.SEND_METH
    )
    requests.post(url, data=data)


while True:
    answer_user_bot()
    time.sleep(const.__period)
