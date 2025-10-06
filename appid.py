import win32com.client

link_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\!ndic8r Keyboard Layout Indicator\Keyboard Indicator.lnk"

shell = win32com.client.Dispatch("Shell.Application")
folder = shell.Namespace(link_path.rsplit("\\", 1)[0])
item = folder.ParseName(link_path.rsplit("\\", 1)[1])
app_id = item.ExtendedProperty("System.AppUserModel.ID")

print("AppUserModelID:", app_id)
