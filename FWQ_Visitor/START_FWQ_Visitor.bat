@echo off
SET /P Kafka= Introduce la IP:Puerto del Kafka: 
SET /P registry= Introduce la IP:Puerto del Registry: 
SET /P api= Introduce la IP:Puerto de la API: 
python FWQ_Visitor.py %registry% %Kafka% %api%
pause