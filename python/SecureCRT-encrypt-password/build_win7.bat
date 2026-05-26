@echo off
setlocal EnableExtensions
cd /d %~dp0

set "PYTHON_EXE=python"
set "REQ_FILE=%~dp0requirements_win7.txt"
set "SCRIPT_FILE=%~dp0securecrt_encrypt_password.py"

echo ========================================
echo SecureCRT Password Extractor
echo Win7/Win8/Win10/Win11 Package Builder
echo ----------------------------------------
echo Recommended Python: 3.8.x 64-bit
echo Win7 preferred: Python 3.8.10
echo Working dir: %~dp0
echo ========================================
echo.

REM Step 0: Check Python exists
where %PYTHON_EXE% >nul 2>nul
if errorlevel 1 goto no_python

REM Step 0b: Check Python version (3.8.x ~ 3.10.x)
%PYTHON_EXE% -c "import sys; sys.exit(0 if (3, 8) <= sys.version_info < (3, 11) else 1)"
if errorlevel 1 goto bad_python

echo [1/6] Python version:
%PYTHON_EXE% -c "import sys; print(sys.version)"
if errorlevel 1 goto fail
echo.

echo [2/6] Upgrade pip/setuptools/wheel...
%PYTHON_EXE% -m pip install --upgrade pip==24.0 setuptools==69.5.1 wheel==0.43.0
if errorlevel 1 goto fail

echo.
echo [3/6] Install project requirements...
%PYTHON_EXE% -m pip install -r "%REQ_FILE%"
if errorlevel 1 goto fail
echo.

echo [4/6] Verify pycryptodome internal API...
%PYTHON_EXE% -c "from Crypto.Protocol.KDF import _bcrypt_hash; print('  _bcrypt_hash OK')"
if errorlevel 1 goto fail
echo.

echo [5/6] Clean old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo   Clean done.
echo.

echo [6/6] Run PyInstaller...
REM --console (not --windowed): this tool needs stdin for passphrase input
REM --onefile: single exe for easy distribution
REM --add-data: bundle the cipher module alongside if needed
REM --hidden-import: ensure pycryptodome internals are included
%PYTHON_EXE% -m PyInstaller --clean -F --console "%SCRIPT_FILE%" ^
    --name=SecureCRT_Encrypt_Password ^
    --hidden-import=securecrt_cipher ^
    --hidden-import=Crypto ^
    --hidden-import=Crypto.Cipher ^
    --hidden-import=Crypto.Cipher.AES ^
    --hidden-import=Crypto.Cipher.Blowfish ^
    --hidden-import=Crypto.Cipher._mode_cbc ^
    --hidden-import=Crypto.Hash ^
    --hidden-import=Crypto.Hash.SHA256 ^
    --hidden-import=Crypto.Hash.SHA512 ^
    --hidden-import=Crypto.Protocol ^
    --hidden-import=Crypto.Protocol.KDF ^
    --hidden-import=Crypto.Protocol.KDF._bcrypt_hash ^
    --hidden-import=Crypto.Util ^
    --hidden-import=Crypto.Util._raw_api ^
    --hidden-import=Crypto.Util.py3compat ^
    --hidden-import=Crypto.Util.number ^
    --hidden-import=Crypto.Math ^
    --hidden-import=Crypto.Math.Numbers ^
    --hidden-import=encodings ^
    --hidden-import=encodings.utf_16 ^
    --hidden-import=encodings.utf_8 ^
    --hidden-import=encodings.idna ^
    --hidden-import=encodings.mbcs ^
    --hidden-import=ctypes ^
    --hidden-import=ctypes.wintypes ^
    --hidden-import=getpass ^
    --hidden-import=csv ^
    --hidden-import=re ^
    --hidden-import=argparse ^
    --hidden-import=struct
if errorlevel 1 goto fail

echo.
echo ========================================
echo Build finished successfully!
echo Output: dist\SecureCRT_Encrypt_Password.exe
echo ----------------------------------------
echo Usage:
echo   1. Copy exe to the same directory as Sessions/
echo   2. Double-click exe to run (will prompt for passphrase)
echo   3. Or run from CMD with SecureCRT_Encrypt_Password.exe --help
echo.
echo Before release:
echo   - Test on a Win7 SP1 machine with KB2533623 + KB2999226
echo   - Test on Win10/Win11
echo   - Ensure Sessions/ folder is next to the exe
echo ========================================
echo.
pause
exit /b 0

:no_python
echo.
echo [ERROR] Python was not found in PATH.
echo Please install Python 3.8.x 64-bit and add it to PATH.
echo Download: https://www.python.org/downloads/release/python-3810/
echo.
pause
exit /b 1

:bad_python
echo.
echo [ERROR] Unsupported Python version.
echo Please use Python 3.8.x to 3.10.x. Win7 should prefer 3.8.10.
%PYTHON_EXE% -c "import sys; print('Current version:', sys.version)"
echo.
pause
exit /b 1

:fail
echo.
echo [ERROR] Build failed.
echo Possible causes:
echo   - Network issue (cannot download dependencies)
echo   - Missing Win7 patches (KB2533623, KB2999226)
echo   - Python version mismatch
echo   - pycryptodome C extension compilation failure
echo.
echo Try running the commands one by one in cmd.exe to find the exact error.
echo.
pause
exit /b 1
