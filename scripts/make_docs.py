from pathlib import Path

README_TEXT = """# Autonomous Agent Wallet & Risk Control Plane (Topic F)

Competition: 2026 Shenzhen International FinTech Competition (FinTechathon) - International Track
Topic: Topic F - Agent Wallet (Autonomous On-chain Wallet)
Repository: https://github.com/Crux-15/agent-wallet

## 1. Project Overview
This project implements an autonomous AI financial participant for Ethereum wallet management, transaction execution, and deterministic risk control. It separates conversational intent parsing (powered by Google Gemini with a deterministic local fallback router) from financial execution via a strict ToolExecutor and PolicyEngine control plane.

### Core Capabilities
- Autonomous Treasury & Portfolio Management: Real-time tracking of total ETH balance, locked treasury reserve floor (0.002 ETH), spendable liquidity, rolling 24-hour spending caps, and live network gas prices in Gwei.
- Quantitative Risk Scoring (0 to 100): Evaluates every proposed transfer across recipient allowlist status, transaction size relative to caps, 24-hour cumulative velocity, and gas fee conditions.
- Preflight Dry-Run Simulation: Simulates transactions before execution to compute risk scores, projected post-transfer balances, and estimated gas costs without moving funds.
- Three-Tier Permission Governance: Supports Tier 0 (Read-Only), Tier 1 (Approve Everything), and Tier 2 (Limited Auto) with human-in-the-loop supervisor approval for medium transfers (> 0.002 ETH).
- Batch Settlement: Executes multi-recipient disbursements while enforcing policy checks on each individual transfer.
- Dual Execution Adapters: Identical interface (ExecutionAdapter) for instant in-memory testing (MockAdapter) and live Ethereum Sepolia blockchain execution (ChainAdapter).

## 2. On-Chain Execution Evidence (Ethereum Sepolia Testnet)
Note: The FinTechathon Organizing Committee officially confirmed via email that Ethereum Sepolia testnet transaction hashes are accepted as real on-chain execution evidence for Topic F.

- Approved Recipient Address: 0x78964c29614bF783c3339cd7b553C8627168554E

| # | Timestamp | Operation | Amount | Risk Score | Policy Decision | Sepolia Transaction Hash & Etherscan Link |
|---|---|---|---|---|---|---|
| 1 | 2026-10-19 22:44:00 | Autonomous Small Transfer | 0.0005 ETH | 1/100 (LOW) | allow (Auto-executed in Tier 2) | [0xd03fff8dc8ba123539f97cab7dd456c9487535c446df01674aee8cee6524a0a4](https://sepolia.etherscan.io/tx/0xd03fff8dc8ba123539f97cab7dd456c9487535c446df01674aee8cee6524a0a4) |
| 2 | 2026-10-19 22:44:38 | Supervisor-Approved Transfer | 0.0022 ETH | 21/100 (MEDIUM) | needs_approval -> Human Approved | [0xbde5dd8c3f4e0ffdd0afae4ae95ae29e58f183618a17314e07495a323ac17cc0](https://sepolia.etherscan.io/tx/0xbde5dd8c3f4e0ffdd0afae4ae95ae29e58f183618a17314e07495a323ac17cc0) |

Supporting artifacts inside the evidence/ and logs/ directories:
- evidence/sepolia_tx_list.txt - Extracted Sepolia transaction log table.
- evidence/chain_demo_output.txt - Full terminal transcript of live Sepolia execution and attack blocking.
- evidence/tier_demo_output.txt - Verification of Tier 0, Tier 1, and Tier 2 governance behavior.
- evidence/tx1.png & evidence/tx2.png - Etherscan confirmation screenshots.
- evidence/dashboard.png - Streamlit Web Control Center screenshot connected to Sepolia.
- logs/audit.jsonl - Structured JSON Lines audit trail of all tool calls, policy decisions, human approvals, and results.

## 3. How Judges Can Run & Test the Project
1. Clone repository: `git clone https://github.com/Crux-15/agent-wallet.git && cd agent-wallet`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the 50 automated unit tests (no API keys required): `python -m pytest -q`
4. Launch the interactive Web Control Center: `streamlit run app.py`
5. Launch the terminal CLI agent: `python agent.py`
"""

