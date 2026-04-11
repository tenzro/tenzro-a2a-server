"""Agent Card builder — serves at /.well-known/agent.json for A2A discovery."""


def build_agent_card(base_url: str = "https://a2a.tenzro.network") -> dict:
    """Build the A2A Agent Card with all 19 skills."""
    return {
        "name": "Tenzro Network Agent",
        "description": (
            "Tenzro Network -- AI-native agentic tokenized settlement layer. "
            "Provides wallet operations, identity management, inference routing, "
            "settlement, and blockchain interaction."
        ),
        "url": f"{base_url}/a2a",
        "version": "0.1.0",
        "protocolVersion": "0.2.0",
        "capabilities": {
            "streaming": True,
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "skills": [
            {
                "id": "wallet",
                "name": "Wallet Operations",
                "description": (
                    "Create wallets, check balances, and send TNZO transactions "
                    "on the Tenzro network."
                ),
                "tags": ["blockchain", "wallet", "payments"],
                "examples": [
                    "Check my TNZO balance",
                    "Send 10 TNZO to 0xabc...",
                    "Create a new wallet",
                ],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain", "application/json"],
            },
            {
                "id": "identity",
                "name": "Identity Management",
                "description": (
                    "Register and resolve decentralized identities (DIDs) "
                    "on the Tenzro Decentralized Identity Protocol (TDIP). "
                    "Manage human-readable usernames with set_username and "
                    "resolve_username for easy identity lookup."
                ),
                "tags": ["identity", "did", "credentials", "username"],
                "examples": [
                    "Register a new identity",
                    "Resolve DID did:tenzro:human:abc123",
                    "Set my username to alice",
                    "Resolve username bob",
                ],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain", "application/json"],
            },
            {
                "id": "inference",
                "name": "AI Inference",
                "description": (
                    "Route AI inference requests to model providers on the "
                    "Tenzro network, with settlement in TNZO."
                ),
                "tags": ["ai", "inference", "models"],
                "examples": [
                    "List available AI models",
                    "Run inference on model X",
                ],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain", "application/json"],
            },
            {
                "id": "settlement",
                "name": "Settlement & Payments",
                "description": (
                    "Settle payments for AI services using micropayment channels, "
                    "escrow, and batch settlement on the Tenzro ledger."
                ),
                "tags": ["settlement", "payments", "escrow"],
                "examples": [
                    "Check settlement status",
                    "Open a micropayment channel",
                ],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain", "application/json"],
            },
            {
                "id": "verification",
                "name": "Proof Verification",
                "description": (
                    "Verify ZK proofs, TEE attestations, and transaction signatures "
                    "on the Tenzro network."
                ),
                "tags": ["verification", "zk-proofs", "tee"],
                "examples": [
                    "Verify a ZK proof",
                    "Check TEE attestation",
                ],
                "inputModes": ["application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "staking",
                "name": "Staking & Provider Management",
                "description": (
                    "Stake TNZO tokens, manage validator/provider registration, "
                    "and query provider performance statistics."
                ),
                "tags": ["staking", "provider", "validator"],
                "examples": [
                    "How much TNZO is staked?",
                    "Register as a model provider",
                    "Get provider statistics",
                ],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain", "application/json"],
            },
            {
                "id": "task_marketplace",
                "name": "Task Marketplace",
                "description": (
                    "Post tasks to the decentralized AI task marketplace, browse "
                    "open tasks, submit quotes, and track task completion with "
                    "TNZO escrow-based payment."
                ),
                "tags": ["tasks", "marketplace", "ai", "escrow"],
                "examples": [
                    "Post a code review task for 50 TNZO",
                    "List open inference tasks",
                    "Get task status for task-id-123",
                    "Cancel my pending task",
                    "Submit a quote for task-id-456",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "agent_marketplace",
                "name": "Agent Marketplace",
                "description": (
                    "Publish, discover, rate, and spawn reusable AI agent templates on "
                    "the Tenzro decentralized agent marketplace. Search templates "
                    "by capability, type, and pricing model. Rate templates, view "
                    "template stats, and spawn running agents from templates."
                ),
                "tags": ["agents", "marketplace", "templates", "ai", "rating"],
                "examples": [
                    "List available agent templates",
                    "Register a new coding agent template",
                    "Search for autonomous agent templates",
                    "Get agent template details for template-id-789",
                    "Rate template template-id-789 with 5 stars",
                    "Spawn an agent from template template-id-789",
                    "Get stats for agent template template-id-789",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "agent_spawning",
                "name": "Agent Spawning",
                "description": (
                    "Dynamically spawn autonomous sub-agents with specific capabilities. "
                    "Parent agents can create up to 50 children, each with its own DID "
                    "and MPC wallet. Supports hierarchical agent topologies."
                ),
                "tags": ["agents", "spawning", "autonomous", "orchestration"],
                "examples": [
                    "Spawn a sub-agent with coding capabilities",
                    "List my child agents",
                    "Run an autonomous agent task",
                    "Spawn an agent named 'researcher' with web-search capability",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "swarm_orchestration",
                "name": "Swarm Orchestration",
                "description": (
                    "Create and manage agent swarms for parallel task execution. "
                    "An orchestrator agent can create a swarm of specialized sub-agents, "
                    "broadcast tasks to all members simultaneously, collect results, "
                    "and terminate the swarm when done."
                ),
                "tags": ["swarm", "orchestration", "parallel", "agents"],
                "examples": [
                    "Create a swarm with 3 research agents",
                    "Get swarm status for swarm-id-123",
                    "Terminate swarm swarm-id-456",
                    "Broadcast 'analyze this dataset' to my swarm",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "token",
                "name": "Token Management",
                "description": (
                    "Create ERC-20 tokens, query token info and balances, "
                    "transfer tokens across VMs (EVM, SVM, DAML), and wrap "
                    "native TNZO to VM representations via the unified token registry."
                ),
                "tags": ["token", "erc20", "cross-vm", "registry"],
                "examples": [
                    "Create a new token called MyToken (MTK) with 1M supply",
                    "Get token info for TNZO",
                    "List all registered tokens",
                    "Get my TNZO balance across all VMs",
                    "Transfer 100 TNZO from EVM to SVM",
                    "Wrap 50 TNZO for EVM",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "contract",
                "name": "Smart Contract Deployment",
                "description": (
                    "Deploy smart contracts to the Tenzro multi-VM runtime "
                    "(EVM, SVM, DAML). Submit bytecode with constructor arguments "
                    "and receive the deployed contract address."
                ),
                "tags": ["contract", "deploy", "evm", "svm", "daml"],
                "examples": [
                    "Deploy an EVM contract with bytecode 0x6080...",
                    "Deploy a Solana program",
                    "What VMs are supported for contract deployment?",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "ap2-payments",
                "name": "AP2 Payments",
                "description": (
                    "Agent Payments Protocol (AP2) for autonomous financial "
                    "transactions. Create, authorize, execute, check status, "
                    "and cancel payments between agents."
                ),
                "tags": ["payments", "ap2", "agentic", "settlement"],
                "examples": [
                    "Create payment for 100 TNZO",
                    "Authorize spending limit of 1000 TNZO",
                    "Execute payment pay-id-123",
                    "Check payment status for pay-id-456",
                    "Cancel pending payment pay-id-789",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "join",
                "name": "Join as MicroNode",
                "description": (
                    "Join the Tenzro Network as a full MicroNode participant -- "
                    "zero-install. Auto-provisions a TDIP DID, MPC wallet, and "
                    "10 network capabilities (inference, payments, agent collaboration, "
                    "MCP tools, task execution, chain queries, smart contracts, "
                    "TEE compute, cross-chain bridge, governance)."
                ),
                "tags": ["join", "onboarding", "micronode", "identity", "wallet"],
                "examples": [
                    "Join the Tenzro Network as Alice",
                    "Create a new identity on Tenzro",
                    "Onboard to Tenzro with username Bob",
                    "Join as a MicroNode",
                ],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain", "application/json"],
            },
            {
                "id": "nft",
                "name": "NFT Management",
                "description": (
                    "Create and manage NFT collections (ERC-721/1155), mint tokens, "
                    "transfer, query ownership, cross-VM pointers."
                ),
                "tags": ["nft", "erc721", "erc1155", "collectibles", "cross-vm"],
                "examples": [
                    "Create a new ERC-721 NFT collection",
                    "Mint an NFT in collection 0xabc...",
                    "Transfer NFT #42 to 0xdef...",
                    "Query ownership of NFT #7",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "bridge",
                "name": "Cross-Chain Bridge",
                "description": (
                    "Cross-chain bridge operations via LI.FI aggregator (58+ chains), "
                    "LayerZero, CCIP v1.6, deBridge with hooks."
                ),
                "tags": ["bridge", "cross-chain", "lifi", "layerzero", "ccip", "debridge"],
                "examples": [
                    "Bridge 100 TNZO from Ethereum to Solana",
                    "Get bridge routes from Tenzro to Base",
                    "Estimate bridge fee for 500 USDC to Arbitrum",
                    "List available bridge adapters",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "compliance",
                "name": "Compliance & KYC",
                "description": (
                    "ERC-3643 T-REX compliance: KYC verification, accreditation, "
                    "country restrictions, freeze/recover, trusted issuers."
                ),
                "tags": ["compliance", "kyc", "erc3643", "t-rex", "accreditation"],
                "examples": [
                    "Verify KYC status for address 0xabc...",
                    "Check accreditation for investor 0xdef...",
                    "List country restrictions for token XYZ",
                    "Freeze token holdings for 0x123...",
                    "Add a trusted issuer to the registry",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "crosschain",
                "name": "Cross-Chain Token Standard",
                "description": (
                    "ERC-7802 cross-chain token standard: authorized bridge mint/burn "
                    "with rate limits and audit trail."
                ),
                "tags": ["crosschain", "erc7802", "mint", "burn", "rate-limit"],
                "examples": [
                    "Authorize a bridge for cross-chain minting",
                    "Set rate limit for bridge 0xabc... to 10000 TNZO/day",
                    "Query audit trail for cross-chain token transfers",
                    "Revoke bridge authorization for 0xdef...",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json"],
            },
            {
                "id": "events",
                "name": "Event Streaming",
                "description": (
                    "Real-time event streaming via WebSocket (eth_subscribe), gRPC, "
                    "webhooks with HMAC signatures, historical queries."
                ),
                "tags": ["events", "websocket", "streaming", "webhooks", "grpc"],
                "examples": [
                    "Subscribe to new block events via WebSocket",
                    "Register a webhook for transfer events on 0xabc...",
                    "Query historical events for contract 0xdef...",
                    "Stream pending transactions in real time",
                ],
                "inputModes": ["text/plain", "application/json"],
                "outputModes": ["application/json", "text/event-stream"],
            },
        ],
        "defaultInputModes": ["text/plain", "application/json"],
        "defaultOutputModes": ["text/plain", "application/json"],
    }
