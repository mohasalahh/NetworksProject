# Chat Room Implementation using TCP and UDP Sockets in Python

This project is a comprehensive implementation of a chat room application using both TCP and UDP sockets. It's structured into several directories, each serving a specific purpose in the overall architecture of the application.

## Directory Structure

### Client
This directory contains the client-side implementation of the chat room.
- `ClientServer.py`: Main client-side server script.
- `RegistryThread.py`: Manages client registration in a separate thread.
- `UDPServer.py`: UDP server implementation for the client.
- `configurations.py`: Configuration settings for the client.
- `db.py`: Database functionalities for the client.
- `registry.py`: Client registry functionalities.

### LoadTesting
Dedicated to load testing of the chat room application.
- `LoadTesting.py`: Script for conducting load testing.
- `LoadTestingResults.py`: Script for analyzing and presenting load testing results.
- `configurations.py`: Configuration settings for load testing.
- `empty_saved_dictionary.pkl` and `saved_dictionary.pkl`: Pickle files for storing test data/results.
- `load_testing.log`: Log file for load testing activities.

### Peer
Contains scripts related to the peer-to-peer aspect of the chat room.
- `PeerClient.py`: Peer client script.
- `PeerServer.py`: Server part of the peer-to-peer communication.
- `PeerThread.py`: Manages peer connections in separate threads.
- `configurations.py`: Configuration settings for peer-to-peer communication.
- `peer.py`: Core functionalities of peer-to-peer communication.

### Testing
Scripts for testing different components of the application.
- `AuthTesting.py`: Testing authentication mechanisms.
- `EncryptionTesting.py`: Testing encryption functionalities.

### Utils
Utility scripts used across various parts of the project.
- `AESEnryptionUtils.py`: Utility script for AES encryption.

## Setup and Running

### Prerequisites
- Python 3.x
- Additional libraries: [List any additional libraries required]

### Installation
- Clone the repository: `git clone [repository-url]`
- Navigate to the project directory: `cd [project-directory]`
- Install required libraries: `pip install -r requirements.txt` (if applicable)

### Running the Application
- Start the server: `python [server-script]`
- Run the client: `python [client-script]`

## Testing
- To run tests, navigate to the `Testing` directory and execute: `pytest [test-script]`

