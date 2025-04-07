# Cryptocurrency Proof of Concept (POC) - AP Computer Science Principles Project

## Introduction

This project is a Proof of Concept (POC) cryptocurrency system, developed as part of an AP Computer Science Principles project. It aims to demonstrate the fundamental principles of blockchain technology and cryptocurrency transactions in a simplified environment. The system includes a backend built with Python (FastAPI, websockets, MongoDB) and a frontend built with Next.js.

## Components

The system consists of the following main components:

1.  **FastAPI Backend (`main.py`)**:
    * Handles API endpoints for sending coins, registering users, and retrieving balances.
    * Manages user accounts, private/public key pairs, and transaction processing.
    * Uses websockets for communication with the blockchain nodes.
    * Implements transaction signing using ECDSA.
    * Uses a encryption key for secure communication between nodes.
    * Uses a .env file for sensitive information.
2.  **Blockchain Node (`blockchain.py`)**:
    * Maintains the blockchain data using MongoDB.
    * Validates transactions and adds them to blocks.
    * Implements a consensus mechanism (simplified Proof-of-Work).
    * Broadcasts new blocks and transactions to other nodes.
    * Manages peer-to-peer communication using websockets.
    * Verifies wallet balance before adding transactions.
3.  **Miner Node (`minner.py`)**:
    * Participates in the mining process to create new blocks.
    * Solves the Proof-of-Work puzzle.
    * Submits valid blocks to the blockchain node.
    * Communicates with the blockchain node using websockets.
4.  **Next.js Frontend**:
    * Provides a user interface for interacting with the cryptocurrency system.
    * Allows users to register, send coins, and view their balances.
    * Communicates with the FastAPI backend via API calls.

## Cryptocurrency Overview

This POC cryptocurrency operates on a simplified blockchain. Key features include:

* **Transactions**: Users can send coins to each other using their public keys as addresses.
* **Blocks**: Transactions are grouped into blocks, which are added to the blockchain.
* **Mining**: Miners solve a simple Proof-of-Work puzzle to create new blocks.
* **Integrity**: The blockchain's integrity is maintained through cryptographic hashing and transaction signing.
* **Wallets**: Users have wallets consisting of a public and private key pair.

## Ensuring Integrity

The integrity of the cryptocurrency is ensured through several mechanisms:

1.  **Transaction Signing (ECDSA)**:
    * Each transaction is signed by the sender's private key.
    * This ensures that only the owner of the private key can initiate a transaction.
    * The signature is verified by other nodes using the sender's public key.
2.  **Cryptographic Hashing (SHA-256)**:
    * Blocks are linked together using cryptographic hashes.
    * Each block contains the hash of the previous block, creating a chain.
    * Any tampering with a block will change its hash, invalidating subsequent blocks.
3.  **Proof-of-Work (Simplified)**:
    * Miners must solve a computational puzzle to create new blocks.
    * This makes it computationally expensive to alter the blockchain.
    * The first 5 charaters of the block hash must be 0's to be valid.
4.  **Node Synchronization**:
    * Blockchain nodes synchronize their data to ensure consistency.
    * Any discrepancies are resolved by adopting the longest valid chain.
    * Nodes send heartbeats to ensure they are still online.
5.  **Wallet Balance Verification**:
    * Before adding a transaction, the blockchain node verifies the sender's wallet balance.
    * This ensures that users cannot spend more coins than they own.

## AP Computer Science Principles Project

This project demonstrates several key concepts from the AP Computer Science Principles curriculum:

* **Abstraction**: The blockchain system abstracts away the complexities of cryptography and distributed systems.
* **Algorithms**: The mining process involves an algorithm to solve the Proof-of-Work puzzle.
* **Programming**: The system is implemented using Python and Next.js, demonstrating programming skills.
* **Data**: The blockchain is a distributed data structure.
* **Impact of Computing**: The project explores the potential impact of cryptocurrencies and blockchain technology.
* **Security**: The system incorporates cryptographic techniques to ensure security and integrity.
* **The internet**: the project uses websockets to represent peer to peer communication over the internet.
* **Global Impact**: Cryptocurrencies have a global impact, allowing for decentralized and borderless transactions.

## Setup Instructions

1.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn websockets pymongo python-dotenv ecdsa cryptography
    cd frontend
    npm install
    ```
2.  **Configure Environment Variables**:
    * Create a `.env` file in the root directory.
    * Add the following variables:
        ```
        NODE_KEY=<your_node_key>
        MINNER_KEY=<your_minner_key>
        DATABASE_URL=<your_mongodb_url>
        ENCRYPT_KEY=<your_encryption_key>
        ```
    * Generate secure random keys for `NODE_KEY`, `MINNER_KEY` and `ENCRYPT_KEY`.
    * Replace `<your_mongodb_url>` with your MongoDB connection string.
3.  **Run the Backend**:
    ```bash
    python blockchain.py
    python minner.py
    python main.py
    ```
4.  **Run the Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```
5.  **Access the Application**:
    * Open your web browser and navigate to `http://localhost:3000`.

## Notes

* This is a simplified POC and not intended for production use.
* The Proof-of-Work difficulty is very low for demonstration purposes.
* The system can be expanded to include more features, such as transaction fees and more complex consensus mechanisms.
* The front end is located in the folder called "frontend"