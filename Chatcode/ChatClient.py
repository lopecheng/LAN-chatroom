#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Administrator'
import wx,time,sys,socket,thread,threading
reload(sys)
sys.setdefaultencoding( "utf-8" )

ADDR=('172.20.10.2',2640)
tcpCliSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcpCliSock.bind(('',0))
tcpCliSock.connect(ADDR)

class LoginFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title= u'登 录', size=(410,340))
        panel = wx.Panel(self,-1)
        self.Centre()

        self.recvfromseverlogindata = ''
        self.username = ''
        
        userphoto_img = wx.Image(r'myPhoto.png',wx.BITMAP_TYPE_ANY).Scale(90,90)
        self.userstaticbitmap = wx.StaticBitmap(panel,-1,wx.BitmapFromImage(userphoto_img),pos=(30,200))
        
        loginphoto_img = wx.Image(r'loginPhoto.png',wx.BITMAP_TYPE_ANY).Scale(430,180)
        self.loginstaticbitmap = wx.StaticBitmap(panel,-1,wx.BitmapFromImage(loginphoto_img),pos=(0,0))

        self.usernamestaticText = wx.StaticText(panel,-1,u'用 户 名:',pos=(145,200))
        self.usernamecomboBox = wx.ComboBox(panel,value='',pos=(205,200),size=(140,30))

        self.passwordstaticText = wx.StaticText(panel,-1,label=u'密     码:',pos=(145,230))
        self.passwordtextCtrl = wx.TextCtrl(panel,-1,'',pos=(205,230),size=(140,20),style=wx.TE_PASSWORD)

        self.loginButton = wx.Button(panel,label=u'登 录',pos=(145,260),size=(90,30))
        self.Bind(wx.EVT_BUTTON, self.OnButtonLogin, self.loginButton)
        self.registerButton = wx.Button(panel,label=u'注 册',pos=(265,260),size=(90,30))
        self.Bind(wx.EVT_BUTTON,self.OnButtonRegister, self.registerButton)

        self.SetSizeHints(430,360,430,360)

        thread.start_new_thread(self.run,())

    def OnButtonLogin(self,event):
        #function need to be repaired
        username = self.usernamecomboBox.GetValue()
        password = self.passwordtextCtrl.GetValue()
        if username != '':
            if password != '':
                tcpCliSock.send(('Login'+' '+username+' '+password).encode('gbk'))
                time.sleep(0.5)
                self.run()
            else:
                self.LoginTipsDialog(tip=u'请 输 入 密 码')
        else:
            self.LoginTipsDialog(tip=u'请 输 入 用 户 名')
    
    
    def checkLogin(self):
        returndata = self.recvfromseverlogindata.split(' ')
        if returndata[2] == '0':
            self.username = returndata[1]
            return True
        if returndata[2]=='1':
            self.LoginTipsDialog(tip=u'密 码 不 正 确')
            return False
        if returndata[2]=='2':
            self.LoginTipsDialog(tip=u'用 户 名 不 存 在')
            return False
        if returndata[2]=='3':
            self.LoginTipsDialog(tip=u'用 户 名 已 登 录')
            return False

    def run(self):
        data = (tcpCliSock.recv(1024)).decode('gbk')
        if data != '':
            self.recvfromseverlogindata = data
            if self.checkLogin():
                ChatroomFrame(self.username)
                self.Destroy()

    def LoginTipsDialog(self, tip):
        logindlg = wx.MessageDialog(self,tip,'Caution',wx.CANCEL|wx.OK|\
                                                         wx.ICON_QUESTION)
        if logindlg.ShowModal() == wx.ID_OK:
            logindlg.Destroy()
        
    def OnButtonRegister(self,event):
        RegisterFrame()
        self.Destroy()

