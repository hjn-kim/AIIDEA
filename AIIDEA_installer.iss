; AIIDEA Inno Setup Script
; Requires Inno Setup 6+ : https://jrsoftware.org/isinfo.php

[Setup]
AppName=AIIDEA
AppVersion=1.0
; AppId는 앱을 고유하게 식별하는 GUID — 절대 변경하지 마세요 (변경 시 기존 버전 감지 불가)
AppId={{7A3F1D2E-8B4C-4D6E-9F2A-1C5E7B3D4F6A}
AppPublisher=AIIDEA
DefaultDirName={localappdata}\Programs\AIIDEA
DefaultGroupName=AIIDEA
OutputDir=installer
OutputBaseFilename=AIIDEA_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\icon.ico
; 관리자 권한 없어도 설치 가능 (사용자 폴더에 설치됨 → .env 파일 쓰기 가능)
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\AIIDEA.exe
UninstallDisplayName=AIIDEA
; 실행 중인 앱 자동 종료
CloseApplications=yes
CloseApplicationsFilter=AIIDEA.exe
RestartApplications=no

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 만들기"; GroupDescription: "추가 옵션:"

[Files]
; 메인 실행 파일
Source: "dist\AIIDEA\AIIDEA.exe"; DestDir: "{app}"; Flags: ignoreversion
; 라이브러리 (필수)
Source: "dist\AIIDEA\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; .env — API 키가 없을 때만 기본 파일 배치 (기존 키 보호는 [Code]에서 처리)
Source: "dist\AIIDEA\.env"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 시작 메뉴
Name: "{group}\AIIDEA"; Filename: "{app}\AIIDEA.exe"; IconFilename: "{app}\AIIDEA.exe"
Name: "{group}\AIIDEA 제거"; Filename: "{uninstallexe}"
; 바탕화면 바로가기 (선택)
Name: "{autodesktop}\AIIDEA"; Filename: "{app}\AIIDEA.exe"; IconFilename: "{app}\AIIDEA.exe"; Tasks: desktopicon

[Run]
; 설치 완료 후 실행 옵션
Filename: "{app}\AIIDEA.exe"; Description: "AIIDEA 바로 실행"; Flags: nowait postinstall skipifsilent

[Code]
var
  EnvContent: AnsiString;
  EnvWasBacked: Boolean;

{ 기존 설치의 언인스톨러 경로를 레지스트리에서 조회 }
function GetUninstallString(): String;
var
  sKey: String;
  sValue: String;
begin
  sKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{7A3F1D2E-8B4C-4D6E-9F2A-1C5E7B3D4F6A}_is1';
  sValue := '';
  if not RegQueryStringValue(HKLM, sKey, 'UninstallString', sValue) then
    RegQueryStringValue(HKCU, sKey, 'UninstallString', sValue);
  Result := sValue;
end;

{ 기존 설치 경로 조회 }
function GetOldInstallPath(): String;
var
  sKey: String;
  sValue: String;
begin
  sKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{7A3F1D2E-8B4C-4D6E-9F2A-1C5E7B3D4F6A}_is1';
  sValue := '';
  if not RegQueryStringValue(HKLM, sKey, 'InstallLocation', sValue) then
    RegQueryStringValue(HKCU, sKey, 'InstallLocation', sValue);
  Result := sValue;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  sUninstall: String;
  sOldPath: String;
  sEnvPath: String;
  iCode: Integer;
begin
  { 설치 직전: 기존 버전 자동 제거 }
  if CurStep = ssInstall then
  begin
    sUninstall := GetUninstallString();
    if sUninstall <> '' then
    begin
      { 기존 .env 백업 (API 키 보존) }
      sOldPath := GetOldInstallPath();
      if sOldPath <> '' then
      begin
        sEnvPath := AddBackslash(sOldPath) + '.env';
        EnvWasBacked := LoadStringFromFile(sEnvPath, EnvContent);
      end;

      { 기존 버전 자동 제거 (사용자 확인 없이) }
      Exec(RemoveQuotes(sUninstall),
           '/SILENT /NORESTART /SUPPRESSMSGBOXES',
           '', SW_HIDE, ewWaitUntilTerminated, iCode);
    end;
  end;

  { 설치 완료 후: 백업한 .env 복원 }
  if CurStep = ssPostInstall then
  begin
    if EnvWasBacked and (EnvContent <> '') then
      SaveStringToFile(ExpandConstant('{app}\.env'), EnvContent, False);
  end;
end;
