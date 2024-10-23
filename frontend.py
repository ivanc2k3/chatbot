import wx
import wx.richtext as rt
from db import check_user, insert_user, get_user_id, get_conversation, update_conversation
from reply import reply_with_text

class ChatFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(ChatFrame, self).__init__(*args, **kw)

        self.user_id = None
        
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)  # 用於切換面板
        self.login_panel = LoginPanel(self)
        self.register_panel = RegisterPanel(self)
        self.chat_panel = ChatPanel(self)
        
        self.panel_sizer.Add(self.login_panel, 1, wx.EXPAND)
        self.panel_sizer.Add(self.register_panel, 1, wx.EXPAND)
        self.panel_sizer.Add(self.chat_panel, 1, wx.EXPAND)
        
        self.register_panel.Hide()  # 默認顯示登入介面
        self.chat_panel.Hide()

        self.SetSizer(self.panel_sizer)
        self.Layout()

    def show_panel(self, panel_name):
        """切換顯示的面板"""
        self.login_panel.Hide()
        self.register_panel.Hide()
        self.chat_panel.Hide()

        if panel_name == 'login':
            self.login_panel.Show()
        elif panel_name == 'register':
            self.register_panel.Show()
        elif panel_name == 'chat':
            self.chat_panel.Show()
        
        self.Layout()

