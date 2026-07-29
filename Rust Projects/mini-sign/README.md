# mini-sign

A small Rust CLI demonstrating Ed25519 digital signatures.

## Features

- Generate public/private key pairs
- Sign files
- Verify signatures
- Detect file tampering

## Usage

cargo run -- generate-keys
cargo run -- sign files/message.txt
cargo run -- verify files/message.txt signatures/message.sig

## Concepts

- Public key cryptography
- Digital signatures
- Rust Result/error handling
- File I/O