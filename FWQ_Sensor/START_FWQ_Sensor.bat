@echo off
SET /P Kafka= Introduce la IP:Puerto del Kafka: 
SET /P attraction= Introduce el id de la atraccion: 
python FWQ_Sensor.py %Kafka% %attraction%
pause