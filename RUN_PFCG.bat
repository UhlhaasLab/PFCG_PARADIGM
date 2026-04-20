@echo off

set "PARTICIPANT=%~1"
@REM set "BLOCK=%~2"
set "viewing_distance=%~2"

set "LOGFILE=%PARTICIPANT%_log.txt"
set "LOGDIR=logs"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOGFILE=%LOGDIR%\%PARTICIPANT%_log.txt"

if "%PARTICIPANT%"=="" (
    echo Please provide participant ID
    pause
    exit /b
)

@REM make sure the python in psychopy path in vpixx computer is added her 
"C:\Users\barada01\AppData\Local\Programs\PsychoPy\python.exe" "C:\Users\barada01\Documents\paradigm\BI exp\BI-task-switch\psychopy-PFC\PFCG_PARADIGM\PFCG_paradigm_practice.py" 

if errorlevel 1 (
    echo Experiment 1 failed. Aborting.
    pause
    exit /b
)

@REM --block "%BLOCK%/" --viewing_distance_cm "%viewing_distance_cm%" if need to add block and viewing distance as arguments in the following line
"C:\Users\barada01\AppData\Local\Programs\PsychoPy\python.exe" "C:\Users\barada01\Documents\paradigm\BI exp\BI-task-switch\psychopy-PFC\PFCG_PARADIGM\PFCG_paradigm.py" --participant "%PARTICIPANT%" --viewing_distance "%viewing_distance%" 
@REM > "%LOGFILE%" 2>&1

pause 