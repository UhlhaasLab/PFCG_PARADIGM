@echo off

REM Get participant name from first argument
set PARTICIPANT=%1

REM Optional: check if provided
if "%PARTICIPANT%"=="" (
    echo Please provide participant ID
    pause
    exit /b
)

"C:\Users\barada01\AppData\Local\Programs\PsychoPy\python.exe" ^
"C:\Users\barada01\Documents\paradigm\BI exp\BI-task-switch\psychopy-PFC\PFCG_PARADIGM\PFCG_paradigm.py" --participant %PARTICIPANT%

pause