TECH_DOC_TEXT = """# Technical Documentation: Autonomous Agent Wallet & Risk Control Plane

Competition: 2026 Shenzhen International FinTech Competition (FinTechathon) - International Track
Topic: Topic F - Agent Wallet (Autonomous On-chain Wallet)
Repository: https://github.com/Crux-15/agent-wallet

## 1. System Architecture
The system enforces a strict separation between the Cognitive Plane (LLM intent parsing) and the Execution Plane (deterministic policy verification and cryptographic signing). The AI model never holds private keys, never signs transactions, and cannot override safety limits.

1. User & Supervisor Interface (app.py and agent.py): Provides a Streamlit Web Control Center and CLI interface for natural language interaction, live portfolio telemetry, preflight dry-run simulation, and human-in-the-loop transaction approval.
2. Cognitive Layer (agent.py): Uses Google Gemini function-calling across 6 strictly typed tools (get_balance, get_policy_limits, get_portfolio_status, simulate_transfer, send_eth, batch_send_eth). Includes automatic model failover and a deterministic regex fallback router so operations never fail during API rate limits.
3. Security Guard Layer (executor.py): ToolExecutor intercepts every tool call, injects live network telemetry (gas price in Gwei), queries PolicyEngine.check(), enforces human approval callbacks on medium payments, and logs every event to logs/audit.jsonl.
4. Deterministic Policy Engine (policy.py): Evaluates all transfers using exact decimal.Decimal arithmetic and persists rolling 24-hour spending history to logs/policy_state.json.
5. Execution Adapter Layer (adapters/): Implements ExecutionAdapter (base.py) with two interchangeable implementations: MockAdapter (in-memory sandbox) and ChainAdapter (Ethereum Sepolia via Web3.py using dynamic EIP-1559 gas pricing with a 20% safety buffer).

## 2. Core Algorithms

### 2.1 Ordered Seven-Stage Policy Verification Pipeline
When PolicyEngine.check(args) is called, it runs a fail-closed sequential check:
1. Permission Tier Lock: If tier == READ_ONLY (0), deny immediately.
2. Address Regex & Checksum Validation: Require recipient to match ^0x[0-9a-fA-F]{40}$.
3. Exact Decimal Positivity Check: Parse amount_eth using Decimal; reject NaN, Infinity, or values <= 0.
4. Recipient Allowlist Enforcement: Reject any recipient not present in the configured allowlist.
5. Per-Transaction & Rolling 24-Hour Caps: Reject if amount > 0.01 ETH or if spent_last_24h() + amount > 0.05 ETH.
6. Treasury Reserve Floor & Gas Ceiling Guard: Reject if balance - amount < 0.002 ETH (reserve floor) or if network gas > 50 Gwei (fee spike protection).
7. Human Supervisor Escalation: If tier == APPROVE_ALL (1) or amount > 0.002 ETH, return status='needs_approval'; otherwise return status='allow'.

### 2.2 Quantitative Risk Scoring Algorithm
Every proposed transfer receives a deterministic risk score from 0 to 100:
- Unapproved or invalid recipient address: +60 points
- Transaction size ratio relative to per-tx cap: up to +40 points
- Exceeds automatic approval threshold (0.002 ETH): +15 points
- Breaches 24-hour rolling cap (0.05 ETH): +35 points
- Network gas exceeds 50 Gwei ceiling: +25 points
Scores map to four bands: LOW (0-19), MEDIUM (20-39), HIGH (40-69), and CRITICAL (70-100).

### 2.3 Commit-After-Receipt State Accounting
PolicyEngine.record(amount) is executed ONLY after ChainAdapter.transfer() receives an on-chain transaction receipt with status == 1. Denied, human-rejected, or reverted transactions never consume the user's 24-hour budget.
"""

