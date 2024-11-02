# Files For Peers - UDHT
**Project Status: Development**

This is a repository containing two micro services that compound a distributed hashtable project that area a system part of a Files for Peers project, it relevant to say that this only a part of the project, in this documentation we will discuss the objetives and goals of the project and them go through the two microservies that are in this part of the system.

# Project Details 

This project aims to utilize a decentralized network for peer-to-peer file sharing, leveraging blockchain to store and validate transactions between peers. The system comprises four main components:

 - **UDHT** (Users Distributed Hash Table) - a hash table structure that holds peer information, enabling peer connections, information sharing, and network-wide peer updates.
  
 - **FDHT** (File Distribuited Hash Table) - A hash table where peers can store files they wish to share with others, designed to efficiently locate files.

 - **BlockChain** (BlockChain Application) - This blockchain system is responsible for storing and recording new transactions, categorized as _Upload Blocks_, _Download Blocks_, or _Hold Stake Blocks_. It operates using a proof-of-stake mechanism for block validation, ensuring efficient and secure transaction processing within the network.

# UDHT 
This component is responsible for maintaining sufficient peer information to establish connections and synchronize data with other peers. It manages the sharing of its own hash table, merges it with those of other peers, and facilitates the distribution of the updated hash table across the network.

This application is divided into two microservices to optimize resource utilization, DHTManager and DHTSync.

## DHTManager
The DHTManager is a microservice responsible for managing the Distributed Hash Table (DHT). It provides an interface for creating, deleting, updating, and retrieving peers, as well as accessing all data within the hash table. Additionally, it handles the persistence of the hash table and manages the serialization and deserialization of its data.

This microservice exclusively allows connections from localhost, ensuring that no external access is permitted. It is essential to note that this design prioritizes security and local communication among microservices.

### Diagram 

![DHT Manager Diagram](https://raw.githubusercontent.com/felipemelonunes09/FilesForPeers-udht/main/docs/dhtmanager-driagram)

### Running
To run this microservice, download the code and use the following command, specifying the desired port:
```python
python3 main.py DHT_PORT=<port>
```
If you have a containerized environment, you can modify the variable in the docker-compose file and use the following command to bring up all containers using Docker:
```bash
docker-compose up --build
```

### Usage 
To use this microservice, establish a local TCP/IP connection with the specified service port. Once connected, you can interact with the service using the following options:

- Create Peer: Add a new peer.
- Delete Peer: Remove an existing peer.
- Edit Peer: Modify details of an existing peer.
- Get Peer: Retrieve information about a specific peer.
- Get HashTable: Access the current hash table binary.
- Close: to send a signal to the server that you are closing the connection.



