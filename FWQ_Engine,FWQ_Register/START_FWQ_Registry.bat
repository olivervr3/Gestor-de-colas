@echo off
SET /P puerto= Introduce el puerto donde quieres que se te abra el servidor Registry: 
python FWQ_Registry.py %puerto%
pause