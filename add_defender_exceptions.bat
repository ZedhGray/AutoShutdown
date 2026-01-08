@echo off
echo ================================================
echo    Agregar Excepciones a Windows Defender
echo ================================================
echo.
echo IMPORTANTE: Este script debe ejecutarse como ADMINISTRADOR
echo.
pause

echo Agregando excepciones para desarrollo...
echo.

REM Agregar la carpeta del proyecto
powershell -Command "Add-MpPreference -ExclusionPath '%cd%'"
if errorlevel 1 (
    echo ERROR: No se pudo agregar la carpeta del proyecto
    echo Asegurate de ejecutar como Administrador
    pause
    exit /b 1
)
echo OK - Carpeta del proyecto agregada

REM Agregar carpeta dist
powershell -Command "Add-MpPreference -ExclusionPath '%cd%\dist'"
if errorlevel 1 (
    echo ADVERTENCIA: No se pudo agregar carpeta dist
) else (
    echo OK - Carpeta dist agregada
)

REM Agregar el ejecutable específico (si existe)
if exist "dist\AutoShutdown.exe" (
    powershell -Command "Add-MpPreference -ExclusionPath '%cd%\dist\AutoShutdown.exe'"
    if errorlevel 1 (
        echo ADVERTENCIA: No se pudo agregar el ejecutable
    ) else (
        echo OK - Ejecutable AutoShutdown.exe agregado
    )
)

REM Agregar la carpeta de instalación final
powershell -Command "Add-MpPreference -ExclusionPath 'C:\AutoShutdown'"
if errorlevel 1 (
    echo ADVERTENCIA: No se pudo agregar carpeta de instalacion
) else (
    echo OK - Carpeta C:\AutoShutdown agregada
)

echo.
echo ================================================
echo    Excepciones Agregadas Exitosamente
echo ================================================
echo.
echo Las siguientes rutas han sido agregadas a Windows Defender:
echo - %cd%
echo - %cd%\dist
if exist "dist\AutoShutdown.exe" echo - %cd%\dist\AutoShutdown.exe
echo - C:\AutoShutdown
echo.
echo Ahora puedes compilar sin que Windows Defender interfiera.
echo.
pause
