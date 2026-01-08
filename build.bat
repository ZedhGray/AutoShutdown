@echo off
echo ================================================
echo    Auto Shutdown - Script de Build
echo ================================================
echo.

REM Cambiar al directorio donde está el script
cd /d "%~dp0"
echo Directorio de trabajo: %cd%
echo.

REM Verificar que PyInstaller esté instalado
echo [1/5] Verificando PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no encontrado. Instalando...
    python -m pip install pyinstaller
)
echo OK - PyInstaller listo
echo.

REM Limpiar builds anteriores
echo [2/5] Limpiando builds anteriores...

REM Cerrar la aplicación si está corriendo
echo Cerrando AutoShutdown si esta en ejecucion...
taskkill /F /IM AutoShutdown.exe >nul 2>&1
if errorlevel 1 (
    echo - AutoShutdown no estaba corriendo
) else (
    echo - AutoShutdown cerrado
    timeout /t 2 >nul
)

REM Limpiar carpetas
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist installer_output rmdir /s /q installer_output
echo OK - Limpieza completada
echo.

REM Crear el ejecutable con PyInstaller
echo [3/5] Compilando ejecutable con PyInstaller...
echo Esto puede tomar varios minutos...
echo.

REM Verificar que el archivo fuente exista
if not exist "auto_shutdown_gui_v2.pyw" (
    echo ERROR: No se encuentra auto_shutdown_gui_v2.pyw
    echo Asegurate de que todos los archivos esten en la misma carpeta
    echo y ejecuta este script desde esa carpeta.
    pause
    exit /b 1
)

REM Verificar que el .spec exista
if not exist "auto_shutdown.spec" (
    echo ERROR: No se encuentra auto_shutdown.spec
    pause
    exit /b 1
)

REM Verificar/crear icono (opcional)
if not exist "icon.ico" (
    echo.
    echo NOTA: No se encontro icon.ico
    echo El ejecutable se creara sin icono personalizado (usara el de Python por defecto)
    echo.
    echo Si quieres un icono personalizado:
    echo   1. Instala Pillow: pip install pillow
    echo   2. Ejecuta: python create_icon.py
    echo   3. Vuelve a compilar
    echo.
    timeout /t 3 >nul
)

echo Compilando desde: %cd%
python -m PyInstaller auto_shutdown.spec
if errorlevel 1 (
    echo ERROR: Fallo al compilar el ejecutable
    pause
    exit /b 1
)
echo OK - Ejecutable creado en dist\AutoShutdown.exe
echo.

REM Agregar a excepciones de Windows Defender (requiere permisos admin)
echo [4/5] Configurando Windows Defender...
echo.
echo NOTA: Esta parte es OPCIONAL y requiere permisos de administrador
echo Si no corriste como admin, esto fallara (es normal)
echo.
powershell -Command "Add-MpPreference -ExclusionPath '%cd%\dist\AutoShutdown.exe'" 2>nul
if errorlevel 1 (
    echo OMITIDO: No se agrego a excepciones de Defender
    echo         (No es critico, puedes hacerlo manualmente despues)
) else (
    echo OK - Agregado a excepciones de Windows Defender
)
echo.

REM Crear el instalador (requiere Inno Setup instalado)
echo [5/5] Creando instalador con Inno Setup...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
    if errorlevel 1 (
        echo ERROR: Fallo al crear el instalador
        pause
        exit /b 1
    )
    echo OK - Instalador creado en installer_output\AutoShutdown_Setup.exe
) else (
    echo ADVERTENCIA: Inno Setup no encontrado
    echo Descárgalo de: https://jrsoftware.org/isdl.php
    echo Instalador NO creado, pero el ejecutable está listo en dist\
)
echo.

echo ================================================
echo    BUILD COMPLETADO
echo ================================================
echo.
echo Archivos generados:
echo - Ejecutable: dist\AutoShutdown.exe
if exist installer_output\AutoShutdown_Setup.exe (
    echo - Instalador: installer_output\AutoShutdown_Setup.exe
)
echo.
echo ============================================
echo IMPORTANTE: Como evitar alertas de Windows
echo ============================================
echo.
echo 1. NO ejecutes este script como Administrador
echo    (PyInstaller no lo necesita y puede causar problemas)
echo.
echo 2. Para agregar a excepciones de Defender:
echo    - Ejecuta "add_defender_exceptions.bat" como Admin
echo    - O hazlo manualmente en Configuracion de Windows
echo.
echo 3. Para distribuir sin alertas (opcional):
echo    - Considera firmar digitalmente el ejecutable
echo    - Costo: $50-300/año
echo.
pause
