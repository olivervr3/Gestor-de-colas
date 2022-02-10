Este proyecto consiste en la comunicación básica sockets, así como streaming de eventos y gestion de colas mediante Apache Kafka de una parque de atracciones.

Dicha implementación se ha realizado cifrando datos mediante comunicación asíncrona de servicios con OpenSSH, algoritmos de hashing para datos de usuario y la propia libreria de Apache Kafka para cifrar datos entre topics.

También se ha implementado dentro de los principios de arquitectura SOA (Service Oriented Architecture) y la tecnología de comunicación de basada en servicios REST.

Los usuarios del parque de atracciones se verán limitados por el tiempo que hace en diferentes países, así solo pudiendo subirse a atracciones donde haga buen tiempo. El tiempo lo consumimos de la API de OpenWeather.

La arquitectura de implementación es tal que:

![Alt text](Images/Arquitecture.PNG?raw=true "Arquitectura")

En la carpeta de DOC hay una especificación más en detalle del Código con una guía de despliegue.