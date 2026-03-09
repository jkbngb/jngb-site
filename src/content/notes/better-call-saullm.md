---
title: "Better Call Saul(LM): Six Models, Four Documents, Zero Consensus"
summary: "In <a href='/notes/privacy-first-contract-analysis'>Part 1</a>, three small models disagreed on whether the GPL is a contract. Fair enough. Small models on a laptop.<br><br>So we appealed to higher authority. Bigger models. An Nvidia H100. A legal-specialist LLM trained on court rulings.<br><br>The bigger models did not agree more. They <strong>disagreed differently</strong>. Llama 70B classified every single document as a contract. Its 8B sibling had said no to most of them. Same family. Same prompt. Same temperature.<br><br>Six models, four documents, <strong>zero consensus</strong>."
date: "2026-03"
tags: ["local-llm", "cloud-gpu", "document-processing", "model-disagreement"]
stack: ["Scaleway", "vLLM", "SaulLM-54B", "Qwen2.5-72B", "Llama-3.1-70B"]
---

## Quick Brief

- **Sequel to [Part 1](/notes/privacy-first-contract-analysis).** Same pipeline. Four deliberately ambiguous legal documents. Three local models on a laptop, three bigger models on an Nvidia H100 in a European data center.
- **The finding**: temperature 0.1 is supposed to be near-deterministic. Llama 3.1 classified the same document as both CONTRACT and NOT CONTRACT on successive runs. Same prompt, same hardware, same everything.
- **Scale does not resolve disagreement.** Bigger models don't agree more. They disagree differently. Every document produces a different voting coalition across six models.

## Context

[Part 1](/notes/privacy-first-contract-analysis) ended with a question: if three small local models disagree on an ambiguous document, do bigger models resolve it?

The short answer is no.

The longer answer involves a legal-specialist LLM, an Nvidia H100 in Warsaw, and the discovery that a MacBook Air can outpace a data center GPU under the right (wrong) conditions.

## The Experiment

Same eight-step pipeline as before. Same classification prompt. (<a href="/classification-prompt.txt" target="_blank">Here it is, in full</a>, for anyone who wants to see exactly what the models were given.) Temperature 0.1 across every run, on every model.

One honest disclosure about the prompt: line 5 reads *"contract, legal agreement, or terms of service."* That phrasing nudges the model toward classifying a Terms of Service as a contract. Some models followed the hint. Others ignored it entirely. We publish the prompt so you can judge for yourself.

### Documents

Four documents, chosen because they sit in the grey zone between "clearly a contract" and "clearly not."

| Document | Why it is ambiguous |
|----------|---------------------|
| GNU GPL v3 | A license with obligations, conditions, and restrictions. No named parties. No signatures. |
| Creative Commons BY-SA 4.0 | Rights and conditions, but permissive. More of a permission slip than a binding agreement. |
| Sample Terms of Service | The classification prompt literally mentions "terms of service." Does the model follow the hint? |
| Sample MOU | Not legally binding in the traditional sense, but structurally looks exactly like a contract. |

### Models

**Local** (Apple MacBook Air M3, 16 GB RAM, via Ollama):

- <a href="https://ollama.com/library/llama3.1:8b" target="_blank">Llama 3.1 (8B)</a>
- <a href="https://mistral.ai/news/mistral-nemo" target="_blank">Mistral Nemo (12B)</a>
- <a href="https://huggingface.co/Qwen/Qwen2.5-14B" target="_blank">Qwen 2.5 (14B)</a>

**Cloud** (Scaleway H100-1-80G, 80 GB VRAM, Warsaw, via vLLM):

- <a href="https://huggingface.co/Equall/SaulLM-54B-Instruct" target="_blank">SaulLM 54B</a> – a Mistral derivative fine-tuned on US and European legal texts
- <a href="https://huggingface.co/Qwen/Qwen2.5-72B-Instruct" target="_blank">Qwen 2.5 (72B)</a>
- <a href="https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct" target="_blank">Llama 3.1 (70B)</a>

## Part 1: The Local Court

### The Model Disagreed With Itself

This was not the expected finding.

