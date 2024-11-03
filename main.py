import wx
import wx.richtext as rt
import base64
from io import BytesIO
from db import check_user, insert_user, get_user_id, get_conversation, update_conversation, delete_conversation
from reply import reply_with_text, reply_with_image

class ChatFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(ChatFrame, self).__init__(*args, **kw)

        self.user_id = None
        
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)  
        self.login_panel = LoginPanel(self)
        self.register_panel = RegisterPanel(self)
        self.chat_panel = ChatPanel(self)
        
        self.panel_sizer.Add(self.login_panel, 1, wx.EXPAND)
        self.panel_sizer.Add(self.register_panel, 1, wx.EXPAND)
        self.panel_sizer.Add(self.chat_panel, 1, wx.EXPAND)
        
        self.register_panel.Hide()  
        self.chat_panel.Hide()

        self.SetSizer(self.panel_sizer)
        self.Layout()

    def show_panel(self, panel_name):
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
        
        self.username_label = wx.StaticText(self, label="Username:")
        self.username_input = wx.TextCtrl(self)
        self.password_label = wx.StaticText(self, label="Password:")
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        
        login_button = wx.Button(self, label="Login")
        register_button = wx.Button(self, label="Register")
        
        self.error_label = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        
        vbox.Add(self.username_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.username_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(login_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(register_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.error_label, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.SetSizer(vbox)
        
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
        
        self.username_label = wx.StaticText(self, label="New Username:")
        self.username_input = wx.TextCtrl(self)
        self.password_label = wx.StaticText(self, label="New Password:")
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        
        create_account_button = wx.Button(self, label="Create Account")
        back_to_login_button = wx.Button(self, label="Back to Login")
        
        self.result_label = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        
        vbox.Add(self.username_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.username_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_label, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.password_input, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(create_account_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(back_to_login_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.result_label, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.SetSizer(vbox)
        
        create_account_button.Bind(wx.EVT_BUTTON, self.on_create_account)
        back_to_login_button.Bind(wx.EVT_BUTTON, self.on_back_to_login)

    def on_create_account(self, event):
        username = self.username_input.GetValue()
        password = self.password_input.GetValue()
        
        result = insert_user(username, password)
        self.result_label.SetLabel(result)
        
        if result == "User created successfully":
            self.parent.show_panel('login')  
        elif result == "Username already exists":
            self.username_input.SetValue("")
            self.password_input.SetValue("")
            self.username_input.SetFocus()
        
    def on_back_to_login(self, event):
        self.parent.show_panel('login')

class ChatPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(ChatPanel, self).__init__(*args, **kw)
        
        self.chat_display = rt.RichTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size=(400, 300))
        
        self.input_box = wx.TextCtrl(self, size=(300, 30), style=wx.TE_PROCESS_ENTER)
        
        send_button = wx.Button(self, label="Send")
        
        upload_button = wx.Button(self, label="Upload Image")
        
        self.uploaded_image = None

        delete_button = wx.Button(self, label="Delete Conversation")

        delete_button.Bind(wx.EVT_BUTTON, self.on_delete_conversation)

        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.input_box, proportion=1, flag=wx.EXPAND)
        hbox.Add(send_button, proportion=0)
        hbox.Add(upload_button, proportion=0)
        hbox.Add(delete_button, proportion=0)  
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.chat_display, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(hbox, flag=wx.EXPAND | wx.ALL, border=10)
        
        self.SetSizer(vbox)
        
        send_button.Bind(wx.EVT_BUTTON, self.on_send)
        upload_button.Bind(wx.EVT_BUTTON, self.on_upload_image)  
        self.input_box.Bind(wx.EVT_TEXT_ENTER, self.on_send)  

    def first_display(self):
        convertWord = {"assistant": "myRobot", "user": "user"}
        if self.GetParent().user_id:  
            conversation = get_conversation(self.GetParent().user_id)
            if conversation:
                for msg in conversation:  
                    self.chat_display.BeginBold()
                    self.chat_display.WriteText(f"{convertWord[msg['role']]}: ")
                    self.chat_display.EndBold()
                    
                    for content_item in msg['content']:
                        if content_item.get("type") == "text":
                            text_content = content_item['text']
                            
                            self.chat_display.WriteText(f"{text_content}\n")

                        elif content_item.get("type") == "image_url" and "url" in content_item['image_url']:
                            image_data_url = content_item['image_url']['url']

                            if image_data_url.startswith("data:image/"):
                                try:
                                    base64_data = image_data_url.split(",")[1]
                                    image_data = base64.b64decode(base64_data)
                                    image_stream = BytesIO(image_data)
                                    image = wx.Image(image_stream)
                                    scaled_image = image.Scale(100, 100)  
                                    bmp = scaled_image.ConvertToBitmap()

                                    self.chat_display.WriteImage(bmp)
                                    self.chat_display.WriteText("\n")  
                                except Exception as e:
                                    self.chat_display.WriteText(f"[Error displaying image: {str(e)}]\n")

            else:
                self.chat_display.BeginBold()
                self.chat_display.WriteText("myRobot: ")
                self.chat_display.EndBold()
                self.chat_display.WriteText("Hello! How can I help you today?\n")

    def on_send(self, event):
        message = self.input_box.GetValue()
        if message.strip():
            self.chat_display.BeginBold()
            self.chat_display.WriteText("User: ")
            self.chat_display.EndBold()
            self.chat_display.WriteText(f"{message}\n")
            self.input_box.SetValue("") 

            user_id = self.GetParent().user_id
            if user_id:
                conversation = get_conversation(user_id) or []  

                updated_messages, response = reply_with_text(message, conversation)

                self.chat_display.BeginBold()
                self.chat_display.WriteText("myRobot: ")
                self.chat_display.EndBold()
                self.chat_display.WriteText(f"{response}\n")

                update_conversation(user_id, updated_messages)

    def on_upload_image(self, event):
        with wx.FileDialog(self, "Choose an image", wildcard="Image files (*.png;*.jpg;*.jpeg)|*.png;*.jpg;*.jpeg",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            image_path = fileDialog.GetPath()
            
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

            self.chat_display.BeginBold()
            self.chat_display.WriteText("User uploaded an image:\n")
            self.chat_display.EndBold()

            image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
            scaled_image = image.Scale(100, 100)
            bmp = scaled_image.ConvertToBitmap()
            self.chat_display.WriteImage(bmp)
            self.chat_display.WriteText("\n")
            
            self.chat_display.BeginBold()
            self.chat_display.WriteText("myRobot: Please enter text to describe or process the image.\n")
            self.chat_display.EndBold()

            user_id = self.GetParent().user_id
            if user_id:
                conversation = get_conversation(user_id) or []

                def on_user_enter_description(event):
                    description = self.input_box.GetValue()
                    if description.strip():
                        self.chat_display.BeginBold()
                        self.chat_display.WriteText("User: ")
                        self.chat_display.EndBold()
                        self.chat_display.WriteText(f"{description}\n")
                        self.input_box.SetValue("")

                        updated_messages, response = reply_with_image(description, encoded_image, conversation)

                        self.chat_display.BeginBold()
                        self.chat_display.WriteText("myRobot: ")
                        self.chat_display.EndBold()
                        self.chat_display.WriteText(f"{response}\n")

                        update_conversation(user_id, updated_messages)

                        self.input_box.Bind(wx.EVT_TEXT_ENTER, self.on_send)

                self.input_box.Bind(wx.EVT_TEXT_ENTER, on_user_enter_description)

    def on_delete_conversation(self, event):
        user_id = self.GetParent().user_id
        if user_id:
            delete_conversation(user_id)
            
            self.chat_display.Clear()
            
            self.chat_display.BeginBold()
            self.chat_display.WriteText("myRobot: ")
            self.chat_display.EndBold()
            self.chat_display.WriteText("Conversation deleted. How can I help you further?\n")



class MyApp(wx.App):
    def OnInit(self):
        frame = ChatFrame(None, title="ChatBot", size=(450, 500))
        frame.Show()
        return True
    
def main():
    app = MyApp()
    app.MainLoop()

if __name__ == '__main__':
    main()
