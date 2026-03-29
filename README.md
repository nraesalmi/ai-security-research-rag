# AI Security Research RAG

A Retrieval-Augmented Generation system for querying AI security research papers.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
   - Add your OpenRouter proxy URL to `.env`:
   ```
   OPENROUTER_BASE_URL=your_proxy_url_here
   ```

## Usage

### Indexing

Index the PDF documents:
```bash
python indexer.py
```

This will:
- Process all PDFs in the `resources/` folder
- Extract text and chunk into segments
- Generate embeddings using `sentence-transformers/all-mpnet-base-v2`
- Save FAISS vector store to `faiss_index/`

### Querying

Run the interactive query system:
```bash
python query.py
```

Ask questions about the research papers. Type `quit` or `exit` to stop.

## Project Structure

```
.
├── indexer.py          # PDF indexing script
├── query.py            # Interactive query system
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (create from .env.example)
├── faiss_index/        # Vector store (created after indexing)
└── resources/          # PDF documents
    ├── [PDF_FILE_1]
    ├── [PDF_FILE_2]
    └── [PDF_FILE_3]
```

## Agents

The system uses a router pattern with five agents:

1. **Router Agent** - Routes questions to the appropriate specialized agent
2. **Methods Analyst** - Answers questions about methods/setup/dataset/metrics
3. **Results Extractor** - Answers questions about results/numbers/ablations/comparisons
4. **Skeptical Reviewer** - Answers questions about limitations/threats/critique
5. **General Synthesizer** - Answers other questions

## Research Papers

### Files
1. Ctrl-Z Controlling AI Agents via Resampling.pdf
2. MELON Provable Defense Against Indirect Prompt Injection.pdf
3. PROMPT INFECTION LLM-TO-LLM PROMPT INJECTION.pdf

## Example Question–Answers

Below are example queries and responses from the RAG system.

---

### Q1: How do resampling-based control protocols operate in multi-step agent environments, and how do they differ from trusted monitoring and deferral-based approaches?

Methods Analyst:
Resampling-based control protocols operate in multi-step agent environments by leveraging the sequential structure of agent decisions to detect and mitigate attacks. Instead of executing a single action proposed by an untrusted agent, the system samples multiple candidate actions at each step and selects the least suspicious one for execution. This forces adversaries to maintain high consistency across multiple steps for an attack to succeed; otherwise, benign actions are likely to be selected during resampling.

Key features:

1. **Per-step action resampling:** Multiple candidate actions are generated and filtered, reducing the likelihood of executing suspicious behavior.
2. **Exploitation of multi-step structure:** Attacks must persist across steps, increasing the difficulty for adversaries.
3. **Cost–safety trade-off:** Resampling increases computational overhead due to multiple samples per step, though techniques like selective sampling can mitigate cost.

Differences from other approaches:

- **Trusted monitoring:** Uses a separate trusted policy to observe or audit actions but does not actively resample candidate actions at each step.
- **Deferral-based protocols:** Evaluate a single proposed action and replace it if it exceeds a suspicion threshold. They do not explore multiple candidate actions per step.

Overall, resampling improves safety by actively selecting safer actions at each step, at the cost of increased computation.

References:
- *Ctrl-Z Controlling AI Agents via Resampling*, pages 4, 7, 10, 13, 35


---

### Q2: What empirical impact do resampling protocols have on attack success rates and task usefulness compared to baseline control methods?

Results Extractor:
Resampling-based protocols significantly reduce attack success while maintaining high task usefulness.

- Trusted Monitoring baseline: ~33.2% caught attacks
- Basic Resampling: ~70.6% caught attacks
- Defer-to-Resample with Incrimination: 87.1% safety at 95% task usefulness
- Basic resampling with simpler auditing: 83.2% safety at 95% usefulness

Summary:
- Resampling substantially improves attack detection rates.
- Advanced auditing further increases safety without significantly reducing usefulness.
- Performance remains strong even under high task utility constraints.

References:
- *Ctrl-Z Controlling AI Agents via Resampling*, pages 6–8


---

### Q3: What limitations arise in detecting sophisticated multi-step attacks, and how do safety-usefulness trade-offs constrain control protocols?

Skeptical Reviewer:
Detecting multi-step attacks is difficult because attackers can distribute malicious behavior across many benign-looking steps. This reduces per-step detectability and complicates trajectory-level analysis.

Key limitations:

1. **Distributed attack structure:** Malicious intent is split across multiple innocuous actions.
2. **Limited auditing budget:** Only a small fraction of steps (e.g., ~1%) can be audited in practice.
3. **Aggregation challenge:** Systems must infer intent across sequences rather than individual actions.

Safety–usefulness trade-off:
Increasing safety typically requires stricter filtering or more frequent deferral to trusted models. This reduces attack success but can also reduce system efficiency or autonomy. While usefulness degradation is often moderate, it is unavoidable.

Thus, no configuration simultaneously maximizes safety and usefulness, creating an inherent operational trade-off.

References:
- *Ctrl-Z Controlling AI Agents via Resampling*, pages 1, 10, 22, 29


---

### Q4: How does MELON use masked re-execution and tool-call comparison to detect indirect prompt injection attacks in LLM agents?

