"""Handler functions for each routed skill.

Every handler accepts the user's natural-language text (and optional metadata)
and returns a plain-text or JSON response string by calling the Tenzro JSON-RPC
or Web API.
"""

from .rpc_client import rpc_call, api_call
import json
import re


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_address(text: str) -> str | None:
    """Extract a hex address from text."""
    m = re.search(r"0x[a-fA-F0-9]+", text)
    return m.group(0) if m else None


def _extract_did(text: str) -> str | None:
    """Extract a did:tenzro:... or did:pdis:... identifier."""
    m = re.search(r"did:(tenzro|pdis):\S+", text)
    return m.group(0).rstrip("?.!,;") if m else None


def _extract_amount(text: str) -> float | None:
    """Extract a numeric amount from text like 'send 10 TNZO'."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:TNZO|tnzo|tokens?)?", text)
    return float(m.group(1)) if m else None


def _extract_name(text: str) -> str:
    """Extract a name/label from the end of the text, fallback to 'Anonymous'."""
    words = text.strip().rstrip("?.!,;").split()
    return words[-1] if len(words) > 2 else "Anonymous"


def _extract_id(text: str, prefix: str = "") -> str | None:
    """Extract a UUID-like or prefixed identifier."""
    pattern = (
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )
    m = re.search(pattern, text)
    return m.group(0) if m else None


# ---------------------------------------------------------------------------
# Wallet & Blockchain
# ---------------------------------------------------------------------------

async def handle_wallet(text: str, metadata: dict = None) -> str:
    t = text.lower()
    addr = _extract_address(text)

    if "create" in t or "new wallet" in t:
        result = await rpc_call("tenzro_createWallet", ["ed25519"])
        return (
            f"Wallet created:\n"
            f"  Address: {result['address']}\n"
            f"  Key type: {result['key_type']}\n"
            f"  Threshold: {result['threshold']}-of-{result['total_shares']}"
        )

    if ("send" in t or "transfer" in t) and addr:
        # Try to find a second address and amount
        addresses = re.findall(r"0x[a-fA-F0-9]+", text)
        amount = _extract_amount(text)
        if len(addresses) >= 2 and amount:
            from_addr = addresses[0]
            to_addr = addresses[1]
            # Query nonce and chain id
            nonce_hex = await rpc_call("eth_getTransactionCount", [from_addr, "latest"])
            chain_id_hex = await rpc_call("eth_chainId", [])
            nonce = int(nonce_hex, 16) if nonce_hex else 0
            chain_id = int(chain_id_hex, 16) if chain_id_hex else 1337
            wei = int(amount * 1e18)
            tx = {
                "from": from_addr,
                "to": to_addr,
                "value": hex(wei),
                "nonce": hex(nonce),
                "chainId": hex(chain_id),
                "gas": hex(21000),
                "gasPrice": hex(10**9),
            }
            result = await rpc_call("eth_sendRawTransaction", [json.dumps(tx)])
            return f"Transaction sent.\n  Hash: {result}\n  From: {from_addr}\n  To: {to_addr}\n  Amount: {amount} TNZO"
        return (
            "To send TNZO, provide: from address, to address, and amount.\n"
            "Example: 'Send 10 TNZO from 0xabc... to 0xdef...'"
        )

    if addr:
        result = await rpc_call("eth_getBalance", [addr, "latest"])
        wei = int(result, 16) if result else 0
        tnzo = wei / 1e18
        return f"Balance for {addr}: {tnzo:.6f} TNZO ({wei} wei)"

    return (
        "Wallet operations:\n"
        "  - 'Create a new wallet'\n"
        "  - 'Check balance for 0xabc...'\n"
        "  - 'Send 10 TNZO from 0xabc... to 0xdef...'"
    )


async def handle_block(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "transaction" in t:
        tx_hash = _extract_address(text)
        if tx_hash:
            result = await rpc_call("tenzro_getTransaction", [tx_hash])
            return json.dumps(result, indent=2)
        return "Provide a transaction hash (0x...) to look up."

    result = await rpc_call("eth_blockNumber", [])
    height = int(result, 16) if result else 0
    return f"Current block height: {height}"


async def handle_status(text: str, metadata: dict = None) -> str:
    result = await rpc_call("tenzro_nodeInfo", [])
    return (
        f"Node Status:\n"
        f"  Role: {result.get('role', 'unknown')}\n"
        f"  State: {result.get('state', 'unknown')}\n"
        f"  Peers: {result.get('peer_count', 0)}\n"
        f"  Block height: {result.get('block_height', 0)}\n"
        f"  Uptime: {result.get('uptime_secs', 0)}s"
    )


async def handle_network(text: str, metadata: dict = None) -> str:
    peer_count = await rpc_call("tenzro_peerCount", [])
    listening = await rpc_call("net_listening", [])
    return (
        f"Network Info:\n"
        f"  Peers: {peer_count}\n"
        f"  Listening: {listening}"
    )


async def handle_faucet(text: str, metadata: dict = None) -> str:
    addr = _extract_address(text)
    if not addr:
        return "Provide an address to receive testnet TNZO.\nExample: 'Request faucet tokens for 0xabc...'"
    result = await api_call("/api/faucet", method="POST", body={"address": addr})
    if result.get("error"):
        return f"Faucet error: {result['error']}"
    amount = result.get("amount", "100")
    tx_hash = result.get("tx_hash", "pending")
    return (
        f"Faucet tokens sent!\n"
        f"  Address: {addr}\n"
        f"  Amount: {amount} TNZO\n"
        f"  Tx hash: {tx_hash}"
    )


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

async def handle_identity(text: str, metadata: dict = None) -> str:
    t = text.lower()
    did = _extract_did(text)

    if did:
        result = await rpc_call("tenzro_resolveIdentity", [did])
        return json.dumps(result, indent=2)

    if "register" in t:
        name = _extract_name(text)
        identity_type = "machine" if "machine" in t else "human"
        result = await rpc_call("tenzro_registerIdentity", [identity_type, name])
        return (
            f"Identity registered:\n"
            f"  DID: {result.get('did', 'unknown')}\n"
            f"  Type: {identity_type}\n"
            f"  Status: {result.get('status', 'active')}"
        )

    if "username" in t:
        if "set" in t:
            words = text.strip().split()
            username = words[-1].rstrip("?.!,;") if len(words) > 2 else None
            if username:
                result = await rpc_call("tenzro_setUsername", [username])
                return f"Username set: {username}\n{json.dumps(result, indent=2)}"
            return "Provide a username to set. Example: 'Set my username to alice'"
        words = text.strip().split()
        username = words[-1].rstrip("?.!,;")
        result = await rpc_call("tenzro_resolveUsername", [username])
        return json.dumps(result, indent=2)

    return (
        "Identity operations:\n"
        "  - 'Register a new human identity named Alice'\n"
        "  - 'Resolve DID did:tenzro:human:abc123'\n"
        "  - 'Set my username to alice'\n"
        "  - 'Resolve username bob'"
    )


# ---------------------------------------------------------------------------
# AI Inference
# ---------------------------------------------------------------------------

async def handle_inference(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "list" in t and "model" in t:
        result = await rpc_call("tenzro_listModels", [])
        if not result:
            return "No models currently registered on the network."
        lines = ["Available models:"]
        for m in result:
            lines.append(f"  - {m.get('name', 'unknown')} ({m.get('id', '')})")
        return "\n".join(lines)

    if "chat" in t or "ask" in t or "complete" in t:
        # Extract the prompt after keywords
        prompt = text
        for kw in ["chat", "ask", "complete", "say"]:
            idx = t.find(kw)
            if idx >= 0:
                prompt = text[idx + len(kw):].strip().lstrip(":").strip()
                break
        result = await rpc_call("tenzro_chat", {"model_id": "default", "message": prompt, "max_tokens": 100})
        return json.dumps(result, indent=2)

    if "endpoint" in t:
        result = await rpc_call("tenzro_listModelEndpoints", [])
        return json.dumps(result, indent=2)

    result = await rpc_call("tenzro_listModels", [])
    if not result:
        return "No models currently available. Use 'list models' to check later."
    lines = ["Available models:"]
    for m in result:
        lines.append(
            f"  - {m.get('name', 'unknown')} | "
            f"Category: {m.get('category', 'n/a')} | "
            f"ID: {m.get('id', '')}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Staking & Provider
# ---------------------------------------------------------------------------

async def handle_staking(text: str, metadata: dict = None) -> str:
    t = text.lower()
    addr = _extract_address(text)
    amount = _extract_amount(text)

    if "unstake" in t or "withdraw" in t:
        if addr and amount:
            result = await rpc_call("tenzro_unstake", [addr, str(amount)])
            return f"Unstake initiated: {amount} TNZO from {addr}\n{json.dumps(result, indent=2)}"
        return "To unstake, provide: address and amount.\nExample: 'Unstake 100 TNZO from 0xabc...'"

    if "stake" in t and amount and addr:
        role = "Validator"
        if "model" in t or "provider" in t:
            role = "ModelProvider"
        if "tee" in t:
            role = "TeeProvider"
        result = await rpc_call("tenzro_stake", [addr, str(amount), role])
        return f"Staked {amount} TNZO as {role} from {addr}\n{json.dumps(result, indent=2)}"

    if addr:
        result = await rpc_call("tenzro_getVotingPower", [addr])
        return f"Staking info for {addr}:\n{json.dumps(result, indent=2)}"

    return (
        "Staking operations:\n"
        "  - 'Stake 1000 TNZO from 0xabc... as Validator'\n"
        "  - 'Unstake 500 TNZO from 0xabc...'\n"
        "  - 'Get staking info for 0xabc...'"
    )


async def handle_provider(text: str, metadata: dict = None) -> str:
    t = text.lower()
    addr = _extract_address(text)

    if "register" in t and addr:
        result = await rpc_call("tenzro_registerProvider", [addr])
        return f"Provider registered: {addr}\n{json.dumps(result, indent=2)}"

    if ("status" in t or "stats" in t) and addr:
        result = await rpc_call("tenzro_providerStats", [addr])
        return f"Provider stats for {addr}:\n{json.dumps(result, indent=2)}"

    return (
        "Provider operations:\n"
        "  - 'Register as provider with address 0xabc...'\n"
        "  - 'Get provider status for 0xabc...'"
    )


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

async def handle_payment(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "session" in t:
        result = await rpc_call("tenzro_listPaymentSessions", [])
        return f"Payment sessions:\n{json.dumps(result, indent=2)}"

    if "info" in t or "gateway" in t:
        result = await rpc_call("tenzro_paymentGatewayInfo", [])
        return f"Payment gateway info:\n{json.dumps(result, indent=2)}"

    if "challenge" in t:
        protocol = "mpp"
        if "x402" in t:
            protocol = "x402"
        result = await rpc_call("tenzro_createPaymentChallenge", [protocol, "/api/resource"])
        return f"Payment challenge created ({protocol}):\n{json.dumps(result, indent=2)}"

    if "ap2" in t:
        amount = _extract_amount(text)
        if "create" in t and amount:
            return (
                f"To create an AP2 payment for {amount} TNZO, provide:\n"
                f"  - Payer DID\n"
                f"  - Payee DID\n"
                f"  - Amount: {amount} TNZO\n"
                f"Use JSON format for full AP2 payment creation."
            )
        if "authorize" in t:
            return (
                "AP2 authorization requires:\n"
                "  - Agent DID\n"
                "  - Spending limit (TNZO)\n"
                "  - Time window (seconds)"
            )
        if "status" in t:
            pay_id = _extract_id(text)
            if pay_id:
                return f"AP2 payment status lookup for {pay_id} -- use tenzro_getSettlement RPC."
            return "Provide a payment ID to check status."
        if "cancel" in t:
            pay_id = _extract_id(text)
            if pay_id:
                return f"AP2 payment cancellation for {pay_id} -- submit cancel via settlement RPC."
            return "Provide a payment ID to cancel."
        if "execute" in t:
            pay_id = _extract_id(text)
            if pay_id:
                return f"AP2 payment execution for {pay_id} -- submit via settlement RPC."
            return "Provide a payment ID to execute."

    if "mpp" in t:
        result = await rpc_call("tenzro_createPaymentChallenge", ["mpp", "/api/resource"])
        return f"MPP challenge:\n{json.dumps(result, indent=2)}"

    if "x402" in t:
        result = await rpc_call("tenzro_createPaymentChallenge", ["x402", "/api/resource"])
        return f"x402 challenge:\n{json.dumps(result, indent=2)}"

    return (
        "Payment operations:\n"
        "  - 'Create MPP payment challenge'\n"
        "  - 'Create x402 payment challenge'\n"
        "  - 'List payment sessions'\n"
        "  - 'AP2 create payment for 100 TNZO'\n"
        "  - 'Payment gateway info'"
    )


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

async def handle_verification(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "tee" in t or "attestation" in t:
        result = await api_call("/api/verify/tee-attestation", method="POST", body={
            "provider": "simulation",
            "quote": "test",
        })
        return f"TEE attestation verification:\n{json.dumps(result, indent=2)}"

    if "transaction" in t or "signature" in t:
        tx_hash = _extract_address(text)
        if tx_hash:
            result = await api_call("/api/verify/transaction", method="POST", body={
                "tx_hash": tx_hash,
            })
            return f"Transaction verification:\n{json.dumps(result, indent=2)}"
        return "Provide a transaction hash to verify its signature."

    if "zk" in t or "proof" in t:
        result = await api_call("/api/verify/zk-proof", method="POST", body={
            "proof_type": "groth16",
            "proof": "test",
            "public_inputs": [],
        })
        return f"ZK proof verification:\n{json.dumps(result, indent=2)}"

    return (
        "Verification operations:\n"
        "  - 'Verify a ZK proof'\n"
        "  - 'Check TEE attestation'\n"
        "  - 'Verify transaction signature for 0xabc...'"
    )


# ---------------------------------------------------------------------------
# Bridge
# ---------------------------------------------------------------------------

async def handle_bridge(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "route" in t:
        return (
            "To get bridge routes, specify source and destination chains.\n"
            "Example: 'Get bridge routes from Tenzro to Ethereum'\n"
            "Supported chains: Ethereum, Solana, Base, Arbitrum, Optimism, Polygon, BSC, Avalanche"
        )

    if "adapter" in t or "list" in t:
        return (
            "Available bridge adapters:\n"
            "  - LayerZero V2 (omnichain messaging + OFT)\n"
            "  - Chainlink CCIP v1.6 (cross-chain messaging)\n"
            "  - deBridge DLN (intent-based swaps)\n"
            "  - LI.FI Aggregator (58+ chains)\n"
            "  - Canton (DAML enterprise)"
        )

    if "fee" in t or "estimate" in t:
        return (
            "To estimate bridge fees, provide:\n"
            "  - Source chain\n"
            "  - Destination chain\n"
            "  - Token and amount\n"
            "Example: 'Estimate bridge fee for 500 USDC from Ethereum to Arbitrum'"
        )

    amount = _extract_amount(text)
    if amount:
        return (
            f"To bridge {amount} tokens, provide:\n"
            f"  - Source chain\n"
            f"  - Destination chain\n"
            f"  - Token symbol\n"
            f"  - Sender and recipient addresses\n"
            f"Use the MCP server at mcp.tenzro.network/mcp for programmatic bridging."
        )

    return (
        "Cross-chain bridge operations:\n"
        "  - 'Bridge 100 TNZO from Ethereum to Solana'\n"
        "  - 'Get bridge routes from Tenzro to Base'\n"
        "  - 'Estimate bridge fee for 500 USDC to Arbitrum'\n"
        "  - 'List available bridge adapters'\n"
        "Supported: LayerZero, CCIP, deBridge, LI.FI, Canton"
    )


# ---------------------------------------------------------------------------
# Join / Onboarding
# ---------------------------------------------------------------------------

async def handle_join(text: str, metadata: dict = None) -> str:
    name = _extract_name(text)
    if name.lower() in ("network", "tenzro", "micronode", "join", "node"):
        name = "Anonymous"

    result = await rpc_call("tenzro_participate", [name])

    did = result.get("did", "unknown")
    address = result.get("address", "unknown")
    capabilities = result.get("capabilities", [])

    cap_lines = "\n".join(f"    - {c}" for c in capabilities) if capabilities else "    (default capabilities)"

    return (
        f"Welcome to the Tenzro Network!\n"
        f"\n"
        f"  Name: {name}\n"
        f"  DID: {did}\n"
        f"  Wallet: {address}\n"
        f"  Capabilities:\n"
        f"{cap_lines}\n"
        f"\n"
        f"Your identity and MPC wallet have been provisioned.\n"
        f"Use 'faucet' to request testnet TNZO tokens."
    )


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------

async def handle_list_tokens(text: str, metadata: dict = None) -> str:
    result = await rpc_call("tenzro_listTokens", [])
    if not result:
        return "No tokens registered in the unified token registry."
    tokens = result.get("tokens", result) if isinstance(result, dict) else result
    if not tokens:
        return "No tokens registered in the unified token registry."
    lines = [f"Registered tokens ({len(tokens)}):"]
    for tok in tokens:
        lines.append(
            f"  - {tok.get('symbol', '?')} ({tok.get('name', '?')}) | "
            f"VM: {tok.get('vm_type', 'all')} | "
            f"ID: {tok.get('token_id', '')}"
        )
    return "\n".join(lines)


async def handle_create_token(text: str, metadata: dict = None) -> str:
    # Try to extract token details from text
    # Pattern: "Create token MyToken (MTK) with 1000000 supply"
    name_match = re.search(r"(?:called|named|token)\s+(\w+)", text, re.IGNORECASE)
    symbol_match = re.search(r"\((\w{2,6})\)", text)
    supply = _extract_amount(text)

    if name_match and symbol_match and supply:
        name = name_match.group(1)
        symbol = symbol_match.group(1)
        result = await rpc_call("tenzro_createToken", [name, symbol, str(int(supply)), "18"])
        return f"Token created:\n{json.dumps(result, indent=2)}"

    return (
        "To create a token, provide:\n"
        "  - Name, symbol, total supply, decimals\n"
        "Example: 'Create a token called MyToken (MTK) with 1000000 supply'\n"
        "Default decimals: 18"
    )


async def handle_token_info(text: str, metadata: dict = None) -> str:
    # Extract symbol or address
    addr = _extract_address(text)
    if addr:
        result = await rpc_call("tenzro_getToken", [addr])
        return json.dumps(result, indent=2)

    words = text.strip().split()
    symbol = words[-1].rstrip("?.!,;").upper() if words else None
    if symbol and len(symbol) <= 10:
        result = await rpc_call("tenzro_getToken", [symbol])
        return json.dumps(result, indent=2)

    return "Provide a token symbol or address.\nExample: 'Get token info for TNZO'"


async def handle_token_balance(text: str, metadata: dict = None) -> str:
    addr = _extract_address(text)
    if addr:
        result = await rpc_call("tenzro_getTokenBalance", [addr])
        return f"Token balance for {addr}:\n{json.dumps(result, indent=2)}"
    return "Provide an address to check token balance.\nExample: 'Get token balance for 0xabc...'"


async def handle_cross_vm_transfer(text: str, metadata: dict = None) -> str:
    return (
        "Cross-VM token transfer requires:\n"
        "  - Token symbol or ID\n"
        "  - Source VM (evm, svm, daml)\n"
        "  - Target VM (evm, svm, daml)\n"
        "  - Amount\n"
        "  - Sender address\n"
        "Example: 'Transfer 100 TNZO from EVM to SVM for 0xabc...'\n"
        "Note: TNZO uses the pointer model (no bridge risk)."
    )


async def handle_wrap_tnzo(text: str, metadata: dict = None) -> str:
    addr = _extract_address(text)
    amount = _extract_amount(text)
    if addr and amount:
        vm = "evm"
        if "svm" in text.lower() or "solana" in text.lower():
            vm = "svm"
        elif "daml" in text.lower() or "canton" in text.lower():
            vm = "daml"
        result = await rpc_call("tenzro_wrapTnzo", [addr, str(amount), vm])
        return f"Wrap TNZO:\n{json.dumps(result, indent=2)}"
    return (
        "To wrap TNZO for a specific VM:\n"
        "  - Provide address, amount, and target VM\n"
        "Example: 'Wrap 50 TNZO for EVM from 0xabc...'\n"
        "Note: In the pointer model, wrapping is a no-op (balances are unified)."
    )


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------

async def handle_contract(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "vm" in t or "supported" in t:
        return (
            "Supported VMs for contract deployment:\n"
            "  - EVM (Ethereum Virtual Machine) -- Solidity bytecode\n"
            "  - SVM (Solana Virtual Machine) -- BPF programs\n"
            "  - DAML (Canton) -- DAML templates via DAR upload"
        )

    bytecode = _extract_address(text)  # bytecodes start with 0x too
    if bytecode and len(bytecode) > 42:  # longer than an address
        vm_type = "evm"
        if "svm" in t or "solana" in t:
            vm_type = "svm"
        elif "daml" in t or "canton" in t:
            vm_type = "daml"
        result = await rpc_call("tenzro_deployContract", [vm_type, bytecode])
        return f"Contract deployed:\n{json.dumps(result, indent=2)}"

    return (
        "To deploy a smart contract, provide:\n"
        "  - VM type: evm, svm, or daml\n"
        "  - Bytecode (hex-encoded, starting with 0x)\n"
        "  - Constructor arguments (optional)\n"
        "Example: 'Deploy an EVM contract with bytecode 0x6080604052...'"
    )


# ---------------------------------------------------------------------------
# NFT
# ---------------------------------------------------------------------------

async def handle_nft(text: str, metadata: dict = None) -> str:
    t = text.lower()
    addr = _extract_address(text)

    if "create" in t or "collection" in t:
        return (
            "To create an NFT collection, provide:\n"
            "  - Collection name\n"
            "  - Symbol\n"
            "  - Standard (ERC-721 or ERC-1155)\n"
            "  - Base URI for metadata\n"
            "This will deploy an NFT contract via the multi-VM runtime."
        )

    if "mint" in t:
        if addr:
            return (
                f"To mint an NFT in collection {addr}, provide:\n"
                f"  - Token URI or metadata\n"
                f"  - Recipient address\n"
                f"  - Token ID (for ERC-1155)"
            )
        return "Provide the collection address to mint. Example: 'Mint an NFT in collection 0xabc...'"

    if "transfer" in t:
        return (
            "To transfer an NFT, provide:\n"
            "  - Collection address\n"
            "  - Token ID\n"
            "  - Recipient address"
        )

    if "owner" in t or "query" in t:
        return (
            "To query NFT ownership, provide:\n"
            "  - Collection address\n"
            "  - Token ID"
        )

    return (
        "NFT operations:\n"
        "  - 'Create a new ERC-721 NFT collection'\n"
        "  - 'Mint an NFT in collection 0xabc...'\n"
        "  - 'Transfer NFT #42 to 0xdef...'\n"
        "  - 'Query ownership of NFT #7'"
    )


# ---------------------------------------------------------------------------
# Compliance
# ---------------------------------------------------------------------------

async def handle_compliance(text: str, metadata: dict = None) -> str:
    t = text.lower()
    addr = _extract_address(text)

    if "kyc" in t and addr:
        return (
            f"KYC verification for {addr}:\n"
            f"  Use tenzro_resolveIdentity to check KYC tier.\n"
            f"  KYC tiers: Unverified (0), Basic (1), Enhanced (2), Full (3)"
        )

    if "accredit" in t and addr:
        return (
            f"Accreditation check for {addr}:\n"
            f"  Query the identity registry for credential type 'AccreditedInvestor'."
        )

    if "country" in t or "restrict" in t:
        return (
            "Country restrictions are managed per-token via the T-REX identity registry.\n"
            "  Provide a token symbol to query restrictions."
        )

    if "freeze" in t and addr:
        return (
            f"To freeze token holdings for {addr}:\n"
            f"  This requires compliance officer role and T-REX token contract interaction."
        )

    if "issuer" in t:
        return (
            "Trusted issuer management:\n"
            "  - Add a trusted issuer with their DID and claim topics\n"
            "  - Remove a trusted issuer by DID\n"
            "  - List all trusted issuers for a token"
        )

    return (
        "Compliance & KYC operations (ERC-3643 T-REX):\n"
        "  - 'Verify KYC status for 0xabc...'\n"
        "  - 'Check accreditation for 0xdef...'\n"
        "  - 'List country restrictions for token XYZ'\n"
        "  - 'Freeze token holdings for 0x123...'\n"
        "  - 'Add a trusted issuer to the registry'"
    )


# ---------------------------------------------------------------------------
# Cross-Chain Token Standard (ERC-7802)
# ---------------------------------------------------------------------------

async def handle_crosschain(text: str, metadata: dict = None) -> str:
    t = text.lower()
    addr = _extract_address(text)

    if "authorize" in t and addr:
        return (
            f"To authorize bridge {addr} for cross-chain minting:\n"
            f"  Submit an ERC-7802 authorizeBridge transaction with the bridge address.\n"
            f"  This grants mint/burn rights on the target chain."
        )

    if "rate limit" in t:
        return (
            "To set a cross-chain rate limit:\n"
            "  Provide bridge address, token, and limit (tokens/day).\n"
            "  Example: 'Set rate limit for bridge 0xabc... to 10000 TNZO/day'"
        )

    if "audit" in t or "trail" in t:
        return (
            "Cross-chain audit trail:\n"
            "  Query ERC-7802 CrossChainMint and CrossChainBurn events.\n"
            "  Provide a token address or bridge address to filter."
        )

    if "revoke" in t and addr:
        return (
            f"To revoke bridge authorization for {addr}:\n"
            f"  Submit an ERC-7802 revokeBridge transaction."
        )

    return (
        "ERC-7802 Cross-Chain Token Standard:\n"
        "  - 'Authorize a bridge for cross-chain minting'\n"
        "  - 'Set rate limit for bridge 0xabc... to 10000 TNZO/day'\n"
        "  - 'Query audit trail for cross-chain transfers'\n"
        "  - 'Revoke bridge authorization for 0xdef...'"
    )


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

async def handle_events(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "websocket" in t or "subscribe" in t:
        return (
            "WebSocket event streaming:\n"
            "  Connect to ws://rpc.tenzro.network and call eth_subscribe.\n"
            "  Supported subscriptions:\n"
            "    - newHeads (new blocks)\n"
            "    - logs (contract events, with optional address/topics filter)\n"
            "    - pendingTransactions"
        )

    if "webhook" in t:
        return (
            "Webhook registration:\n"
            "  Provide a callback URL, event filter, and optional contract address.\n"
            "  Webhooks are signed with HMAC-SHA256 for verification.\n"
            "  Example: 'Register webhook at https://myapp.com/hook for transfers on 0xabc...'"
        )

    if "histor" in t or "query" in t:
        addr = _extract_address(text)
        if addr:
            return (
                f"To query historical events for {addr}:\n"
                f"  Use eth_getLogs with the contract address and block range."
            )
        return "Provide a contract address to query historical events."

    return (
        "Event streaming options:\n"
        "  - 'Subscribe to new block events via WebSocket'\n"
        "  - 'Register a webhook for transfer events'\n"
        "  - 'Query historical events for contract 0xabc...'\n"
        "  - 'Stream pending transactions in real time'"
    )


# ---------------------------------------------------------------------------
# Canton / DAML
# ---------------------------------------------------------------------------

async def handle_canton(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "domain" in t:
        result = await rpc_call("tenzro_listCantonDomains", [])
        return f"Canton domains:\n{json.dumps(result, indent=2)}"

    if "contract" in t:
        result = await rpc_call("tenzro_listDamlContracts", [])
        return f"DAML contracts:\n{json.dumps(result, indent=2)}"

    if "submit" in t or "command" in t:
        return (
            "To submit a DAML command, provide:\n"
            "  - Command type: create or exercise\n"
            "  - Template ID (for create)\n"
            "  - Contract ID (for exercise)\n"
            "  - Payload (JSON)\n"
            "Use the Canton MCP server at canton-mcp.tenzro.network/mcp for full access."
        )

    return (
        "Canton / DAML operations:\n"
        "  - 'List Canton domains'\n"
        "  - 'List DAML contracts'\n"
        "  - 'Submit a DAML command'"
    )


# ---------------------------------------------------------------------------
# Task Marketplace
# ---------------------------------------------------------------------------

async def handle_task_marketplace(text: str, metadata: dict = None) -> str:
    t = text.lower()
    task_id = _extract_id(text)

    if "post" in t or "create" in t:
        amount = _extract_amount(text)
        return (
            "To post a task to the marketplace, provide:\n"
            f"  - Description of the task\n"
            f"  - Budget: {amount or '?'} TNZO\n"
            f"  - Category (inference, code-review, data-analysis, etc.)\n"
            f"  - Deadline (optional)\n"
            "The budget is held in escrow until task completion."
        )

    if "cancel" in t and task_id:
        result = await rpc_call("tenzro_cancelTask", [task_id])
        return f"Task canceled: {task_id}\n{json.dumps(result, indent=2)}"

    if "quote" in t and task_id:
        amount = _extract_amount(text)
        if amount:
            result = await rpc_call("tenzro_quoteTask", [task_id, str(amount)])
            return f"Quote submitted for task {task_id}: {amount} TNZO\n{json.dumps(result, indent=2)}"
        return f"Provide a quote amount for task {task_id}.\nExample: 'Submit a quote of 50 TNZO for task {task_id}'"

    if task_id:
        result = await rpc_call("tenzro_getTask", [task_id])
        return f"Task details:\n{json.dumps(result, indent=2)}"

    # Default: list tasks
    result = await rpc_call("tenzro_listTasks", [])
    if not result:
        return "No tasks currently listed on the marketplace."
    lines = ["Task marketplace:"]
    for task in result:
        lines.append(
            f"  - [{task.get('status', '?')}] {task.get('title', 'Untitled')} | "
            f"Budget: {task.get('budget', '?')} TNZO | "
            f"ID: {task.get('id', '')}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Agent Marketplace
# ---------------------------------------------------------------------------

async def handle_agent_marketplace(text: str, metadata: dict = None) -> str:
    t = text.lower()
    template_id = _extract_id(text)

    if "register" in t or "publish" in t:
        return (
            "To register an agent template, provide:\n"
            "  - Name\n"
            "  - Description\n"
            "  - Capabilities (list)\n"
            "  - Pricing model (per-task, per-hour, subscription)\n"
            "  - Agent type (autonomous, semi-autonomous, tool)"
        )

    if "rate" in t and template_id:
        # Try to extract rating
        rating_match = re.search(r"(\d)\s*star", text)
        rating = int(rating_match.group(1)) if rating_match else None
        if rating:
            return f"Rating {rating} stars submitted for template {template_id}."
        return f"Provide a star rating (1-5) for template {template_id}."

    if "spawn" in t and template_id:
        return (
            f"To spawn an agent from template {template_id}:\n"
            f"  This will create a new agent instance with its own DID and wallet.\n"
            f"  The agent inherits all capabilities defined in the template."
        )

    if "stats" in t and template_id:
        result = await rpc_call("tenzro_getAgentTemplate", [template_id])
        return f"Template stats:\n{json.dumps(result, indent=2)}"

    if template_id:
        result = await rpc_call("tenzro_getAgentTemplate", [template_id])
        return f"Agent template:\n{json.dumps(result, indent=2)}"

    if "search" in t:
        query = text.split("search")[-1].strip().rstrip("?.!,;") if "search" in t else ""
        result = await rpc_call("tenzro_listAgentTemplates", [])
        if not result:
            return "No agent templates found."
        lines = [f"Agent templates matching '{query}':"] if query else ["Available agent templates:"]
        for tmpl in result:
            lines.append(
                f"  - {tmpl.get('name', 'Unnamed')} | "
                f"Type: {tmpl.get('agent_type', '?')} | "
                f"ID: {tmpl.get('id', '')}"
            )
        return "\n".join(lines)

    # Default: list
    result = await rpc_call("tenzro_listAgentTemplates", [])
    if not result:
        return "No agent templates registered on the marketplace."
    lines = ["Available agent templates:"]
    for tmpl in result:
        lines.append(
            f"  - {tmpl.get('name', 'Unnamed')} | "
            f"Type: {tmpl.get('agent_type', '?')} | "
            f"ID: {tmpl.get('id', '')}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Agent Spawning
# ---------------------------------------------------------------------------

async def handle_agent_spawning(text: str, metadata: dict = None) -> str:
    t = text.lower()

    if "list" in t and ("child" in t or "agent" in t):
        result = await rpc_call("tenzro_listAgentTemplates", [])
        return f"Spawned agents:\n{json.dumps(result, indent=2)}"

    if "spawn" in t:
        # Try to extract agent name
        name_match = re.search(r"(?:named?|called)\s+['\"]?(\w+)['\"]?", text, re.IGNORECASE)
        name = name_match.group(1) if name_match else "sub-agent"
        # Try to extract capabilities
        cap_match = re.search(r"(?:with|capability|capabilities)\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        capabilities = cap_match.group(1).strip().rstrip("?.!,;") if cap_match else "general"

        return (
            f"Agent spawn request:\n"
            f"  Name: {name}\n"
            f"  Capabilities: {capabilities}\n"
            f"\n"
            f"Each spawned agent receives:\n"
            f"  - Its own TDIP DID (did:tenzro:machine:...)\n"
            f"  - MPC wallet (2-of-3 threshold)\n"
            f"  - Delegation scope from parent\n"
            f"  - Max 50 child agents per parent\n"
            f"\n"
            f"Use the A2A protocol or tenzro_registerAgent RPC for programmatic spawning."
        )

    if "run" in t or "task" in t:
        return (
            "To run an autonomous agent task:\n"
            "  - Spawn or select an agent\n"
            "  - Submit a task description\n"
            "  - The agent executes autonomously within its delegation scope\n"
            "  - Results are returned via A2A protocol"
        )

    return (
        "Agent spawning operations:\n"
        "  - 'Spawn a sub-agent with coding capabilities'\n"
        "  - 'Spawn an agent named researcher with web-search capability'\n"
        "  - 'List my child agents'\n"
        "  - 'Run an autonomous agent task'"
    )


# ---------------------------------------------------------------------------
# Swarm Orchestration
# ---------------------------------------------------------------------------

async def handle_swarm(text: str, metadata: dict = None) -> str:
    t = text.lower()
    swarm_id = _extract_id(text)

    if "create" in t:
        count_match = re.search(r"(\d+)\s*(?:agent|member|worker)", text)
        count = int(count_match.group(1)) if count_match else 3
        return (
            f"Swarm creation request:\n"
            f"  Members: {count}\n"
            f"\n"
            f"Each swarm member gets its own DID and wallet.\n"
            f"The orchestrator can broadcast tasks to all members simultaneously.\n"
            f"Use tenzro_createSwarm RPC for programmatic creation."
        )

    if "status" in t and swarm_id:
        return (
            f"To get swarm status for {swarm_id}:\n"
            f"  Use tenzro_getSwarm RPC with the swarm ID."
        )

    if "terminat" in t and swarm_id:
        return (
            f"To terminate swarm {swarm_id}:\n"
            f"  Use tenzro_terminateSwarm RPC. This will:\n"
            f"  - Stop all member agents\n"
            f"  - Settle any pending payments\n"
            f"  - Archive the swarm state"
        )

    if "broadcast" in t:
        return (
            "To broadcast a task to all swarm members:\n"
            "  Provide the swarm ID and task description.\n"
            "  All members execute in parallel; results are aggregated."
        )

    return (
        "Swarm orchestration:\n"
        "  - 'Create a swarm with 3 research agents'\n"
        "  - 'Get swarm status for swarm-id-123'\n"
        "  - 'Terminate swarm swarm-id-456'\n"
        "  - 'Broadcast a task to my swarm'"
    )


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

async def handle_help(text: str, metadata: dict = None) -> str:
    return (
        "Tenzro Network Agent -- 19 skills available:\n"
        "\n"
        "  Blockchain:\n"
        "    wallet     - Create wallets, check balances, send TNZO\n"
        "    identity   - Register/resolve DIDs, manage usernames\n"
        "    staking    - Stake TNZO, manage validators/providers\n"
        "    token      - Create ERC-20 tokens, cross-VM transfers\n"
        "    contract   - Deploy smart contracts (EVM/SVM/DAML)\n"
        "    nft        - NFT collections (ERC-721/1155)\n"
        "    bridge     - Cross-chain via LayerZero/CCIP/deBridge\n"
        "\n"
        "  AI & Agents:\n"
        "    inference   - Route AI inference requests\n"
        "    task_marketplace - Post/browse AI tasks with escrow\n"
        "    agent_marketplace - Discover/spawn agent templates\n"
        "    agent_spawning - Spawn autonomous sub-agents\n"
        "    swarm       - Orchestrate agent swarms\n"
        "\n"
        "  Payments & Settlement:\n"
        "    settlement  - Micropayment channels, escrow\n"
        "    ap2-payments - Agent-to-agent payments\n"
        "    payment     - MPP/x402 payment challenges\n"
        "\n"
        "  Security & Compliance:\n"
        "    verification - ZK proofs, TEE attestations\n"
        "    compliance   - ERC-3643 T-REX KYC\n"
        "    crosschain   - ERC-7802 cross-chain tokens\n"
        "\n"
        "  Infrastructure:\n"
        "    join    - Join as MicroNode (zero-install onboarding)\n"
        "    events  - WebSocket/webhook event streaming\n"
        "\n"
        "Try: 'Check my TNZO balance for 0xabc...'\n"
        "     'Join the Tenzro Network as Alice'\n"
        "     'List available AI models'"
    )


# ---------------------------------------------------------------------------
# Handler dispatch table
# ---------------------------------------------------------------------------

HANDLERS: dict[str, callable] = {
    "wallet": handle_wallet,
    "block": handle_block,
    "status": handle_status,
    "network": handle_network,
    "faucet": handle_faucet,
    "identity": handle_identity,
    "inference": handle_inference,
    "staking": handle_staking,
    "provider": handle_provider,
    "payment": handle_payment,
    "verification": handle_verification,
    "bridge": handle_bridge,
    "join": handle_join,
    "list_tokens": handle_list_tokens,
    "create_token": handle_create_token,
    "token_info": handle_token_info,
    "token_balance": handle_token_balance,
    "cross_vm_transfer": handle_cross_vm_transfer,
    "wrap_tnzo": handle_wrap_tnzo,
    "contract": handle_contract,
    "nft": handle_nft,
    "compliance": handle_compliance,
    "crosschain": handle_crosschain,
    "events": handle_events,
    "canton": handle_canton,
    "task_marketplace": handle_task_marketplace,
    "agent_marketplace": handle_agent_marketplace,
    "agent_spawning": handle_agent_spawning,
    "swarm_orchestration": handle_swarm,
    "help": handle_help,
}
