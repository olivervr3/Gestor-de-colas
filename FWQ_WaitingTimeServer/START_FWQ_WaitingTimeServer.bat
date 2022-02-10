@echo off
SET /P Kafka= Introduce la IP:Puerto del Kafka: 
SET /P puerto= Introduce el puerto donde se abrira el servidor: 
python FWQ_WaitingTimeServer.py %puerto% %Kafka%
pause