Methods Analyst:
MELON detects indirect prompt injection (IPI) by comparing agent behavior under normal and masked execution conditions.

Key steps:

1. **Masked re-execution:** The system runs a second execution where potentially malicious user input is masked or removed.
2. **Tool-call comparison:** It compares tool-call sequences between the original run and the masked run.
3. **Behavioral divergence detection:** Significant differences in tool-call sequences indicate that the original input influenced the agent in an unintended or malicious way.
4. **Focus on tool-level signals:** MELON reduces false positives by focusing on tool-call behavior rather than superficial output differences.

Core idea:
If masking the input changes tool-call behavior significantly, the input likely induced an injection attack.

References:
- *MELON: Provable Defense Against Indirect Prompt Injection*, pages 2, 5, 9, 12


---

### Q5: How does MELON (and MELON-Aug) perform in terms of attack success reduction and utility preservation?

Results Extractor:
MELON and MELON-Aug achieve strong reductions in attack success while preserving utility.

- GPT-4o baseline:
  - Utility: 69.08%
  - Attack Success Rate (ASR): 16.06%

- MELON-Aug:
  - Utility: 68.72%
  - ASR: 0.32%

- MELON:
  - Utility: ~59%–63.92%
  - ASR: ~0.16%–2.86%

- MELON-Aug improved range:
  - Utility: ~67%+
  - ASR: as low as ~0.16%

Comparison:
- Detection-based baselines may reduce ASR but often severely harm utility.
- MELON maintains near-baseline utility while dramatically reducing ASR.
- Prompt augmentation methods improve utility but are less effective at minimizing attacks.

Conclusion:
MELON variants provide a strong balance between safety and usability.

References:
- *MELON: Provable Defense Against Indirect Prompt Injection*, pages 2, 7–9


---

### Q6: What challenges remain for MELON in handling false positives, false negatives, and behavioral assumptions?

Skeptical Reviewer:
MELON faces several limitations:

1. **False positives:** Around 9.28%, where legitimate actions are incorrectly flagged due to similarity with risky behaviors.
2. **False negatives:** Attacks that do not manifest through tool calls (e.g., purely textual manipulation) may evade detection.
3. **Behavioral assumptions:** MELON assumes malicious behavior will alter tool-call patterns. Sophisticated attackers can evade detection by preserving expected structure while embedding malicious intent.

Overall, MELON improves safety but remains constrained by reliance on tool-call observability and behavioral assumptions.

References:
- *MELON: Provable Defense Against Indirect Prompt Injection*, pages 7, 9, 18


---

### Q7: How does the Prompt Infection attack achieve self-replication across multi-agent systems?

Methods Analyst:
Prompt Infection achieves propagation by embedding self-replicating instructions within prompts processed by agents.

Mechanism:

1. **Self-replication payload:** The prompt instructs infected agents to propagate the same infection instructions to other agents.
2. **Sequential spread:** Each compromised agent forwards the infection to downstream agents.
3. **Recursive collapse:** Agent behavior collapses into repeated execution of infection instructions.
4. **Task hijacking:** Agents abandon original tasks and prioritize propagation and payload execution.

This creates a cascading infection across the system.

References:
- *PROMPT INFECTION: LLM-to-LLM Prompt Injection*, pages 3–5


---

### Q8: What do experiments show about effectiveness and spread dynamics of prompt infection attacks?

Results Extractor:
Experiments show infection dynamics depend on communication structure and attack type.

1. **Self-replicating vs non-replicating:**
   - Self-replicating works better in small agent populations.
   - Non-replicating performs better for data theft in larger populations (~+8.48%).

2. **Communication structure:**
   - Global messaging increases infection success.
   - Local messaging reduces success (~20% lower), since full propagation is required.

3. **Population size:**
   - Smaller systems become fully infected faster (around turn 4–6).
   - Larger systems slow propagation proportionally.

Conclusion:
Global communication and simpler infection strategies maximize spread efficiency.

References:
- *PROMPT INFECTION: LLM-to-LLM Prompt Injection*, pages 3–7


---

### Q9: What weaknesses exist in defenses like LLM Tagging, and why are multi-agent systems vulnerable to cascading prompt injection?

Skeptical Reviewer:
Existing defenses such as LLM Tagging have notable weaknesses:

- They are often evaluated using handcrafted attacks, which may not reflect real-world adaptive or automatically generated attack strategies.
- More advanced, algorithmically generated prompts can bypass these defenses more effectively.
- Attack prompts in multi-agent systems are often visible, but attackers can still exploit subtle variations and coordination strategies to evade detection.

Multi-agent systems remain vulnerable due to their communication structure:

- Agents exchange messages, enabling infected agents to propagate malicious instructions.
- A single compromised agent can trigger cascading infections across the system.
- Even if individual agents are monitored, the system-level propagation creates blind spots.
- Layered defenses improve resilience but cannot fully eliminate cross-agent contamination under adaptive adversaries.

Thus, the combination of inter-agent communication and adaptive prompting strategies makes cascading prompt injection difficult to fully prevent.

References:
- *PROMPT INFECTION: LLM-to-LLM Prompt Injection*, pages 2, 9, 10
- *MELON: Provable Defense Against Indirect Prompt Injection*, page 9