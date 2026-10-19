# Technical Documentation: Autonomous Agent Wallet & Risk Control Plane

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
