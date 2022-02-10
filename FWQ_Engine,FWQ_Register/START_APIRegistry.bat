@echo off
SET /P api= Introduce la IP:Puerto de la API: 
python API_Rest.py %api%
pause