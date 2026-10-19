# Autonomous Agent Wallet & Risk Control Plane (Topic F)

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
