@echo off
set curpath=%~dp0

cd ..
set KBE_ROOT=%cd%
set KBE_RES_PATH=%KBE_ROOT%/kbe/res/;%curpath%/;%curpath%/scripts/;%curpath%/res/
set KBE_BIN_PATH=%KBE_ROOT%/kbe/bin/server/

if defined uid (echo UID = %uid%)

cd %curpath%
call "kill_server.bat"
rmdir /s/q logs

echo KBE_ROOT = %KBE_ROOT%
echo KBE_RES_PATH = %KBE_RES_PATH%
echo KBE_BIN_PATH = %KBE_BIN_PATH%


start "" "%KBE_BIN_PATH%/machine.exe" --cid=1000 --gus=1000 --hide=1
start "" "%KBE_BIN_PATH%/logger.exe" --cid=2000 --gus=2000 --hide=1
start "" "%KBE_BIN_PATH%/interfaces.exe" --cid=3000 --gus=3000 --hide=1
start "" "%KBE_BIN_PATH%/dbmgr.exe" --cid=4000 --gus=4000 --hide=1
start "" "%KBE_BIN_PATH%/baseappmgr.exe" --cid=5000 --gus=5000 --hide=1
start "" "%KBE_BIN_PATH%/cellappmgr.exe" --cid=6000 --gus=6000 --hide=1
start "" "%KBE_BIN_PATH%/baseapp.exe" --cid=7000 --gus=7000 --hide=1
start "" "%KBE_BIN_PATH%/baseapp.exe" --cid=7001 --gus=7001 --hide=1
start "" "%KBE_BIN_PATH%/cellapp.exe" --cid=8000 --gus=8000 --hide=1
start "" "%KBE_BIN_PATH%/cellapp.exe" --cid=8001 --gus=8001 --hide=1
start "" "%KBE_BIN_PATH%/loginapp.exe" --cid=9000 --gus=9000 --hide=1
