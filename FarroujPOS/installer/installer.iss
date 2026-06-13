; Inno Setup Installer Script for Farrouj POS
; Requires building the .exe first with build.py

[Setup]
AppName=Farrouj POS
AppVersion=1.0.0
DefaultDirName={autopf}\FarroujPOS
DefaultGroupName=Farrouj POS
OutputDir=.
OutputBaseFilename=FarroujPOS_Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\FarroujPOS.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Farrouj POS"; Filename: "{app}\FarroujPOS.exe"
Name: "{commondesktop}\Farrouj POS"; Filename: "{app}\FarroujPOS.exe"
