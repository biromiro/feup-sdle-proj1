# SDLE First Assignment - Implementation of a Reliable Pub/Sub Service

SDLE First Assignment of group T05G11.

Group members:

1. João Baltazar (up201905616@up.pt)
2. Luís Lucas (up201904624@up.pt)
3. Nuno Costa (up201906272@up.pt)
4. Pedro Nunes (up201905396@up.pt)

# Description

 A publish/subscribe service is one of many possible messaging patterns typically used as a part of a message-oriented middleware (MOM) in distributed systems. This project's goal is to implement a reliable version of this service, using the *ZeroMQ* library.
    
The goal was achieved and the system meets the specifications. In this report, we showcase our implementation of the service using *Python*, while carefully explaining its reliability and failure scenarios and discussing possible improvements.

Implementing this service also prompted discussion, allowing for a deeper understanding of some difficulties in these types of systems such as the impossibility of perfect *exactly-once* delivery, information durability and server resilience and availability.

# How to run

## Server

The server can run using the following command, inside the ``src`` folder

```
python3 server.py [-h] (-a | -p) {0 , 1}
``` 
Where:
- ``-h`` outputs a help message
- ``-a`` or ``-p`` are required and decide whereas the server will be active or passive, respectively
- {0 , 1} decide which server to use

## Client
The client can run using the following command, inside the ``src`` folder

```
python3 client.py [-h] (operation)
```
Where:
- ``-h`` outputs a help message
- ``operation`` is the desired operation from the avaliable set of operations ``(get, put, subscribe, unsubscribe)``

### Get
To run a get command use the following
```
python3 client.py get <id> <topic>
```
Where:
- ``<id>`` is the client ID.
- ``<topic>`` is the topic we want to get from.
### Put
To run a put command use the following
```
python3 client.py put (-t TEXT | -f FILE) <topic>
```
Where:
- ``-t`` or ``-f`` are required and decides if we're putting text from the console or from a file. ``TEXT`` is the desired text and ``FILE`` is the filepath.
- ``<topic>`` is the desired publishing topic.
### Subscribe
To run a subscription command use the following
```
python3 client.py subscribe <id> <topic>
```
Where:
- ``<id>`` is the client ID.
- ``<topic>`` is the desired topic for subscription.
### Unsubscribe
To run a unsubscription command use the following
```
python3 client.py unsubscribe <id> <topic>
```
Where:
- ``<id>`` is the client ID.
- ``<topic>`` is the desired topic for unsubscription.