On the very first run, Llama 3.1 (8B) classified the GPL v3 as NOT CONTRACT. 90% confidence. Its reasoning: the document *"grants permissions rather than establishes contractual relationships."*

On the second run, same model, same document, same prompt, same hardware, same temperature: CONTRACT. 25 minutes of full contract analysis followed. Its reasoning this time: the document *"contains a preamble, terms and conditions, and obligations for developers and users."*

**Both arguments are defensible. That is the problem.**

![Llama classifying the GPL as CONTRACT while the previous run shows NOT CONTRACT](/images/llama-gpl-flip.png)
*Same model. Same document. Same temperature (0.1). Different answer.*

Temperature 0.1 is supposed to be near-deterministic. It is not deterministic enough. On a document like the GPL, the model sits right on a decision boundary. A tiny amount of sampling noise is enough to flip the result. If you are using classification as a gate in your pipeline, this matters.

### The Voting Table

The remaining local runs were more stable, but the disagreement patterns were just as interesting.

![All three local models evaluating the GPL v3](/images/gpl-three-models-local.png)
*Three models, one document. Qwen and Mistral agree (not a contract). Llama can't make up its mind.*

| Document | Llama 8B | Mistral 12B | Qwen 14B |
|----------|----------|-------------|----------|
| GPL v3 | 🤷‍♂️ | NO | NO |
| CC BY-SA 4.0 | NO | NO | NO |
| Terms of Service | NO | NO | **YES** |
| MOU | **YES** | NO | **YES** |

**No two documents produced the same coalition.** Every document split the court differently.

A few things stood out:

**Mistral was the strictest classifier.** Four documents, four times NOT CONTRACT. Its reasoning was consistently structural: no named parties, no signatures, no deal.

**Qwen was the most prompt-compliant.** The classification prompt mentions "terms of service," and Qwen took the hint. The other two models ignored it and did their own structural analysis.

**Every model reported 90–100% confidence.** Even when they disagreed with each other. Even when Llama disagreed with itself. Confidence, at least for ambiguous legal documents, tells you nothing.

## Part 2: Oyez! Oyez! Oyez!

The small models disagreed on every document. Time to appeal to a higher court.

The compute runs on Scaleway, in a Warsaw data center. (Paris was fully booked.) The GPU is still Nvidia.

![Scaleway H100 instance: €2.73 per hour](/images/scaleway-h100-summary.png)
*The appeal comes at €2.73 per hour, billed per minute.*

Three cloud models. Same documents. Same prompt. Same temperature. The question: does scale resolve the disagreement? Does legal specialization?

### Better Call Saul(LM)

The first model to take the bench was a specialist.

<a href="https://huggingface.co/Equall/SaulLM-54B-Instruct" target="_blank">SaulLM 54B</a> is a legal-domain LLM. Fine-tuned on court rulings, legislative documents, and US/European legal texts. The kind of model you call in when the generalists can't agree.

![SaulLM appearing in the model dropdown alongside local models](/images/saullm-enters-courtroom.png)
*The specialist enters.*

| Document | SaulLM 54B | Confidence |
|----------|-----------|------------|
| GPL v3 | NOT CONTRACT | 90% |
| CC BY-SA 4.0 | NOT CONTRACT | 90% |
| Terms of Service | NOT CONTRACT | 90% |
| MOU | **CONTRACT** | 100% |

Three out of four: not a contract. On the MOU, a confident yes.

Now here is the reveal.

**SaulLM is built on Mixtral.** Same model family as Mistral Nemo, the hanging judge from the local court who voted NO on everything.

And SaulLM voted almost identically. Three out of four NO, just like its generalist parent. The legal specialist and the general-purpose model from the same family arrived at nearly the same conclusions.

Nearly.

The one break: the MOU. Mistral 12B rejected it (no binding language, no signatures). SaulLM accepted it (named parties, legal obligations, signature block). The legal specialist recognized what the generalist dismissed.

**Legal training didn't make the model more permissive. It made it more precise.** SaulLM rejected the licenses and the ToS (despite the prompt nudge), but it recognized the MOU's contractual structure where its parent saw only a non-binding document.

### The Big Siblings

Two more cloud models completed the bench.