SECURITY_DOC_TEXT = """# Security Self-Assessment Report

Competition: 2026 Shenzhen International FinTech Competition (FinTechathon) - International Track
Topic: Topic F - Agent Wallet (Autonomous On-chain Wallet)
Repository: https://github.com/Crux-15/agent-wallet

## 1. Permission-Tier Implementation
The wallet implements three permission tiers inside policy.py (PolicyEngine), selectable via environment configuration or live in the Streamlit Control Center sidebar:

| Tier | Mode Name | Autonomous Capabilities | Human Approval Requirement |
|---|---|---|---|
| Tier 0 | READ_ONLY | Balance, portfolio status, policy limits, and dry-run simulation only. | All outgoing transfers are strictly denied (status='deny'). |
| Tier 1 | APPROVE_ALL | Read tools and simulation. | 100% of valid transfers require explicit human approval (status='needs_approval'). |
| Tier 2 | LIMITED_AUTO (Default) | Read tools + auto-execution of allowlisted micro-transfers <= 0.002 ETH. | Transfers > 0.002 ETH and <= 0.01 ETH require human approval; > 0.01 ETH denied. |

Empirical Verification (from evidence/tier_demo_output.txt):
- Tier 0 (read-only): result=denied, human_asked=no, risk=1/100
- Tier 1 (approve everything): result=sent, human_asked=yes, risk=1/100
- Tier 2 (small = automatic): result=sent, human_asked=no, risk=1/100

## 2. Implemented Security Controls
- Privilege Separation: The LLM has zero access to PRIVATE_KEY or Web3 signing objects.
- Self-Approval Immunity: Passing 'approved': True in tool arguments is ignored by ToolExecutor (verified by test_the_model_cannot_approve_itself).
- Persistent 24h Spend Tracking: Spending history is saved to logs/policy_state.json so restarting the process cannot reset daily limits.
- Sanitized Audit Logging: Error handlers log only type(e).__name__ to logs/audit.jsonl so RPC keys and secrets never leak into logs.

## 3. Known-Risk List & Production Remediation Plan
1. Local Console/UI Approval Channel: Approval currently occurs via local terminal input or local Streamlit UI buttons. Production remediation: Replace with cryptographic out-of-band WebAuthn passkeys or hardware wallet signatures.
2. Plaintext .env Key Storage: The testnet private key lives in a git-ignored .env file. Production remediation: Use an HSM, cloud KMS, or ERC-4337 Smart Account session keys.
3. Local JSON State File: A local root user could edit logs/policy_state.json. Production remediation: Enforce rolling spend limits directly on-chain via smart contract modules.
4. Static Allowlist Configuration: Approved recipients are loaded from environment variables. Production remediation: Use an admin-signed on-chain address book with time-locked updates.
5. Testnet-Only Validation: Validated on Ethereum Sepolia testnet (tx hashes 0xd03fff8dc8ba123539f97cab7dd456c9487535c446df01674aee8cee6524a0a4 and 0xbde5dd8c3f4e0ffdd0afae4ae95ae29e58f183618a17314e07495a323ac17cc0). Production remediation: Add Flashbots MEV protection and reorg depth checks for Mainnet.
6. External LLM API Telemetry: Free-tier Gemini API requests send prompt text to Google servers. Production remediation: Use enterprise zero-data-retention endpoints or local open-weights models.
"""

Path("README.md").write_text(README_TEXT.strip() + "\n", encoding="utf-8")
Path("TECHNICAL_DOCUMENTATION.md").write_text(TECH_DOC_TEXT.strip() + "\n", encoding="utf-8")
Path("SECURITY_SELF_ASSESSMENT.md").write_text(SECURITY_DOC_TEXT.strip() + "\n", encoding="utf-8")
print("SUCCESS: Created README.md, TECHNICAL_DOCUMENTATION.md, and SECURITY_SELF_ASSESSMENT.md")