class ChatroomFrame(wx.Frame):
    def __init__(self,username):
        wx.Frame.__init__(self, parent=None, id=-1, title=u' 欢 迎 进 入 FAMILY 聊 天 室', size=(670,542))
        self.panel = wx.Panel(self,-1)
        self.Centre()

        self.username = username
        tcpCliSock.send(('Flag'+' '+self.username+' '+'join').encode('gbk'))
        self.memberlist = []
        
        self.chatwindows = wx.TextCtrl(self.panel, -1, '', style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH, pos=(1,0), size=(438,280))

        string = u' --------------------------- 以  上  是  历  史  消  息 ----------------------------- '
        self.chattinghistroystaticText = wx.StaticText(self.panel, -1, string, pos=(1,280),size=(438,20))
        self.chattinghistroystaticText.SetForegroundColour('GREY')

        self.inputtextCtrl = wx.TextCtrl(self.panel, -1, '', style=wx.TE_MULTILINE, pos=(1,300),size=(438,120))

        self.sendButton = wx.Button(self.panel, label=u'发   送', pos=(280,422),size=(82,27))
        self.Bind(wx.EVT_BUTTON, self.thread_OnButtonSend, self.sendButton)
        self.closeButton = wx.Button(self.panel, label=u'退   出', pos=(365,422),size=(70,27))
        self.Bind(wx.EVT_BUTTON, self.OnCloseButton, self.closeButton)
        self.Bind(wx.EVT_CLOSE, self.OnCloseButton)
        
        self.memberlistBox = wx.ListBox(self.panel, -1, pos=(440,250), size=(195,200), choices = self.memberlist, style=wx.LB_SINGLE|wx.LB_SORT)
        onlinecount = self.memberlistBox.GetCount()
        self.onlinememberstaticText = wx.StaticText(self.panel, -1, u'         成        员  :  ('+ str(onlinecount) + ')', pos=(490,230), size=(150,20))

        self.visitstaticText = wx.StaticText(self.panel, -1 , u' 访  问  记  录 ：', pos=(440,5), size=(210,20))
        self.accessrecord = wx.TextCtrl(self.panel, -1, '', style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH, pos=(440,20), size=(195,205))

        gridBagSizerAll = wx.GridBagSizer(hgap=5, vgap=5)
        gridBagSizerAll.Add(self.chatwindows, pos=(0,0), flag=wx.ALL|wx.EXPAND, span=(5,5), border=0)
        gridBagSizerAll.Add(self.chattinghistroystaticText, pos=(5,0), flag=wx.ALL|wx.EXPAND, span=(1,5), border=0)
        
        gridBagSizerAll.Add(self.visitstaticText, pos=(0,5), flag=wx.ALL|wx.EXPAND, span=(1,1), border=0)
        gridBagSizerAll.Add(self.accessrecord, pos=(1,5), flag=wx.ALL|wx.EXPAND, span=(1,1), border=0)
        
        gridBagSizerAll.Add(self.inputtextCtrl, pos=(6,0), flag=wx.ALL|wx.EXPAND, span=(1,5), border=0)
        gridBagSizerAll.Add(self.sendButton, pos=(7,3), flag=wx.ALL|wx.EXPAND, span=(1,1), border=0)
        gridBagSizerAll.Add(self.closeButton, pos=(7,4), flag=wx.ALL|wx.EXPAND, span=(1,1), border=0)
        gridBagSizerAll.Add(self.memberlistBox, pos=(3,5), flag=wx.ALL|wx.EXPAND, span=(5,1), border=0)
        gridBagSizerAll.Add(self.onlinememberstaticText, pos=(2,5), flag=wx.ALL|wx.EXPAND, span=(1,1), border=0)

        gridBagSizerAll.AddGrowableCol(0,1)
        gridBagSizerAll.AddGrowableRow(3,1)

        self.panel.SetSizer(gridBagSizerAll)
        gridBagSizerAll.Fit(self)

        self.SetSizeHints(670,542,1000,1000)
        self.Show()

        thread.start_new_thread(self.run,())

    def run(self):
        tcpCliSock.send('MemberList'.encode('gbk'))
        while 1:
            recvfromserver = (tcpCliSock.recv(1024)).decode('gbk')
            if recvfromserver.startswith('Message'):
                thread.start_new_thread(self.updatechattingrecord,(recvfromserver,))
            elif recvfromserver.startswith('Flag'):
                thread.start_new_thread(self.updatevisitrecord,(recvfromserver,))
            elif recvfromserver.startswith('MemberList'):
                thread.start_new_thread(self.updatememberlist,(recvfromserver,))

    def updatechattingrecord(self, recv):
        temp = recv.split(' ')
        self.chatwindows.SetDefaultStyle(wx.TextAttr(wx.BLUE))
        sendtime = self.DateFormat(time.localtime())
        username = temp[1]
        self.chatwindows.AppendText(username+'  '+sendtime+'\n')
        self.chatwindows.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        temp.remove('Message')
        temp.remove(username)
        str = ''
        for item in temp:
            str += item + ' '
        self.chatwindows.AppendText(str+'\n')

    def updatevisitrecord(self, recv):
        temp = recv.split(' ')
        if temp[2] == 'join':
            jointime = self.DateFormat(time.localtime())
            self.accessrecord.SetDefaultStyle(wx.TextAttr(wx.GREEN))
            self.accessrecord.AppendText(temp[1]+' '+jointime+u' 进入了聊天室'+'\n')
            self.memberlist.append(temp[1])            
        if temp[2] == 'exit':
            leavetime = self.DateFormat(time.localtime())
            self.accessrecord.SetDefaultStyle(wx.TextAttr(wx.RED))
            self.accessrecord.AppendText(temp[1]+' '+leavetime+u' 离开了聊天室'+'\n')
            self.memberlist.remove(temp[1])
        self.memberlist.sort()
        self.memberlistBox.Set(self.memberlist)
        self.onlinememberstaticText.SetLabel(u'         成        员  :  ('+str(self.memberlistBox.GetCount()) + ')')

    def updatememberlist(self, recv):
        li = recv.split(' ')
        temp = li[1].split(',')
        for i in temp:
            self.memberlist.append(i)
        self.memberlistBox.Set(self.memberlist)
        self.onlinememberstaticText.SetLabel(u'         成        员  :  ('+str(self.memberlistBox.GetCount()) + ')')
    
    def OnCloseButton(self, event):
        #function need to be repaired
        dlg = wx.MessageDialog(self,u'确 定 退 出','Caution',wx.CANCEL|wx.OK|\
                                                        wx.ICON_QUESTION)
        if dlg.ShowModal()==wx.ID_OK:
            tcpCliSock.send(('Flag'+' '+self.username+' '+'exit').encode('gbk'))
            dlg.Destroy()
            self.Destroy()

    def thread_OnButtonSend(self,event):
        thread.start_new_thread(self.OnButtonSend,(event,))

    def OnButtonSend(self, event):
        #function need to be repaired
        message = (self.inputtextCtrl.GetValue()).strip()
        if len(message)>0:
            tcpCliSock.send(('Message'+' '+self.username+' '+message).encode('gbk'))
            self.inputtextCtrl.SetValue('')
        else:
            dlg = wx.MessageDialog(self,u'请 输 入 内 容!','Caution',wx.CANCEL|wx.OK|\
                                                        wx.ICON_QUESTION)
            if dlg.ShowModal()==wx.ID_OK:
               dlg.Destroy()

    def DateFormat(self,date):
        year = str(date[0])
        month = str(date[1])
        day = str(date[2])
        hour = str(date[3])
        if len(hour)==1:
            hour = '0'+hour
        minute = str(date[4])
        if len(minute)==1:
            minute = '0'+minute
        second = str(date[5])
        if len(second)==1:
            second = '0'+second
        return year+'-'+month+'-'+day+' '+hour+':'+minute+':'+second

class RegisterFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title=u'注  册', size=(340,220))
        panel = wx.Panel(self,-1)
        self.Centre()

        self.recvfromdata = ''

        self.usernamestaticText = wx.StaticText(panel,-1,u'用   户   名:',pos=(25,25))
        self.usernametextCtrl = wx.TextCtrl(panel,-1,'',pos=(105,22),size=(200,25))
        
        self.passwordstaticText = wx.StaticText(panel,-1,label=u'密         码:',pos=(25,63))
        self.passwordtextCtrl = wx.TextCtrl(panel,-1,'',pos=(105,60),size=(200,25),style=wx.TE_PASSWORD)

        self.surepasswordstaticText = wx.StaticText(panel,-1,label=u'确 认 密 码:',pos=(25,103))
        self.surepasswordtextCtrl = wx.TextCtrl(panel,-1,'',pos=(105,100),size=(200,25),style=wx.TE_PASSWORD)

        self.SureButton = wx.Button(panel,label=u'注 册',pos=(50,140),size=(100,25))
        self.Bind(wx.EVT_BUTTON, self.OnButtonSureButton, self.SureButton)
        
        self.CancelButton = wx.Button(panel,label=u'取 消',pos=(180,140),size=(100,25))
        self.Bind(wx.EVT_BUTTON, self.OnButtonCancel, self.CancelButton)

        self.SetSizeHints(340,220,340,220)
        self.Show()

        thread.start_new_thread(self.run,())

    def OnButtonSureButton(self, event):
        newusername = self.usernametextCtrl.GetValue()
        newuserpassword = self.passwordtextCtrl.GetValue()
        surepassword = self.surepasswordtextCtrl.GetValue()
        if newusername != '':
            if newuserpassword != '':
                if newuserpassword == surepassword:
                    tcpCliSock.send(('Register'+' '+newusername+' '+newuserpassword).encode('gbk'))
                else:
                    self.RegisterTipsDialog(tip=u' 密 码 不 一 致')
            else:
                self.RegisterTipsDialog(tip=u' 请 输 入 密 码')
        else:
            self.RegisterTipsDialog(tip=u' 请 输 入 账 户 名')

    def checkRegister(self):
        registerdata = self.recvfromdata.split(' ')
        if registerdata[2] == '0':
            self.RegisterTipsDialog(tip=u'注 册 成 功')
            return True
        if registerdata[2]=='1':
            self.RegisterTipsDialog(tip=u'用 户 已 存 在')
            return False

    def run(self):
        while 1:
            register = tcpCliSock.recv(100).decode('gbk')
            if register != '':
                self.recvfromdata = register
                if self.checkRegister():
                    break
        tcpCliSock.close()
        self.Destroy()

    def OnButtonCancel(self, event):
        dlg = wx.MessageDialog(self,u' 是 否 取 消？ ','Caution',wx.CANCEL|wx.OK|\
                                                       wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            self.Destroy()

    def RegisterTipsDialog(self, tip):
        registersuccessdlg = wx.MessageDialog(self,tip,'Caution',wx.CANCEL|wx.OK|\
                                                         wx.ICON_QUESTION)
        if registersuccessdlg.ShowModal() == wx.ID_OK:
            registersuccessdlg.Destroy()

if __name__ == '__main__':
    app = wx.App()
    frame = LoginFrame()
    frame.Show()
    app.MainLoop()
