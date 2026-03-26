@echo off

set "PARTICIPANT=%~1"
@REM set "BLOCK=%~2"
set "LOGFILE=%PARTICIPANT%_log.txt"
set "LOGDIR=logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOGFILE=%LOGDIR%\%PARTICIPANT%_log.txt"

if "%PARTICIPANT%"=="" (
    echo Please provide participant ID
    pause
    exit /b
)
@REM @REM make sure the python in psychopy path in vpixx computer is added her 
@REM "C:\Users\barada01\AppData\Local\Programs\PsychoPy\python.exe" "C:\Users\barada01\Documents\paradigm\BI exp\BI-task-switch\psychopy-PFC\PFCG_PARADIGM\PFCG_paradigm_practice.py" > "%LOGFILE%" 2>&1

@REM if errorlevel 1 (
@REM     echo Experiment 1 failed. Aborting.
@REM     pause
@REM     exit /b
@REM )

@REM --block "%BLOCK%/"
"C:\Users\barada01\AppData\Local\Programs\PsychoPy\python.exe" "C:\Users\barada01\Documents\paradigm\BI exp\BI-task-switch\psychopy-PFC\PFCG_PARADIGM\PFCG_paradigm.py" --participant "%PARTICIPANT%" > "%LOGFILE%" 2>&1

pause 