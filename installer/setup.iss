[Setup]
AppName=!ndic8r Keyboard language indicator
AppVersion=0.9.04.001
AppPublisher=Serhiy Suprun
AppPublisherURL=https://github.com/suprun/indic8tr
AppSupportURL=https://github.com/suprun/indic8tr/wiki
AppUpdatesURL=https://github.com/suprun/indic8tr/wiki
DefaultDirName={pf}\!ndic8r Keyboard Indicator
DisableDirPage=no
DefaultGroupName=!ndic8r Keyboard Layout Indicator
UninstallDisplayIcon={app}\images\icons\favicon-uninstall.ico
OutputBaseFilename=!ndic8r-Keyboard-Installer
OutputDir=.
Compression=lzma
SolidCompression=yes
RestartIfNeededByRun=yes
; Заборонити встановлення, якщо програма вже встановлена
Uninstallable=yes
AllowCancelDuringInstall=yes
; Windows 7
MinVersion=6.1
; Визначення мови інсталятора за мовою системи
LanguageDetectionMethod=locale
; Файл ліцензії
LicenseFile=..\LICENSE
; Відображення діалогу вибору мови
ShowLanguageDialog=true
; Файли банерів для майстра встановлення
WizardImageFile="images\banner.png"       
; великий банер у майстрі 164 × 314 px
WizardSmallImageFile=images\small.png  
; маленький банер у майстрі 256 × 256 px
SetupIconFile=..\images\icons\favicon.ico

[Files]
; Беремо усю зібрану Nuitka папку
Source: "..\build\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Додаємо файл ліцензії
Source: "..\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion
; Додаємо іконку для деінсталяції
Source: "..\images\icons\favicon-uninstall.ico"; DestDir: "{app}"; Flags: ignoreversion
;Source: "{src}\{#SetupSetting("OutputBaseFilename")}.exe"; DestDir: "{app}"; Flags: external; DestName: "InstallerBackup.exe"

[Dirs]
; Видалити папку {app} повністю, навіть якщо вона порожня
Name: "{app}"; Flags: uninsalwaysuninstall 
Name: "{app}\PIL"; Flags: uninsalwaysuninstall 


[Icons]
; Ярлик у меню Пуск
Name: "{group}\Keyboard Indicator"; Filename: "{app}\KeyboardIndicator.exe"
; Ярлик для деінсталяції
Name: "{group}\Uninstall !ndic8r Keyboard Layout Indicator"; Filename: "{uninstallexe}"; IconFilename: "{app}\images\icons\favicon-uninstall.ico"
; Ярлик у автозавантаження (Startup у %APPDATA%)
Name: "{userstartup}\KeyboardIndicator"; Filename: "{app}\KeyboardIndicator.exe"
;Name: "{group}\Reinstall"; Filename: "{app}\InstallerBackup.exe"; IconFilename: "{app}\images\icons\favicon-reinstall.ico"; Comment: "Запустити для перевстановлення або відновлення програми"


[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "uk"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "it"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "jp"; MessagesFile: "compiler:Languages\Japanese.isl"

[CustomMessages]
; --- Англійська
en.licenseview=Open license file
; --- Українська
uk.licenseview=Відкрити файл ліцензії
; --- Німецька
de.licenseview=Lizenzdatei öffnen
; --- Французька
fr.licenseview=Ouvrir le fichier de licence
; --- Іспанська
es.licenseview=Abrir el archivo de licencia
; --- Португальська
it.licenseview=Abrir o arquivo de licença
; --- Японська
jp.licenseview=ライセンスファイルを開く

[Run]
Filename: "{app}\KeyboardIndicator.exe"; Flags: nowait postinstall skipifsilent; Description: "{cm:LaunchProgram,Keyboard Indicator}"
; Відкрити у Блокноті саме LICENSE.txt
Filename: "notepad.exe"; Parameters: """{app}\LICENSE.txt"""; Description: "{cm:licenseview}"; Flags: postinstall skipifsilent unchecked

[UninstallDelete]
Type: files; Name: "{userappdata}\Indic8tr\*"
;Type: dirifempty; Name: "{userappdata}\Indic8tr"