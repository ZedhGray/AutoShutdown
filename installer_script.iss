; Script de instalación para Auto Shutdown
; Requiere Inno Setup 6 o superior

#define MyAppName "Auto Shutdown"
#define MyAppVersion "1.0"
#define MyAppPublisher "AutoShutdown"
#define MyAppURL "https://github.com/tuusuario/autoshutdown"
#define MyAppExeName "AutoShutdown.exe"

[Setup]
; Información básica
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName=C:\AutoShutdown
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=installer_output
OutputBaseFilename=AutoShutdown_Setup
; SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Configuración de firma digital (opcional pero MUY RECOMENDADO)
; SignTool=signtool
; SignedUninstaller=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\AutoShutdown.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Ejecutar la app al final de la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Código para manejar la instalación
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Crear directorio de configuración si no existe
    // Aquí puedes agregar código adicional si es necesario
  end;
end;

// Verificar si hay una instancia ejecutándose
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  // Intentar cerrar la app si está corriendo
  Exec('taskkill', '/F /IM AutoShutdown.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := '';
end;
