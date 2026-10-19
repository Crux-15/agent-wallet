from pathlib import Path
from fpdf import FPDF

OUT_DIR = Path("submission_files")
OUT_DIR.mkdir(exist_ok=True)


class ReportPDF(FPDF):
    def __init__(self, doc_title):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.doc_title = doc_title
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"2026 Shenzhen International FinTech Competition (Topic F) | {self.doc_title}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 16, 200, 16)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(15, 55, 110)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def code_box(self, text):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(242, 244, 248)
        self.set_text_color(10, 10, 10)
        self.multi_cell(0, 4.5, text, border=1, fill=True)
        self.ln(3)


def build_technical_doc():
    pdf = ReportPDF("Technical Documentation")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(10, 35, 80)
    pdf.multi_cell(0, 10, "Technical Documentation: Autonomous Agent Wallet & Deterministic Risk Control Plane")
    pdf.ln(2)
    pdf.body_text(
        "Competition: 2026 Shenzhen International FinTech Competition (FinTechathon) - International Track\n"
        "Topic: Topic F - Agent Wallet (Autonomous On-chain Wallet)\n"
        "GitHub Repository: https://github.com/Crux-15/agent-wallet"
    )

    pdf.chapter_title("1. System Architecture (Control Plane vs. Execution Plane)")
    pdf.body_text(
        "Our architecture enforces a strict privilege boundary between the Cognitive Layer (LLM intent translation) "
        "and the Execution Layer (deterministic policy verification and cryptographic transaction signing). "
        "The AI model never holds private keys, never accesses Web3 signing objects, and cannot bypass safety rules."
    )
    pdf.code_box(
        "[User / Operator UI: Streamlit Web Control Center (app.py) & CLI (agent.py)]\n"
        "       |\n"
        "       v\n"
        "[Cognitive Layer (agent.py): Gemini Function-Calling + Local Regex Fallback Router]\n"
        "       |  (Emits structured requests across 6 whitelisted tools; MAX_ROUNDS = 5)\n"
        "       v\n"
        "[Security Guard Layer (executor.py): ToolExecutor + Human Approval Gate + AuditLog]\n"
        "       |---> 1. Policy Check ---> [PolicyEngine (policy.py): Tiers 0/1/2, Risk Score 0-100]\n"
        "       |---> 2. Execution    ---> [ExecutionAdapter: MockAdapter | ChainAdapter (Sepolia)]"
    )

    pdf.chapter_title("2. Core Algorithm Description")
    pdf.body_text(
        "A. Seven-Stage Fail-Closed Policy Pipeline (policy.py):\n"
        "Every outgoing payment request is evaluated in strict order using exact decimal.Decimal math:\n"
        "1. Tier Lock Check: If tier == READ_ONLY (0), deny immediately.\n"
        "2. Address Validation: Verify recipient matches ^0x[0-9a-fA-F]{40}$ and apply EIP-55 checksum.\n"
        "3. Exact Decimal Positivity: Reject NaN, Infinity, non-numbers, or amounts <= 0.\n"
        "4. Allowlist Enforcement: Verify recipient address is in the approved recipient set.\n"
        "5. Per-Tx & Rolling 24h Caps: Reject if amount > 0.01 ETH or if spent_last_24h() + amount > 0.05 ETH.\n"
        "6. Reserve Floor & Gas Ceiling Guard: Reject if balance - amount < 0.002 ETH or if live gas > 50 Gwei.\n"
        "7. Human Supervisor Escalation: If tier == APPROVE_ALL (1) or amount > 0.002 ETH, require human approval.\n\n"
        "B. Quantitative Risk Scoring Algorithm (0 to 100):\n"
        "Each transaction receives a composite risk score R in [0, 100]: +60 for unapproved/invalid address, "
        "up to +40 scaled by transaction size relative to the 0.01 ETH cap, +15 if above the 0.002 ETH approval threshold, "
        "+35 if breaching the 24h cap, and +25 if network gas exceeds 50 Gwei. Scores map to LOW (0-19), "
        "MEDIUM (20-39), HIGH (40-69), and CRITICAL (70-100).\n\n"
        "C. EIP-1559 Dynamic Gas & Commit-After-Receipt State Accounting:\n"
        "ChainAdapter constructs EIP-1559 transactions with a 20% gas estimate buffer. PolicyEngine.record() is called "
        "ONLY after wait_for_transaction_receipt confirms status == 1 on Ethereum Sepolia, ensuring denied or failed "
        "calls never deplete the daily spending budget."
    )

    pdf.chapter_title("3. Security Design & On-Chain Execution Evidence")
    pdf.body_text(
        "- Prompt Injection Defense: Untrusted prompts claiming 'admin mode' cannot bypass PolicyEngine.check().\n"
        "- Persistent Spend State: Rolling 24h spend records persist to logs/policy_state.json across restarts.\n"
        "- Secret Redaction: AuditLog (logs/audit.jsonl) records only exception class names so RPC keys never leak.\n"
        "- Automated Verification: 50 pytest unit tests passing across adapters, policy, executor, and agent.\n\n"
        "Confirmed Ethereum Sepolia Testnet Transactions (Approved Recipient: 0x78964c29614bF783c3339cd7b553C8627168554E):\n"
        "1. Auto-Executed (0.0005 ETH, Risk 1/100 LOW, 2026-10-19 22:44:00):\n"
        "   Hash: 0xd03fff8dc8ba123539f97cab7dd456c9487535c446df01674aee8cee6524a0a4\n"
        "2. Human-Approved (0.0022 ETH, Risk 21/100 MEDIUM, 2026-10-19 22:44:38):\n"
        "   Hash: 0xbde5dd8c3f4e0ffdd0afae4ae95ae29e58f183618a17314e07495a323ac17cc0"
    )

    out_path = OUT_DIR / "01_Technical_Documentation.pdf"
    pdf.output(str(out_path))
    print("Created:", out_path)


