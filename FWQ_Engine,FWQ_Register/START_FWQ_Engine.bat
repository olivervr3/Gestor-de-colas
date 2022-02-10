@echo off
SET /P Kafka= Introduce la IP:Puerto del Kafka: 
SET /P visitantes= Introduce el numero de visitiantes maximos: 
SET /P puerto= Introduce la ip:puerto del servidor de tiempos de espera:  
python FWQ_Engine.py %Kafka% %visitantes% %puerto%
pause