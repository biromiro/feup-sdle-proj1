# SDLE First Assignment - Implementation of a Reliable Pub/Sub Service

SDLE First Assignment of group T05G11.

Group members:

1. &lt;João&gt; &lt;Baltazar&gt; (&lt;up201905616@up.pt&gt;)
2. &lt;Luís&gt; &lt;Lucas&gt; (&lt;up201904624@up.pt&gt;)
3. &lt;Nuno&gt; &lt;Costa&gt; (&lt;up201906272@up.pt&gt;)
4. &lt;Pedro&gt; &lt;Nunes&gt; (&lt;up201905396@up.pt&gt;)

# Description

A publish/subscribe service is one of many possible messaging patterns typically used as a part of a message-oriented middleware (MOM) in distributed systems. This project’s goal is to implement a reliable version of this service. The goal was achieved and the system meets the specifications. In this report, we showcase our implementation of the
service, while carefully explaining its reliability and failure
scenarios and discussing possible improvements.
Implementing this service also prompted discussion, allowing for a deeper understanding of some difficulties in
these types of systems such as the impossibility of perfect
exactly-once delivery and information durability.

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
A get command can run using the following command
```
python3 client.py get <id> <topic>
```
Where:
- ``<id>`` is the client ID.
- ``<topic>`` is the topic we want to get from.
### Put
A put command can run using the following command
```
python3 client.py put (-t TEXT | -f FILE) <topic>
```
Where:
- ``-t`` or ``-f`` are required and decides if we're putting text from the console or from a file. ``TEXT`` is the desired text and ``FILE`` is the filepath.
- ``<topic>`` is the desired publishing topic.
### Subscribe
A subscription command can run using the following command
```
python3 client.py subscribe <id> <topic>
```
Where:
- ``<id>`` is the client ID.
- ``<topic>`` is the desired topic for subscription.
### Unsubscribe
```
python3 client.py unsubscribe <id> <topic>
```
Where:
- ``<id>`` is the client ID.
- ``<topic>`` is the desired topic for unsubscription.