class LoginPanel(wx.Panel):
    def __init__(self, parent):
        super(LoginPanel, self).__init__(parent)
        self.parent = parent
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 標籤和輸入框
        self.username_label = wx.StaticText(self, label="Username:")
        self.username_input = wx.TextCtrl(self)
        self.password_label = wx.StaticText(self, label="Password:")
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        
        # 按鈕
        login_button = wx.Button(self, label="Login")
        register_button = wx.Button(self, label="Register")
        
        # 錯誤顯示
        self.error_label = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        
        # 佈局
        vbox.Add(self.username_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.username_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(login_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(register_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.error_label, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.SetSizer(vbox)
        
        # 綁定按鈕事件
        login_button.Bind(wx.EVT_BUTTON, self.on_login)
        register_button.Bind(wx.EVT_BUTTON, self.on_register)

    def on_login(self, event):
        username = self.username_input.GetValue()
        password = self.password_input.GetValue()
        
        result = check_user(username, password)
        if result == "Login successful":
            self.parent.user_id = get_user_id(username)
            self.parent.show_panel('chat')
            self.parent.chat_panel.first_display()
        else:
            self.error_label.SetLabel(result)

    def on_register(self, event):
        self.parent.show_panel('register')

class RegisterPanel(wx.Panel):
    def __init__(self, parent):
        super(RegisterPanel, self).__init__(parent)
        self.parent = parent
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 標籤和輸入框
        self.username_label = wx.StaticText(self, label="New Username:")
        self.username_input = wx.TextCtrl(self)
        self.password_label = wx.StaticText(self, label="New Password:")
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        
        # 按鈕
        create_account_button = wx.Button(self, label="Create Account")
        back_to_login_button = wx.Button(self, label="Back to Login")
        
        # 錯誤或成功顯示
        self.result_label = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        
        # 佈局
        vbox.Add(self.username_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.username_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(create_account_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(back_to_login_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.result_label, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.SetSizer(vbox)
        
        # 綁定按鈕事件
        create_account_button.Bind(wx.EVT_BUTTON, self.on_create_account)
        back_to_login_button.Bind(wx.EVT_BUTTON, self.on_back_to_login)

    def on_create_account(self, event):
        username = self.username_input.GetValue()
        password = self.password_input.GetValue()
        
        result = insert_user(username, password)
        self.result_label.SetLabel(result)
        
        if result == "User created successfully":
            # 注册成功，自动跳转到登录界面或者聊天界面
            self.parent.show_panel('login')  # 或者 'chat'
        elif result == "Username already exists":
            # 用户名已存在，清空输入框并聚焦
            self.username_input.SetValue("")
            self.username_input.SetFocus()
        
    def on_back_to_login(self, event):
        self.parent.show_panel('login')

class ChatPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(ChatPanel, self).__init__(*args, **kw)
        
        # 創建顯示對話的多行富文本框，設置為只讀，支持插入圖片
        self.chat_display = rt.RichTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size=(400, 300))
        
        # 創建輸入框，增加 wx.TE_PROCESS_ENTER 樣式以捕捉 Enter 鍵
        self.input_box = wx.TextCtrl(self, size=(300, 30), style=wx.TE_PROCESS_ENTER)
        
        # 創建發送按鈕
        send_button = wx.Button(self, label="Send")
        
        # 創建上傳圖片按鈕
        upload_button = wx.Button(self, label="Upload Image")
        
        # 初始化變量來保存上傳的圖片
        self.uploaded_image = None
        
        # 設置水平佈局
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.input_box, proportion=1, flag=wx.EXPAND)
        hbox.Add(send_button, proportion=0)
        hbox.Add(upload_button, proportion=0)
        
        # 設置垂直佈局
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.chat_display, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(hbox, flag=wx.EXPAND | wx.ALL, border=10)
        
        # 將面板應用佈局
        self.SetSizer(vbox)
        
        # 綁定事件
        send_button.Bind(wx.EVT_BUTTON, self.on_send)
        upload_button.Bind(wx.EVT_BUTTON, self.on_upload_image)  # 綁定上傳圖片按鈕事件
        self.input_box.Bind(wx.EVT_TEXT_ENTER, self.on_send)  # 捕捉 Enter 鍵事件

    def first_display(self):
        convertWord = {"assistant": "myRobot", "user":"user"}
        if self.GetParent().user_id:  # 確認已登入的用戶 ID
            conversation = get_conversation(self.GetParent().user_id)
            if conversation:
                for msg in conversation:  # 遍歷所有 messages，顯示在聊天框中
                    self.chat_display.BeginBold()
                    self.chat_display.WriteText(f"{convertWord[msg['role']]}: ")
                    self.chat_display.EndBold()
                    for content_item in msg['content']:
                        if "text" in content_item:
                            self.chat_display.WriteText(f"{content_item['text']}\n")
            else:
                self.chat_display.BeginBold()
                self.chat_display.WriteText("myRobot: ")
                self.chat_display.EndBold()
                self.chat_display.WriteText("Hello! How can I help you today?\n")

    def on_send(self, event):
        message = self.input_box.GetValue()
        if message.strip():
            # 顯示用戶輸入的文字
            self.chat_display.BeginBold()
            self.chat_display.WriteText("User: ")
            self.chat_display.EndBold()
            self.chat_display.WriteText(f"{message}\n")
            self.input_box.SetValue("")  # 清空輸入框

            # 產生並顯示 Bot 的回應
            user_id = self.GetParent().user_id
            if user_id:
                conversation = get_conversation(user_id) or []  # 獲取對話記錄

                # 使用 reply_with_text 來處理對話
                updated_messages, response = reply_with_text(message, conversation)

                # 顯示 Bot 的回應
                self.chat_display.BeginBold()
                self.chat_display.WriteText("myRobot: ")
                self.chat_display.EndBold()
                self.chat_display.WriteText(f"{response}\n")

                # 更新對話紀錄至資料庫
                update_conversation(user_id, updated_messages)

    def on_upload_image(self, event):
        # 打開文件對話框以選擇圖片文件
        with wx.FileDialog(self, "Choose an image", wildcard="Image files (*.png;*.jpg;*.jpeg)|*.png;*.jpg;*.jpeg",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # 用戶取消選擇
            
            # 獲取圖片路徑
            image_path = fileDialog.GetPath()
            
            # 加載圖片並縮放到指定大小 (例如 100x100 像素)
            image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
            scaled_image = image.Scale(100, 100)  # 設置縮放的大小
            bmp = scaled_image.ConvertToBitmap()

            # 在聊天框中插入縮放後的圖片
            self.chat_display.BeginBold()
            self.chat_display.WriteText("User uploaded an image:\n")
            self.chat_display.EndBold()
            self.chat_display.WriteImage(bmp)
            self.chat_display.WriteText("\n")  # 插入換行符

            # 顯示提示信息
            self.chat_display.BeginBold()
            self.chat_display.WriteText("myRobot: Please enter text to describe or process the image.\n")
            self.chat_display.EndBold()

class MyApp(wx.App):
    def OnInit(self):
        frame = ChatFrame(None, title="Chat Example", size=(450, 500))
        frame.Show()
        return True

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