<a href="https://huggingface.co/Qwen/Qwen2.5-72B-Instruct" target="_blank">Qwen 2.5 72B</a> is the bigger sibling of the 14B that dissented on the Terms of Service. <a href="https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct" target="_blank">Llama 3.1 70B</a> is the bigger sibling of the 8B that couldn't agree with itself.

**Llama 70B classified all four documents as CONTRACT.** Every single one. Its 8B version was cautious (mostly NO). Its 70B version said yes to everything. Scale didn't stabilize the decision boundary. It moved it entirely to the other side.

**Qwen 72B classified three out of four as CONTRACT.** It agreed with its 14B sibling on the GPL (no), ToS (yes), and MOU (yes). But it flipped on CC BY-SA. The smaller model said no. The bigger model decided a Creative Commons license counts as a "legal agreement." A more generous interpretation, not a more accurate one.

(A footnote on speed: Qwen 72B on the H100 ran slower than Qwen 14B on the MacBook Air. A quantization kernel incompatibility meant the laptop outpaced the data center GPU on token generation. This is not a commentary on Nvidia's hardware. It is a commentary on how software compatibility can bottleneck even the most expensive silicon.)

### The Combined Table

| Document | Llama 8B | Mistral 12B | Qwen 14B | | SaulLM 54B | Qwen 72B | Llama 70B |
|----------|----------|-------------|----------|---|------------|----------|-----------|
| GPL v3 | 🤷‍♂️ | NO | NO | | NO | NO | YES |
| CC BY-SA 4.0 | NO | NO | NO | | NO | YES | YES |
| ToS | NO | NO | YES | | NO | YES | YES |
| MOU | YES | NO | YES | | **YES** | YES | YES |

*Local models on the left, cloud models on the right. Bold YES for SaulLM on the MOU marks where legal training broke from the Mistral family pattern.*

Six models. Four documents. Twenty-four classification decisions. **No stable coalition.**

A few patterns:

- **The Mistral family is the strictest.** Mistral 12B voted NO on everything. SaulLM voted NO on three, only breaking ranks where legal training recognized genuine contractual structure.
- **The Llama family is the least consistent.** The 8B was mostly NO. The 70B was always YES. Same architecture, same training lineage, completely opposite behavior at different scales.
- **Scale makes models more permissive, not more precise.** Both Qwen 72B and Llama 70B said YES more often than their smaller siblings. Bigger does not mean better calibrated on judgment calls.
- **The MOU is the only near-consensus.** Five of six models classified it as a contract. The CC BY-SA was the most divisive after the GPL.

## So What?

This experiment was not designed to find the "right" answer. The GPL v3 is genuinely ambiguous. Reasonable lawyers disagree about whether open-source licenses are contracts. Reasonable models do the same.

The implications for anyone building classification pipelines:

**Temperature 0.1 is not deterministic enough for gating decisions.** If a model sits on a decision boundary, near-zero temperature can still produce different results on successive runs. A classification-as-gate architecture needs a fallback: run the classification twice, use a majority vote, or flag borderline confidence for human review.

**Confidence scores are noise on ambiguous documents.** Every model reported 90–100% confidence on every classification. Including the contradictory ones. Do not route decisions based on confidence alone.

**Model scale does not converge on truth.** The intuition that bigger models are "better" holds for knowledge retrieval. It does not hold for judgment calls on ambiguous categories. Llama 70B saying YES to everything is not more correct than Llama 8B saying mostly NO. It is a different bias, not a better one.

**Domain fine-tuning is more useful than raw scale.** SaulLM, with legal training on a Mixtral base, produced the most defensible set of classifications. It rejected the licenses (structurally not contracts), rejected the Terms of Service (despite the prompt nudge), and accepted the MOU (structurally a contract with named parties and a signature block). It did this with fewer parameters than either Llama 70B or Qwen 72B. It didn't need 70 billion parameters. It needed the right training data.

If you are building a system that makes binary decisions on ambiguous documents, a single model is not enough. Use multiple models. Compare their votes. When they disagree, that is not a bug. **That is information.** Surface it, flag it, and let a human make the call.

The models are not wrong when they disagree. The category is genuinely ambiguous. The only mistake is building a system that pretends otherwise.
