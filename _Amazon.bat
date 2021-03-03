@echo off
TITLE Amazon Bot
pipenv run python destroybots.py
for /d %%a in (G:\nvidia-bot\.profile-amz-*) do rd "%%a" /s /q
pipenv run python app.py amazon --shipping-bypass --delay 2 --p GkfUmwX3DrJiiE