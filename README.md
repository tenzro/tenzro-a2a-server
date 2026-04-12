# Tenzro A2A Server

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![A2A Protocol](https://img.shields.io/badge/A2A-0.2.0-blue)](https://a2a-protocol.org)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

Connect AI agents to Tenzro Network using Google's [Agent-to-Agent (A2A)](https://a2a-protocol.org) protocol.

## Overview

The Tenzro A2A server is an installable Python package that lets any A2A-compatible agent interact with the blockchain — query balances, send transactions, manage identities, spawn sub-agents, trade on marketplaces, deploy contracts, and more. Install with `pip install tenzro-a2a-server` and run locally, or connect directly to the live testnet endpoint.

**Live testnet:** `https://a2a.tenzro.network`
**Local:** `http://localhost:3002`

## Installation

```bash
pip install tenzro-a2a-server
```

Or from source:

```bash
git clone https://github.com/tenzro/tenzro-a2a-server.git
cd tenzro-a2a-server
pip install .
```

## Endpoints

| Endpoint | URL | Description |
|----------|-----|-------------|
| Agent Card | `GET /.well-known/agent.json` | Agent capability discovery |
| A2A RPC | `POST /a2a` | JSON-RPC 2.0 task execution |
| A2A Stream | `POST /a2a/stream` | Server-Sent Events streaming |

## Quick Start

### Discover capabilities

```bash
curl https://a2a.tenzro.network/.well-known/agent.json
```

### Send a task

```bash
curl -X POST https://a2a.tenzro.network/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{ "type": "text", "text": "What is my balance for address 0x1234...?" }]
      }
    },
    "id": 1
  }'
```

### Stream a response (SSE)

```bash
curl -X POST https://a2a.tenzro.network/a2a/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{ "type": "text", "text": "Get the current block height" }]
      }
    },
    "id": 1
  }'
```

## Agent Skills (23)

The Tenzro A2A agent exposes 23 skills covering blockchain, AI, identity, payments, cryptography, security, and agent orchestration:

### Core Blockchain

| Skill | ID | Description |
|-------|-----|-------------|
| **Wallet Operations** | `wallet` | Create wallets, check balances, send TNZO transactions |
| **Token Management** | `token` | Create ERC-20 tokens, cross-VM transfers, wrap TNZO |
| **Smart Contracts** | `contract` | Deploy contracts to EVM, SVM, or DAML |
| **NFT Management** | `nft` | Create collections, mint, transfer, and query NFTs across VMs |
| **Staking & Providers** | `staking` | Stake TNZO, register as validator/provider |

### Identity & Payments

| Skill | ID | Description |
|-------|-----|-------------|
| **Identity Management** | `identity` | Register/resolve DIDs (TDIP), set usernames |
| **Settlement & Payments** | `settlement` | Micropayment channels, escrow, batch settlement |
| **AP2 Payments** | `ap2-payments` | Agent-to-agent autonomous financial transactions |

### AI & Agents

| Skill | ID | Description |
|-------|-----|-------------|
| **AI Inference** | `inference` | Route inference to model providers, settle in TNZO |
| **Agent Spawning** | `agent_spawning` | Spawn sub-agents with own DID and wallet (up to 50) |
| **Swarm Orchestration** | `swarm_orchestration` | Create agent swarms for parallel task execution |
| **Task Marketplace** | `task_marketplace` | Post/browse tasks with TNZO escrow payment |
| **Agent Marketplace** | `agent_marketplace` | Publish, discover, rate, and spawn agent templates |

### Cross-Chain & Compliance

| Skill | ID | Description |
|-------|-----|-------------|
| **Cross-Chain Bridge** | `bridge` | Bridge tokens between Tenzro, Ethereum, Solana, Base via LayerZero/CCIP/deBridge |
| **Cross-Chain Token** | `crosschain` | ERC-7802 cross-chain token standard, mint/burn bridging |
| **Compliance & KYC** | `compliance` | ERC-3643 T-REX compliance, identity verification, KYC attestation |

### Cryptography & Security

| Skill | ID | Description |
|-------|-----|-------------|
| **Cryptography** | `crypto` | Sign, verify, encrypt, decrypt, hash, key exchange (Ed25519, Secp256k1, AES-256-GCM, X25519) |
| **TEE Security** | `tee` | Hardware attestation (TDX, SEV-SNP, Nitro, NVIDIA GPU), seal/unseal data in enclaves |
| **Zero-Knowledge Proofs** | `zk` | Generate and verify Groth16 ZK proofs, manage proving keys and circuits |
| **Key Custody** | `custody` | MPC threshold wallets, encrypted keystores, session keys, spending limits, key rotation |

### Verification & Onboarding

| Skill | ID | Description |
|-------|-----|-------------|
| **Proof Verification** | `verification` | Verify ZK proofs, TEE attestations, transaction signatures |
| **Event Streaming** | `events` | Subscribe to blockchain events via WebSocket, webhooks, gRPC |
| **Join as MicroNode** | `join` | Zero-install network participation with auto-provisioned DID + wallet |

## A2A Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `tasks/send` | Send a message, create or continue a task | `message` (role, parts), `metadata` |
| `tasks/get` | Get task by ID | `id`, `history_length` |
| `tasks/list` | List tasks | `context_id` (optional) |
| `tasks/cancel` | Cancel a running task | `id` |

## Message Routing

The agent routes messages based on natural language content:

| Keywords | Skill |
|----------|-------|
| `balance`, `wallet`, `send`, `transfer` | Wallet Operations |
| `block`, `height`, `transaction` | Block/transaction queries |
| `identity`, `did`, `register`, `resolve`, `username` | Identity Management |
| `model`, `inference`, `ai`, `chat` | AI Inference |
| `payment`, `challenge`, `mpp`, `x402`, `ap2` | Payments |
| `stake`, `validator`, `provider` | Staking |
| `token`, `erc20`, `create token`, `wrap` | Token Management |
| `deploy`, `contract`, `bytecode` | Smart Contracts |
| `spawn`, `sub-agent`, `child agent` | Agent Spawning |
| `swarm`, `parallel`, `orchestrat` | Swarm Orchestration |
| `task`, `marketplace`, `post task`, `quote` | Task Marketplace |
| `template`, `agent marketplace`, `rating` | Agent Marketplace |
| `sign`, `verify signature`, `encrypt`, `decrypt`, `hash`, `key exchange`, `keypair` | Cryptography |
| `tee`, `enclave`, `seal`, `unseal`, `attestation hardware` | TEE Security |
| `zk proof`, `groth16`, `proving key`, `circuit` | Zero-Knowledge Proofs |
| `mpc wallet`, `keystore`, `session key`, `spending limit`, `key rotation`, `custody` | Key Custody |
| `verify`, `proof`, `attestation`, `zk` | Verification |
| `join`, `micronode`, `onboard` | Join as MicroNode |
| `nft`, `collection`, `mint`, `transfer nft` | NFT Management |
| `bridge`, `cross-chain`, `layerzero`, `ccip`, `debridge`, `dln`, `same chain swap` | Cross-Chain Bridge |
| `compliance`, `kyc`, `t-rex`, `erc-3643`, `whitelist` | Compliance & KYC |
| `erc-7802`, `cross-chain token`, `crosschain` | Cross-Chain Token |
| `event`, `subscribe`, `webhook`, `stream`, `listen` | Event Streaming |
| `canton` | Cross-chain bridge |
| `status`, `health`, `node`, `peer`, `network` | Node status |
| `faucet`, `tokens` | Testnet faucet |

## Examples

See the `examples/` directory:

- [`typescript-client.ts`](examples/typescript-client.ts) — TypeScript A2A client
- [`python-client.py`](examples/python-client.py) — Python A2A client (zero deps)
- [`curl-examples.sh`](examples/curl-examples.sh) — cURL command examples

## Integration with AI Frameworks

### LangChain

```python
from langchain.tools import Tool
import requests

def tenzro_a2a(query: str) -> str:
    response = requests.post("https://a2a.tenzro.network/a2a", json={
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": query}]
            }
        },
        "id": 1
    })
    task = response.json().get("result", {})
    for msg in reversed(task.get("messages", [])):
        if msg.get("role") == "agent":
            return msg["parts"][0]["text"]
    return "No response"

tenzro_tool = Tool(
    name="TenzroBlockchain",
    func=tenzro_a2a,
    description="Interact with Tenzro Network — wallets, identities, payments, AI inference, agents, tokens, contracts"
)
```

### CrewAI

```python
from crewai.tools import tool
import requests

@tool("Tenzro Blockchain")
def tenzro_blockchain(query: str) -> str:
    """Interact with Tenzro Network — wallets, identities, AI inference, payments, agents, tokens, contracts, verification."""
    response = requests.post("https://a2a.tenzro.network/a2a", json={
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": query}]
            }
        },
        "id": 1
    })
    task = response.json().get("result", {})
    for msg in reversed(task.get("messages", [])):
        if msg.get("role") == "agent":
            return msg["parts"][0]["text"]
    return "No response"
```

## Architecture

```
Your Agent                    Tenzro Node
    |                              |
    |-- GET /.well-known/agent.json -->  Agent Card (23 skills)
    |                              |
    |-- POST /a2a (tasks/send) ------->  Task Manager
    |                              |     |
    |                              |     v
    |                              |  Message Router
    |                              |  (wallet? identity? spawn? marketplace?)
    |                              |     |
    |                              |     v
    |                              |  Node Subsystems
    |                              |  (Storage, Identity, Wallet, Settlement,
    |                              |   Verification, Bridge, Model Registry,
    |                              |   Agent Runtime, Token Registry, VM...)
    |                              |     |
    |<-- A2aTask (completed) ------------|
```

## Combining A2A with MCP

| Protocol | Best For | Endpoint |
|----------|----------|----------|
| **A2A** (this) | Natural language task delegation | `a2a.tenzro.network/a2a` |
| **MCP** | Structured tool calls from Claude/Cursor | `mcp.tenzro.network/mcp` |
| **JSON-RPC** | Direct EVM-compatible RPC | `rpc.tenzro.network` |
| **Web API** | REST verification and status | `api.tenzro.network` |
| **LI.FI MCP** | Cross-chain bridge aggregation (66 chains) | `lifi-mcp.tenzro.network/mcp` |
| **deBridge** | Official DLN cross-chain swaps | `agents.debridge.com/mcp` |
| **1inch** | DEX aggregation, Fusion swaps | `api.1inch.com/mcp/protocol` |

## Running the Server

```bash
tenzro-a2a-server --port 3002
```

Or with a custom RPC endpoint:

```bash
TENZRO_RPC_URL=http://localhost:8545 tenzro-a2a-server --port 3002
```

### Test the server

```bash
curl https://localhost:3002/.well-known/agent.json
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `TENZRO_RPC_URL` | `https://rpc.tenzro.network` | Tenzro JSON-RPC endpoint |
| `TENZRO_API_URL` | `https://api.tenzro.network` | Tenzro Web API endpoint |

Command-line options:

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `3002` | HTTP server port |
| `--host` | `0.0.0.0` | HTTP server bind address |

## Related

| Resource | URL |
|----------|-----|
| Tenzro Network | [tenzro.com](https://tenzro.com) |
| MCP Server | [github.com/tenzro/tenzro-mcp-server](https://github.com/tenzro/tenzro-mcp-server) |
| TenzroClaw | [github.com/tenzro/TenzroClaw](https://github.com/tenzro/TenzroClaw) |
| A2A Protocol | [a2a-protocol.org](https://a2a-protocol.org) |

## Contact

- Website: [tenzro.com](https://tenzro.com)
- Engineering: [eng@tenzro.com](mailto:eng@tenzro.com)
- GitHub: [github.com/tenzro](https://github.com/tenzro)

## License

Apache 2.0. See [LICENSE](LICENSE).
