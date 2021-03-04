@echo off
rem Bypass "Terminate Batch Job" prompt.
if "%~1"=="-FIXED_CTRL_C" (
   REM Remove the -FIXED_CTRL_C parameter
   SHIFT
) ELSE (
   REM Run the batch with <NUL and -FIXED_CTRL_C
   CALL <NUL %0 -FIXED_CTRL_C %*
   GOTO :EOF
)
TITLE Amazon Bot
pipenv run python destroybots.py
for /d %%a in (G:\nvidia-bot\.profile-amz-*) do rd "%%a" /s /q
pipenv run python app.py amazon --shipping-bypass --delay 2 --p GkfUmwX3DrJiiE
EXIT