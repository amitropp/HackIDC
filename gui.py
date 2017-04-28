import easygui
def yes_no_msg(msg):
    return easygui.ynbox(msg, 'Logeasy')  # show a Continue/Cancel dialog

def ok_msg(msg):
    return easygui.msgbox(msg, 'Logeasy')