def build_security_doc():
    pdf = ReportPDF("Security Self-Assessment Report")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(10, 35, 80)
    pdf.multi_cell(0, 10, "Security Self-Assessment Report: Permission Tiers & Known-Risk Analysis")
    pdf.ln(2)
    pdf.body_text(
        "Competition: 2026 Shenzhen International FinTech Competition (FinTechathon) - International Track\n"
        "Topic: Topic F - Agent Wallet (Autonomous On-chain Wallet)\n"
        "GitHub Repository: https://github.com/Crux-15/agent-wallet"
    )

    pdf.chapter_title("1. Permission-Tier Implementation")
    pdf.body_text(
        "The PolicyEngine (policy.py) enforces three distinct operational permission tiers, selectable via the "
        "POLICY_TIER environment variable or live in the Streamlit Web Control Center sidebar. All hard limits "
        "(allowlist, 0.01 ETH per-tx cap, 0.05 ETH 24h cap, 0.002 ETH reserve floor, 50 Gwei gas ceiling) apply in all tiers:\n\n"
        "- Tier 0 (READ_ONLY = 0): The agent can execute read-only portfolio, balance, limit, and dry-run simulation "
        "tools. All outgoing transfers (send_eth, batch_send_eth) are immediately denied.\n"
        "- Tier 1 (APPROVE_ALL = 1): Every valid outgoing payment pauses for explicit human supervisor approval "
        "(status = 'needs_approval') regardless of how small the amount is.\n"
        "- Tier 2 (LIMITED_AUTO = 2, Default): Micro-payments <= 0.002 ETH to allowlisted addresses execute autonomously; "
        "medium payments (> 0.002 ETH up to 0.01 ETH) require human supervisor approval."
    )
    pdf.code_box(
        "Empirical Verification Output (evidence/tier_demo_output.txt):\n"
        "Tier 0 (read-only)             result=denied   human_asked=no  risk=1/100\n"
        "Tier 1 (approve everything)    result=sent     human_asked=yes risk=1/100\n"
        "Tier 2 (small = automatic)     result=sent     human_asked=no  risk=1/100"
    )

    pdf.chapter_title("2. Implemented Defense-in-Depth Controls")
    pdf.body_text(
        "1. Complete Key Isolation: The LLM agent has no tool or code path to read PRIVATE_KEY or sign transactions.\n"
        "2. Self-Approval Immunity: Passing 'approved': True inside tool arguments is ignored by ToolExecutor "
        "(verified by unit test test_the_model_cannot_approve_itself).\n"
        "3. Persistent 24-Hour Spend Tracking: Spend history is stored in logs/policy_state.json so restarting the "
        "application cannot reset daily spending limits.\n"
        "4. Sanitized Telemetry: Audit logs (logs/audit.jsonl) record only error class names to prevent secret leakage."
    )

    pdf.chapter_title("3. Known-Risk List & Production Remediation Roadmap")
    pdf.body_text(
        "1. Local Console / Web UI Approval Channel: Human approval currently relies on local terminal input or a local "
        "Streamlit button. Remediation: Use cryptographic out-of-band WebAuthn passkey or hardware wallet signatures.\n\n"
        "2. Plaintext .env Key Storage: The testnet private key sits in a local git-ignored .env file. "
        "Remediation: Migrate key custody to an HSM, cloud KMS, or ERC-4337 Smart Account with scoped session keys.\n\n"
        "3. Local JSON Spend State File: A local user with disk write access could modify logs/policy_state.json. "
        "Remediation: Enforce rolling spend limits directly on-chain via smart contract policy modules.\n\n"
        "4. Static Environment Allowlist: Approved recipient addresses are loaded from .env. "
        "Remediation: Implement an admin-signed on-chain address book registry with time-locked additions.\n\n"
        "5. Testnet-Only Validation: Tested on Ethereum Sepolia testnet. "
        "Remediation: Add Mainnet chain-reorg confirmation depth checks and Flashbots Protect RPC for MEV defense.\n\n"
        "6. External Cloud LLM API: Free-tier Gemini API calls transmit prompts to Google servers. "
        "Remediation: Use enterprise zero-data-retention endpoints or locally hosted open-weights models."
    )

    out_path = OUT_DIR / "05_Security_Self_Assessment_Report.pdf"
    pdf.output(str(out_path))
    print("Created:", out_path)


