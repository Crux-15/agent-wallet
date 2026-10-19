# Security Self-Assessment Report

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
