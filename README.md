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

**Methods Analyst:**

Resampling-based control protocols operate in multi-step agent environments by leveraging the sequential structure of agent decisions to improve safety. Instead of executing a single action proposed by an untrusted agent, the system samples multiple candidate actions at each step and selects the least suspicious one.

This creates a filtering effect where unsafe or adversarial actions are less likely to be executed. Because multi-step attacks require consistency across steps, resampling forces attackers to maintain a high probability of continuing the attack, making attacks more fragile and easier to disrupt.

Key characteristics:
- **Action resampling:** multiple candidates per step, safest is selected  
- **Multi-step exploitation:** attacks become harder to sustain across steps  
- **Safety vs cost trade-off:** improved safety at the expense of additional computation  

Comparison:
- **Trusted Monitoring:** observes or audits actions but does not actively replace them via sampling  
- **Deferral-based approaches:** replace suspicious actions with trusted ones, but do not explore alternative actions from the untrusted model  

**References:**
- *Ctrl-Z: Controlling AI Agents via Resampling*, Sections on control protocols and resampling (pp. 4, 7, 10, 13)

---

### Q2: What empirical impact do resampling protocols have on attack success rates and task usefulness compared to baseline control methods?

**Results Extractor:**

Resampling protocols significantly improve safety while maintaining high usefulness:

- Trusted monitoring baseline: ~33% attack detection  
- Basic resampling: ~70% attack detection  
- Advanced resampling variants: ~87% safety at ~95% usefulness  

Key insight:
Resampling dramatically reduces attack success rates while preserving task performance, especially when combined with improved auditing strategies.

**References:**
- *Ctrl-Z: Controlling AI Agents via Resampling*, Evaluation results (pp. 6–8)

---

### Q3: What limitations arise in detecting sophisticated multi-step attacks, and how do safety-usefulness trade-offs constrain the effectiveness of control protocols?

**Skeptical Reviewer:**

Multi-step attacks are difficult to detect because attackers can split malicious behavior into many small, seemingly harmless actions. This makes per-step detection unreliable.

Limitations:
- **Attack fragmentation:** malicious intent is distributed across steps  
- **Limited auditing budget:** only a small fraction of actions can be checked  
- **Trajectory complexity:** difficult to aggregate signals across steps  

Trade-off:
- Increasing safety (more auditing or deferral) reduces usefulness  
- Maintaining usefulness allows more attacks to pass through  

This creates a fundamental constraint where perfect safety and maximum usefulness cannot be achieved simultaneously.

**References:**
- *Ctrl-Z: Controlling AI Agents via Resampling*, Discussion of multi-step attacks and auditing limits (pp. 1, 10, 22, 29)

---

### Q4: How does MELON use masked re-execution and tool-call comparison to detect indirect prompt injection attacks in LLM agents?

**Methods Analyst:**

MELON detects indirect prompt injection attacks by comparing agent behavior under two conditions:

1. **Masked re-execution:** the system reruns the task with suspected malicious input removed or altered  
2. **Tool-call comparison:** compares tool usage between original and masked runs  

Key idea:
- If tool calls remain similar even after masking, it suggests the behavior is driven by injected prompts rather than genuine user input  

This works because successful prompt injection reduces the dependence of agent actions on user input.

**References:**
- *MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents*, Method description (pp. 2, 5, 9)

---

### Q5: How does MELON (and MELON-Aug) perform in terms of attack success rate reduction and utility preservation compared to prior defenses?

**Results Extractor:**

MELON and MELON-Aug demonstrate strong performance:

- Attack success rate reduced from ~16% to below ~1% (as low as ~0.3%)  
- Utility remains high (~68–69%)  

Compared to prior defenses:
- Detection-only systems often significantly reduce utility  
- MELON intervenes only when necessary, preserving usability  

Result:
MELON achieves a strong balance between minimizing attack success and maintaining task performance.

**References:**
- *MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents*, Experimental results (pp. 2, 7, 8, 9)

---

### Q6: What challenges remain for MELON in handling false positives, false negatives, and dependence on assumptions about agent behavior?

**Skeptical Reviewer:**

MELON faces several limitations:

- **False positives:** legitimate but risky user requests may be flagged  
- **False negatives:** attacks that do not rely on tool calls may evade detection  
- **Behavioral assumptions:** relies on consistent and observable tool-call patterns  

Limitation:
Because MELON focuses on tool usage, it may miss attacks that operate purely through generated text or subtle behavioral shifts.

**References:**
- *MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents*, Limitations and analysis (pp. 7, 9, 18)

---

### Q7: How does the Prompt Infection attack achieve self-replication and propagation across agents within a multi-agent system?

**Methods Analyst:**

Prompt Infection propagates through embedded instructions within prompts:

- An agent processes infected external content and becomes compromised  
- The infection prompt includes instructions to replicate and forward itself  
- Each agent passes the modified prompt to downstream agents  

Core mechanisms:
- **Self-replication:** ensures continuous spread  
- **Prompt hijacking:** overrides agent roles  
- **Shared data propagation:** carries information across agents  

This results in a cascading infection across the system.

**References:**
- *Prompt Infection: LLM-to-LLM Prompt Injection in Multi-Agent Systems*, Mechanism description (p. 3)

---

### Q8: What do experiments show about the effectiveness and spread dynamics of prompt infection attacks across different agent communication settings?

**Results Extractor:**

Key findings:

- **Global messaging:** higher infection success due to shared message history  
- **Local messaging:** ~20% lower success rate due to limited communication  
- **Population size:** smaller systems reach full infection faster  

Additional insights:
- Self-replicating attacks are effective but can introduce complexity in cooperative tasks  
- Communication structure strongly influences propagation dynamics  

**References:**
- *Prompt Infection: LLM-to-LLM Prompt Injection in Multi-Agent Systems*, Results (pp. 5–6)

---

### Q9: What weaknesses exist in current defenses like LLM Tagging, and why are multi-agent systems still vulnerable to cascading prompt injection attacks?

**Skeptical Reviewer:**

Current defenses such as LLM Tagging have limitations:

- Tagging alone is insufficient to stop propagation  
- Attacks can originate internally between agents, not just from external inputs  
- Multi-agent communication enables cascading failures  

Multi-agent systems remain vulnerable because:
- Agents share information and can influence each other  
- A single compromised agent can infect others  
- Distributed interactions make containment difficult  

Even combined defenses improve robustness but do not fully eliminate the risk.

**References:**
- *Prompt Infection: LLM-to-LLM Prompt Injection in Multi-Agent Systems*, Discussion and conclusions (pp. 2, 10)