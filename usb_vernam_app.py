#サービス名を入力するとアカウントとパスワードを検索できるアプリ。パスワードは独自に暗号化して保存
#変更
import PySimpleGUI as sg
import csv,pyperclip,string,random

sg.theme('DarkAmber')
table = string.ascii_letters + ' ' + '0123456789'


def verification():
    #usbが刺さっているかを確認する。もし刺さっていなければ終了、刺さっていたらその後の処理に進む
    layout = [
        [sg.Text('Plug in usb',font=('Meiryo',20))],
        [sg.Button('OK',font=('Meiryo',20),key='btn_1')]
    ]
    window = sg.Window('verification',layout)
    while True:
        event,value = window.read()
        if event == None:
            break
        if event == 'btn_1':
            try:
                with open('/Volumes/USB_name/key_data.csv','r+',encoding='utf-8') as f: #USB_nameにはUSBメモリにつけた任意の名前を各々の環境で書き換える
                    reader = csv.reader(f)
                    get_elems = [i for i in reader]
                    gen_gui()
                    break
            except:
                window.close()
                sg.popup('usb is not stuck')
    window.close()



def gen_gui():
    layout = [
        [sg.Text('select mode',font=('Meiryo',20))],
        [sg.Button('add service',font=('Meiryo',20),key='btn_1')],
        [sg.Button('find service',font=('Meiryo',20),key='btn_2')]
    ]

    window = sg.Window('select mode',layout)

    while True:
        event,value = window.read()
        if event == None:
            break
        if event == 'btn_1':
            add_service()
            break
        elif event == 'btn_2':
            find_service()
            break
    window.close()


def add_service():
    layout = [
        [sg.Text('Sevice name',size=(13,1),font=('Meiryo',20)),sg.InputText(font=('Meiryo',20),key='input_text1')],
        [sg.Text('Account name',size=(13,1),font=('Mieryo',20)),sg.InputText(font=('Meiryo',20),key='input_text2')],
        [sg.Text('password',size=(13,1),font=('Meiryo',20)),sg.InputText(font=('Meiryo',20),key='input_text3')],
        [sg.Button('Register',font=('Meiryo',20),key='btn_1')],
        [sg.Button('return←',font=('Meiryo',20),key='btn_2')]
    ]

    window = sg.Window('add_service',layout)

    while True:
        event,value = window.read()
        if event == None:
            break
        if event == 'btn_1':
            elems = [value['input_text1'], value['input_text2'], value['input_text3']]
            write_csv(encrypt(elems))
            sg.popup('complete')
        if event == 'btn_2':
            window.close()
            gen_gui()
    window.close()


def write_csv(data):
    write_data = [data[0],data[1],data[2]]
    key = [data[0],data[3]]
    with open('/Users/runeyamaguchi/Documants/data/find_service.csv','a+',encoding='utf-8') as f:  #暗号を保存するファイル名を環境に合わせて変更
        writer = csv.writer(f)
        writer.writerow(write_data)
    with open('/Volumes/RUNE03/key_data.csv','a+',encoding='utf-8') as f:  #鍵を保存するファイルパスを環境に合わせて変更
        writer = csv.writer(f)
        writer.writerow(key)


def encrypt(data):
    service = data[0]
    account = data[1]
    plane_text = data[2]
    pt_index = [format(table.find(i),'b').zfill(8) for i in plane_text]
    key = gen_key(pt_index)
    cipher = [xor(i,j) for i,j in zip(pt_index,key)]  #平文と鍵の排他的論理和から暗号を生成
    return service,account,cipher,key


def find_service():
    data = read_csv()
    dic = data[0]
    dic2 = data[1]
    layout = [
        [sg.Text('Search from account',font=('Meriyo',20)),sg.InputText(default_text='Enter the service name you want to find.',font=('Meriyo',20),key='in_text1')],
        [sg.Button('search',font=('Meiryo',20),key='btn_1')],
        [sg.Text('Result',font=('Meiryo',20))],
        [sg.Text('Service Name',size=(15,1),font=('Meiryo',20)),sg.InputText(font=('Meiryo',20),key='out_1')],
        [sg.Text('User Name',size=(15,1),font=('Meiryo',20)),sg.InputText(font=('Meiryo',20),key='out_2')],
        [sg.Text('Password',size=(15,1),font=('Meiryo',20)),sg.InputText(font=('Meiryo',20),key='out_3')],
        [sg.Button('return←',font=('Meiryo',20),key='btn_2')]
    ]

    window = sg.Window('find_service',layout)

    while True:
        event, value = window.read()
        if event == None:
            break
        if event == 'btn_1':
            ser_name = value['in_text1']
            window['out_1'].Update(ser_name)
            window['out_2'].Update(dic[ser_name][0])  #dicのvalueは二次元配列で[アカウント名,パスワード]の順に格納されている
            cipher = dic[ser_name][1].strip('[]').replace("'",'').replace(' ','').split(',')  #文字列をリストにするための操作
            key = dic2[ser_name].strip('[]').replace("'",'').replace(' ','').split(',')
            password = decrypt(cipher,key)
            window['out_3'].Update(password)
            pyperclip.copy(dic[ser_name][1])
        if event == 'btn_2':
            window.close()
            gen_gui()
    window.close()


def read_csv():
    dic = {}
    dic2 = {}
    with open('/Users/runeyamaguchi/Documents/data/find_service.csv','r+',encoding='utf-8') as f:
        reader = csv.reader(f)
        for i in reader:
            dic[i[0]] = [i[1],i[2]]
    with open('/Volumes/RUNE03/key_data.csv','r+',encoding='utf-8') as f:
        reader = csv.reader(f)
        for j in reader:
            dic2[j[0]] = j[1]
    return dic,dic2  #戻り値は暗号文と鍵になるのでこの戻り値同士の排他的論理和が平文になる(インデックス番号の2進数)


def xor(value_a,value_b):
    data = []
    for i,j in zip(value_a,value_b):
        if i == '1' and j == '0':
            data.append('1')
        elif i == '0' and j == '1':
            data.append('1')
        else:
            data.append('0')
    data = ''.join(data)
    return data


def gen_key(plane_text):
    keys = [format(random.randint(0,255),'b').zfill(8) for i in range(len(plane_text))]
    return keys


def decrypt(cipher,key):
    decrypt = [xor(i,j) for i,j in zip(cipher,key)]
    pt = [int(i,2) for i in decrypt]
    plane_text = ''.join([table[i] for i in pt])
    return plane_text


verification()