def build_slides():
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    slides = [
        (
            "Autonomous Agent Wallet & Risk Control Plane",
            "2026 Shenzhen International FinTech Competition (FinTechathon) - Topic F",
            [
                "Theme: AI as a Financial Participant (Autonomous On-Chain Wallet)",
                "Core Thesis: Pair AI conversational planning with deterministic financial guardrails",
                "Public Repository: https://github.com/Crux-15/agent-wallet",
                "Verification: 50 Automated Pytest Unit Tests + Live Ethereum Sepolia Execution",
            ],
        ),
        (
            "1. The Problem: Why Naive AI Crypto Wallets Fail",
            "Unbounded LLM agency creates unacceptable financial and security exposure",
            [
                "Prompt Injection: Malicious text can trick an LLM into draining wallet funds",
                "Hallucinated Parameters: LLMs can miscalculate decimals, addresses, or gas fees",
                "No Velocity Controls: Repeated small transfers can bypass single-payment checks",
                "Solution: Strict separation between Cognitive Plane (AI) and Execution Plane (Policy + Keys)",
            ],
        ),
        (
            "2. System Architecture: Control Plane vs. Execution Plane",
            "Defense-in-depth across four modular software layers",
            [
                "1. UI & Supervisor Layer: Streamlit Web Control Center (app.py) & CLI (agent.py)",
                "2. Cognitive Layer (agent.py): Gemini function-calling + deterministic local fallback router",
                "3. Guard Layer (executor.py): ToolExecutor whitelist, human approval gate, JSONL audit log",
                "4. Policy & Adapter Layer: PolicyEngine (policy.py) + MockAdapter & Sepolia ChainAdapter",
            ],
        ),
        (
            "3. Autonomous Asset Management (Task Completion - 40%)",
            "Six structured tools give the agent complete treasury visibility and execution power",
            [
                "get_portfolio_status: Tracks total balance, 0.002 ETH reserve floor, and spendable liquidity",
                "simulate_transfer: Preflight dry-run returning 0-100 risk score, gas cost, and projected balance",
                "send_eth & batch_send_eth: Single and multi-recipient settlement with per-item policy checks",
                "get_balance & get_policy_limits: Real-time inspection of wallet state and active governance rules",
            ],
        ),
        (
            "4. Three-Tier Governance & 7-Stage Policy Pipeline (Security - 30%)",
            "Deterministic Decimal math and persistent 24-hour state (logs/policy_state.json)",
            [
                "Tier 0 (READ_ONLY): Blocks all outgoing transfers; allows monitoring and dry-run simulation",
                "Tier 1 (APPROVE_ALL): 100% of valid transfers pause for human operator approval",
                "Tier 2 (LIMITED_AUTO): Auto-executes <= 0.002 ETH; escalates > 0.002 ETH; denies > 0.01 ETH",
                "Hard Guards: Allowlist regex check, 0.05 ETH 24h cap, 0.002 ETH reserve floor, 50 Gwei gas ceiling",
            ],
        ),
        (
            "5. Quantitative Risk Scoring & Preflight Simulation (Innovation - 30%)",
            "Every transaction is scored from 0 to 100 before touching the blockchain",
            [
                "Risk Formula combines recipient trust (+60), size ratio (+40), threshold (+15), 24h cap (+35), gas (+25)",
                "Risk Bands: LOW (0-19), MEDIUM (20-39), HIGH (40-69), CRITICAL (70-100)",
                "Commit-After-Receipt: Daily spend cap updates ONLY after on-chain receipt.status == 1",
                "Resilient Routing: Local intent router guarantees zero downtime during LLM API rate limits",
            ],
        ),
        (
            "6. Interactive Web Control Center (Streamlit Dashboard)",
            "Real-time visual telemetry, preflight risk simulator, and human-in-the-loop approval",
            [
                "Top KPI Bar: Network mode, Total ETH, Spendable ETH above reserve, 24h cap, Live Gas (Gwei)",
                "Sidebar Governance: Instant switching between Mock/Sepolia and Permission Tiers 0, 1, and 2",
                "Supervisor Banner: One-click Approve or Reject workflow for medium-risk transfers",
                "Live Audit Trail: Real-time table rendering structured events from logs/audit.jsonl",
            ],
        ),
        (
            "7. Real On-Chain Execution Evidence (Ethereum Sepolia Testnet)",
            "Verified live blockchain transactions with Etherscan proof and audit logs",
            [
                "Recipient Address: 0x78964c29614bF783c3339cd7b553C8627168554E",
                "TX #1 (Auto-Approved 0.0005 ETH | Risk 1/100 LOW | 2026-10-19 22:44:00):",
                "   0xd03fff8dc8ba123539f97cab7dd456c9487535c446df01674aee8cee6524a0a4",
                "TX #2 (Human-Approved 0.0022 ETH | Risk 21/100 MEDIUM | 2026-10-19 22:44:38):",
                "   0xbde5dd8c3f4e0ffdd0afae4ae95ae29e58f183618a17314e07495a323ac17cc0",
            ],
        ),
        (
            "8. Testing Rigor & Honest Security Self-Assessment",
            "50 passing unit tests and a transparent production hardening roadmap",
            [
                "50 Pytest Unit Tests: Covers adapters, rolling 24h persistence, reserve floor, and prompt injection",
                "Tier Verification Proof: Identical 0.001 ETH request -> Denied (T0), Human Asked (T1), Sent (T2)",
                "Known Prototype Risks Documented: Local approval channel, .env key storage, local JSON state",
                "Production Roadmap: ERC-4337 Account Abstraction session keys, WebAuthn passkeys, HSM custody",
            ],
        ),
        (
            "9. Summary: Built for Safe, Autonomous On-Chain Finance",
            "Complete alignment with FinTechathon Topic F evaluation criteria",
            [
                "Task Completion (40%): Full portfolio telemetry, simulation, single & batch Sepolia execution",
                "Security & Compliance (30%): 3 permission tiers, 7-stage policy engine, sanitized JSONL audit log",
                "Innovation & Interaction (30%): 0-100 risk scorer, Streamlit Control Center, resilient dual router",
                "Code & Evidence Ready: https://github.com/Crux-15/agent-wallet",
            ],
        ),
    ]

    for idx, (title, subtitle, bullets) in enumerate(slides, 1):
        pdf.add_page()
        # Header banner
        pdf.set_fill_color(12, 40, 88)
        pdf.rect(0, 0, 297, 36, style="F")
        pdf.set_xy(15, 8)
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(200, 220, 255)
        pdf.cell(0, 8, subtitle, new_x="LMARGIN", new_y="NEXT")

        # Bullets
        pdf.set_xy(20, 52)
        pdf.set_text_color(25, 25, 25)
        for b in bullets:
            pdf.set_x(20)
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(255, 11, f"-  {b}")
            pdf.ln(5)

        # Footer
        pdf.set_xy(15, 195)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(110, 110, 110)
        pdf.cell(0, 8, f"2026 Shenzhen International FinTech Competition | Topic F: Agent Wallet | Slide {idx} of {len(slides)}")

    out_path = OUT_DIR / "02_Presentation_Deck.pdf"
    pdf.output(str(out_path))
    print("Created:", out_path)


if __name__ == "__main__":
    build_technical_doc()
    build_security_doc()
    build_slides()
    print("\nALL 3 PDF DELIVERABLES GENERATED SUCCESSFULLY IN submission_files/")