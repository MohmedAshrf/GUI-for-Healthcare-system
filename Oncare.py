import PySimpleGUI as sg
import json
import pyrebase
import random
import time
config = {
    "apiKey": "AIzaSyDxrYU6VgX2_aTRFpTkEXVo85BrBY57XTY",
  "authDomain": "spry-autumn-250814.firebaseapp.com",
  "databaseURL": "https://spry-autumn-250814-default-rtdb.firebaseio.com",
  "projectId": "spry-autumn-250814",
  "storageBucket": "spry-autumn-250814.appspot.com",
  "messagingSenderId": "69638460722",
  "appId": "1:69638460722:web:c75b2b5a01e8c18d60b32b"
}

class keyboard():
    def __init__(self, location=(None, None), font=('Arial', 16)):
        sg.theme('DarkPurple2')
        self.font = font
        numberRow = '@1234567890'
        topRow = 'QWERTYUIOP'
        midRow = 'ASDFGHJKL'
        bottomRow = 'ZXCVBNM.'
        keyboard_layout = [[sg.Button(c, key=c, size=(4, 2), font=self.font) for c in numberRow] + [
            sg.Button('⌫', key='back', size=(4, 2), font=self.font),
            sg.Button('Esc', key='close', size=(4, 2), font=self.font)],
            [sg.Text(' ' * 4)] + [sg.Button(c, key=c.lower(), size=(4, 2), font=self.font) for c in
                               topRow] + [sg.Stretch()],
            [sg.Text(' ' * 11)] + [sg.Button(c, key=c.lower(), size=(4, 2), font=self.font) for c in
                                midRow] + [sg.Stretch()],
            [sg.Text(' ' * 18)] + [sg.Button(c, key=c.lower(), size=(4, 2), font=self.font) for c in
                                bottomRow] + [sg.Stretch()]]

        self.window = sg.Window('keyboard', keyboard_layout,
                                grab_anywhere=True, keep_on_top=True, alpha_channel=0,
                                no_titlebar=True, element_padding=(5, 5), location=location, finalize=True,margins=(5, 5))
        self.hide()

    def _keyboardhandler(self):
        if self.event is not None:
            if self.event == 'close':
                self.hide()
            elif len(self.event) == 1:
                self.focus.update(self.focus.Get() + self.event)
            elif self.event == 'back':
                Text = self.focus.Get()
                if len(Text) > 0:
                    Text = Text[:-1]
                    self.focus.update(Text)

    def hide(self):
        self.visible = False
        self.window.Disappear()

    def show(self):
        self.visible = True
        self.window.Reappear()

    def togglevis(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def update(self, focus):
        self.event, _ = self.window.read(timeout=0)
        if focus is not None:
            self.focus = focus
        self._keyboardhandler()

    def close(self):
        self.window.close()
        sg.theme('DarkPurple')
        




Valid_user = False
email = ''
password = ''

HP= 0
SpO2=0
ecg= 0
pressure =0
temp =0

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
    
sg.theme('DarkPurple')
#PROGRESS BAR
def progress_bar(id,token):
    layout = [[sg.Text('Uploading ...')],
            [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progbar', bar_color=('brown','white'))],
            [sg.Cancel()]]

    window = sg.Window('Please wait', layout)
    for i in range(100):
        event, values = window.read(timeout=1)
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        if i ==50:
            upload_readings(id,token)
            window['progbar'].update_bar(i + 50)
        window['progbar'].update_bar(i + 1)
    window.close()


def create_account(name='',age='',phone=''):
    global email, password,Valid_user
    if Valid_user: #create new user and delete the past email and password
        email=''
        password = ''
        
    layout = [[sg.Text("Email", size =(15, 1),font=16), sg.InputText(email,key='-email-', font=16)],
             [sg.Text("Confirm Email", size =(15, 1), font=16), sg.InputText(email,key='-remail-', font=16)],
             [sg.Text("New Password", size =(15, 1), font=16), sg.InputText(password,key='-pwd-', font=16, password_char='*')],
              [sg.Text("Name", size =(15, 1), font=16), sg.InputText(name,key='-name-', font=16)],
              [sg.Text("Age", size =(15, 1), font=16), sg.InputText(age,key='-age-', font=16)],
              [sg.Text("Phone Number", size =(15, 1), font=16), sg.InputText(phone,key='-phone-', font=16)],
             [sg.Button("Submit"), sg.Button("Cancel")]]
    window = sg.Window("Sign Up", layout, grab_anywhere=True, no_titlebar=False, finalize=True,location=(400,70))
    window['-email-'].bind('<FocusIn>', '')
    window['-remail-'].bind('<FocusIn>', '')
    window['-pwd-'].bind('<FocusIn>', '')
    window['-name-'].bind('<FocusIn>', '')
    window['-age-'].bind('<FocusIn>', '')
    window['-phone-'].bind('<FocusIn>', '')
    
    
    location = window.current_location()
    location = location[0]-100, location[1]+300
    kboard = keyboard(location)
    
    focus = None
    while True:
        cur_focus = window.find_element_with_focus()
        if cur_focus is not None:
            focus = cur_focus   
            
        event,values = window.read(timeout=100, timeout_key='timeout')
        if focus is not None:
            kboard.update(focus)
        if event == '-email-' or event == "-remail-" or event == "-pwd-" or event == "-name-" or event == "-age-" or event == "-phone-":
            kboard.show()
            kboard.update(focus)
        elif event == 'Cancel' or event == sg.WIN_CLOSED:
            Valid_user=False
            break    
        else:
            if event == "Submit":
                kboard.close()
                password = values['-pwd-']
                email = values['-email-']
                name = values["-name-"]
                age = values["-age-"]
                phone = values["-phone-"]
                if values['-email-'] != values['-remail-']:
                    sg.popup_error("Error: please check the re-enterd email", font=16)
                    continue
                elif values['-email-'] == values['-remail-']:
                    try:
                        user_id , user_token = create_user(email,password,name,age,phone)
                        window.close()
                        sg.popup("Sucessfully created user. uploading the data...")
                        Valid_user = True
                        progress_bar(user_id,user_token)
                        sg.popup("Data uploaded. login to display")
                        login_existing(email,password)
                        break
                    except Exception as e:
                        res= json.loads(e.args[1])
                        Valid_user = False
                        if res["error"]["message"] == "INVALID_EMAIL":
                            print("please write a valid email")
                            sg.popup_auto_close("\t\t\t\t\t\t\t\t\t\t\t \n Invalid Email \n\t\t\t\t\t\t\t\t\t\t",title="Error")
                            kboard.close()
                            create_account()
                            break
                        elif res["error"]["message"] == "EMAIL_EXISTS":
                            print("please login")
                            sg.popup_ok("\t\t\t\t\t\t\t\t\t\t\t \nEmail exists\n\t\t\t\t\t\t\t\t\t\t",title="Error")
                            login_existing(email,password)
                            kboard.close()
                            window.close()
                            break
                        elif res["error"]["message"].split(" ")[0] == "WEAK_PASSWORD":
                            print("please enter longer password")
                            sg.popup_ok("\t\t\t\t\t\t\t\t\t\t\t \nWeek password\n\t\t\t\t\t\t\t\t\t\t",title="Error")
                            kboard.close()
                            create_account(name,age,phone)
                            break
                        else:
                            print("please review the error: "+ res["error"]["message"])
                break
    kboard.close()
    window.close()
    


def login_existing(e="",p=""):
    global email,password,Valid_user
    layout = [[sg.Text('Please enter you email and password')],
            [sg.Text("Email", size =(15, 1), font=16),sg.InputText(e,key='-email-', font=16)],
            [sg.Text("Password", size =(15, 1), font=16),sg.InputText(p,key='-pwd-', password_char='*', font=16)],
            [sg.Button('Ok'),sg.Button('Cancel')]]

    window = sg.Window('Login', layout,grab_anywhere=True, no_titlebar=False, finalize=True,location=(400,70),border_depth=2)
    
    window['-email-'].bind('<FocusIn>', '')
    window['-pwd-'].bind('<FocusIn>', '')
    
    location = window.current_location()
    location = location[0]-100, location[1]+200
    kboard = keyboard(location)
    
    focus = None
    
    
    while True:
        cur_focus = window.find_element_with_focus()
        if cur_focus is not None:
            focus = cur_focus   
        event,values = window.read(timeout=100, timeout_key='timeout')
        if focus is not None:
            kboard.update(focus)
        if event == '-email-' or event == "-pwd-":
            kboard.show()
            kboard.update(focus)
            
        elif event == 'Cancel' or event == sg.WIN_CLOSED:
            email=""
            password=""
            break
        else:
            if event == "Ok":
                kboard.close()
                password = values['-pwd-']
                email = values['-email-']
                try:
                    user_id,user_token = login_to_user(email,password)
                    window.close()
                    sg.popup("Sucessfully logged in")
                    Valid_user = True #loged in successfully 
                    progress_bar(user_id,user_token)
                    #sg.popup("Data uploaded")
                    read_data(get_data(user_id,user_token))
                    display_data(user_id,user_token)
                except Exception as e:
                    res= json.loads(e.args[1])
                    if res["error"]["message"] == "INVALID_PASSWORD":
                        print("Please check the password and try again")
                        sg.popup_auto_close("\t\t\t\t\t\t\t\t\t\t\t \n Please check the password and try again\n\t\t\t\t\t\t\t\t\t\t",title="Error")
                        window.close()
                        password = ""
                        login_existing(email,password) #password incorrect retry
                        break
                    elif res["error"]["message"] == "INVALID_EMAIL":
                        print("Please check the Email and try again")
                        sg.popup_auto_close("\t\t\t\t\t\t\t\t\t\t\t \n Please check the Email and try again\n\t\t\t\t\t\t\t\t\t\t",title="Error")
                        kboard.close()
                        window.close()
                        break
                    elif res["error"]["message"] == "EMAIL_NOT_FOUND":
                        print("Email not found please signup")
                        sg.popup_auto_close("\t\t\t\t\t\t\t\t\t\t\t \n Email not found please signup \n\t\t\t\t\t\t\t\t\t\t",title="Error")
                        kboard.close()
                        window.close()
                        create_account()
                    else:
                        print("Please check the error",res["error"]["message"])
                        kboard.close()
                        window.close()
                        break
                break
    kboard.close()
    window.close()
    
def display_data(id="",token=""):
    layout = [[sg.Text("Heart Beat", size =(15, 1),font=16), sg.Text(HP, font=16,key='-HP-')],
              [sg.Text("Tempreture", size =(15, 1),font=16), sg.Text(temp, font=16,key='-temp-')],
              [sg.Text("SpO2", size =(15, 1),font=16), sg.Text(SpO2, font=16,key='-sp-')],
              [sg.Text("Pressure", size =(15, 1),font=16), sg.Text(pressure, font=16 ,key='-pressure-')],
              [sg.Text("ECG", size =(15, 1),font=16), sg.Text(ecg, font=16 ,key='-ecg-')],
                [sg.Button("Cancel")]]
    
    window=sg.Window("Readings", layout,finalize=True,element_padding=(5, 5))
    while True:
        event, values = window.read(timeout=1)
        if token != "": #if user has signed in
            read_data(upload_readings(id,token)) #upload the data then read
        else:
            read_data(set_data_UART()) #read the data wihout upload
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            window.close()
            break
        else:
            window['-HP-'].update(HP)
            window['-temp-'].update(temp)
            window['-sp-'].update(SpO2)
            window['-pressure-'].update(pressure)
            window['-ecg-'].update(ecg)

    
def login_to_user(email,passwd):
    user = auth.sign_in_with_email_and_password(email,passwd)
    return (user["localId"],user["idToken"])

    
def set_data_UART():
    #TODO
    
    data = {"HP":random.randint(20,100),"temp":random.randint(20,100),\
        "SpO2":random.randint(20,100),"ecg":random.randint(10,200),"pressure":80}
    return data

def upload_readings(uid,token):
    data = set_data_UART()
    db.child("patients").child(uid).child("readings").set(data,token)
    return data

def create_user(email,passwd,name,age,phone):
    user = auth.create_user_with_email_and_password(email,passwd)
    uid = user["localId"]
    token = user["idToken"]
    data={"Name":name,"age":age,"Email":email,"phoneNumber":phone}
    db.child("patients").child(uid).set(data,token)
    return (uid,token)
    
def get_data(uid,token):
    return dict(db.child("patients").child(uid).child("readings").get(token).val())

def read_data(dic):
    global HP,SpO2,ecg,pressure,temp
    HP = dic["HP"]
    SpO2 = dic["SpO2"]
    ecg = dic["ecg"]
    pressure = dic["pressure"]
    temp = dic["temp"]

    

def select_option():
    column_to_be_centered = [[sg.Image(filename="oncarelogo.png", key='-Logo-',pad=(60,0,0,0))],
                            [sg.Image(filename="oncare.png", key='-IMAGE-')],
                             [sg.Text('Welcome!',size=(30,1),justification='c')],
                             [sg.Text('Please Select an Option',size=(30,1),justification='c')],
            [sg.Button('Login',size=(30,2))],
            [sg.Button('Signup',size=(30,2))],
            [sg.Button('Display Offline',size=(30,2))],
            [sg.Button('Cancel',size=(30,2))]]
    
    layout = [[sg.Text(key='-EXPAND-', font='ANY 1', pad=(0, 0))],  # the thing that expands from top
              [sg.Text('', pad=(0,0),key='-EXPAND2-'),              # the thing that expands from left
               sg.Column(column_to_be_centered, vertical_alignment='center', 
                         justification='center',  k='-C-')]]

    window = sg.Window('OnCare', layout, resizable=True,finalize=True,grab_anywhere=True, no_titlebar=False)
    window.Maximize()
    window['-C-'].expand(True, True, True)
    window['-EXPAND-'].expand(True, True, True)
    window['-EXPAND2-'].expand(True, False, True)
    while True:
        event, values = window.read(timeout=100)
        if(Valid_user):
            id,token = login_to_user(email,password)
            read_data(upload_readings(id,token))
        else:
            read_data(set_data_UART())
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        elif (event == "Login"):
            login_existing()
        elif (event == "Signup"):
            create_account()
        elif (event == "Display Offline"):
            
            display_data()
            
    window.close()

    
select_option()



