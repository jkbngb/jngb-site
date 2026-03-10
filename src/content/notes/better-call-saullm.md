---
title: "Better Call Saul(LM): Do Bigger Models Actually Agree on Ambiguous Documents?"
summary: "Six open-source LLMs were asked to classify four ambiguous legal documents as contract or not contract. Same prompt. Same temperature. Same documents.<br><br>One model <strong>disagreed with itself</strong> on successive runs. The bigger models did not agree more. They disagreed differently.<br><br>Scaling up did not resolve the disagreement, but <strong>a legal-specialist model came closest to getting it right</strong>."
date: "2026-03"
tags: ["local-llm", "cloud-gpu", "document-processing", "model-disagreement"]
stack: ["Scaleway", "vLLM", "SaulLM-54B", "Llama-3.1-70B", "Qwen2.5-72B"]
---

## Quick Brief

- **Experiment**: six open-source LLMs classify four ambiguous legal documents. Three small models on a laptop, three larger models on an Nvidia H100 in a European data center. One of them a legal specialist.
- **Why it matters**: if you use an LLM as a classification gate in a document pipeline, you need to know how stable that gate actually is.
- **Key insight**: temperature 0.1 is supposed to be near-deterministic. That didn't stop one model from classifying the same document as both CONTRACT and NOT CONTRACT on successive runs. Scaling up did not help, but domain fine-tuning outperformed raw parameter count.

## Context

A <a href="/notes/privacy-first-contract-analysis">previous experiment</a> tested whether contract classification could run entirely on a local laptop using open-source LLMs. Three small models agreed on the easy documents and **disagreed on the hard one**. Which raised the obvious follow-up: **do bigger, more capable models resolve the disagreement?**

Short answer: they just disagree more eloquently.

The longer answer involves a legal-specialist LLM, an Nvidia H100 in Warsaw, and the discovery that a MacBook Air can outpace a data center GPU under the right (i.e., wrong) conditions.

## The Experiment

The pipeline processes uploaded PDFs through eight steps: extraction, normalization, whitespace collapsing, classification, chunking, analysis, and structured output. The LLM only appears at step four, where it receives the beginning of the document and a <a href="/classification-prompt.txt" target="_blank">classification prompt</a> asking it to decide: contract or not? Temperature 0.1 across every run, meaning the model picks the most likely next token 90% of the time, with just a sliver of randomness left.

One disclosure about that prompt: it includes the phrase *"contract, legal agreement, or terms of service."* That phrasing nudges the model toward classifying a Terms of Service as a contract. Some models followed the hint. Others ignored it entirely.

**Four documents** were chosen because they sit in the grey zone between "clearly a contract" and "clearly not":

| Document | Why it is ambiguous |
|----------|---------------------|
| <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank">GNU GPL v3</a> | A license with obligations, conditions, and restrictions. No named parties. No signatures. |
| <a href="https://creativecommons.org/licenses/by-sa/4.0/legalcode.en" target="_blank">Creative Commons BY-SA 4.0</a> | Rights and conditions, but permissive. More of a permission slip than a binding agreement. |
| <a href="https://www.termsfeed.com/public/uploads/2021/12/sample-terms-of-service-template.pdf" target="_blank">Sample Terms of Service</a> | The classification prompt literally mentions "terms of service." Does the model take the bait? |
| <a href="https://www.justice.gov/sites/default/files/ovw/legacy/2008/10/21/sample-mou.pdf" target="_blank">Sample MoU</a> | Not legally binding in the traditional sense, but structurally looks exactly like a contract. |

For the record: the author does not have a law degree and makes no claim to understanding what actually constitutes a contract. The models, as it turned out, didn't either.

## The Local Court

**Six open-source LLMs** evaluated these documents. The first three were the same small models from the <a href="/notes/privacy-first-contract-analysis">previous experiment</a>, running on an Apple MacBook Air (M3, 16 GB RAM) via Ollama: <a href="https://ollama.com/library/llama3.1:8b" target="_blank">Llama 3.1 (8B)</a>, <a href="https://mistral.ai/news/mistral-nemo" target="_blank">Mistral Nemo (12B)</a>, and <a href="https://huggingface.co/Qwen/Qwen2.5-14B" target="_blank">Qwen 2.5 (14B)</a>.

Before running the new documents, a sanity check. In the previous experiment, Llama 3.1 (8B) had classified the <a href="/notes/privacy-first-contract-analysis">GPL v3 as a contract</a>. Same model, same document, same prompt, same hardware, same temperature. If nothing else, that result should be reproducible.

It was not. Llama classified the GPL v3 as NOT CONTRACT. 90% confidence. Its reasoning this time: the document *"grants permissions rather than establishes contractual relationships."*

**The experiment could not even be reproduced before it had properly started.**

So we ran it again, just to be sure. This time: CONTRACT. 90% confidence. 25 minutes of full contract analysis followed. The reasoning was that the document *"contains a preamble, terms and conditions, and obligations for developers and users."* Both arguments are defensible. That is the problem.

Temperature 0.1 is supposed to be near-deterministic. But it seems not deterministic enough. On a document like the GPL, the model sits right on a decision boundary, and a tiny amount of sampling noise is enough to flip the verdict.

![Llama classifying the GPL as CONTRACT while the previous run shows NOT CONTRACT](/images/llama-gpl-flip.png)
*Caught in the act: Llama disagrees with itself. Bottom row: NOT CONTRACT. Top row, minutes later: CONTRACT. A re-run confirmed the original result from the previous experiment.*

The remaining local runs were more stable and confirmed their previous judgements. Time to see how the three models would classify the other ambiguous documents.

All four documents went through the pipeline. The results:

**No two documents produced the same coalition.** Every document split the court differently:

- **Mistral was the hanging judge.** Four documents, four times NOT CONTRACT. Its reasoning was consistently structural: no named parties, no signatures, no deal.
- **Qwen was the most prompt-compliant.** The classification prompt mentions "terms of service," and Qwen took the hint. The other two models ignored it and did their own structural assessment.
- **Every model reported 90 to 100% confidence.** On every document. Including the ones they disagreed on. Including the one where Llama disagreed with itself. Confidence scores, on ambiguous legal documents, are noise.

<table style="width:100%; border-collapse:collapse;">
  <thead>
    <tr>
      <th style="text-align:left;">Document</th>
      <th style="text-align:center;">Llama 8B</th>
      <th style="text-align:center;">Mistral 12B</th>
      <th style="text-align:center;">Qwen 14B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left;"><a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank">GPL v3</a></td>
      <td style="text-align:center;">🤷‍♂️</td>
      <td style="text-align:center;">❌</td>
      <td style="text-align:center;">❌</td>
    </tr>
    <tr>
      <td style="text-align:left;"><a href="https://creativecommons.org/licenses/by-sa/4.0/legalcode.en" target="_blank">CC BY-SA 4.0</a></td>
      <td style="text-align:center;">❌</td>
      <td style="text-align:center;">❌</td>
      <td style="text-align:center;">❌</td>
    </tr>
    <tr>
      <td style="text-align:left;"><a href="https://www.termsfeed.com/public/uploads/2021/12/sample-terms-of-service-template.pdf" target="_blank">Terms of Service</a></td>
      <td style="text-align:center;">❌</td>
      <td style="text-align:center;">❌</td>
      <td style="text-align:center;">✅</td>
    </tr>
    <tr>
      <td style="text-align:left;"><a href="https://www.justice.gov/sites/default/files/ovw/legacy/2008/10/21/sample-mou.pdf" target="_blank">MoU</a></td>
      <td style="text-align:center;">✅</td>
      <td style="text-align:center;">❌</td>
      <td style="text-align:center;">✅</td>
    </tr>
  </tbody>
</table>

<p style="text-align:center; font-size:0.9em; margin-top:-0.5em;">✅ contract &emsp; ❌ not contract</p>

*The GPL v3 was already tested in the <a href="/notes/privacy-first-contract-analysis">previous experiment</a>. Llama had classified it as a contract then. This time, it simply switched sides.*

The small models couldn't agree on what constitutes a contract. So what would a lawyer do? Exactly. Appeal to a higher court.

## Oyez! Oyez! Oyez!

A proper appeal needs proper hardware. The compute runs on <a href="https://www.scaleway.com/en/" target="_blank">Scaleway</a>, a European cloud provider, which in the current geopolitical climate might be reassuring to some. Scaleway offers GPU instances in Paris and Warsaw. Paris was fully booked, so the court convened in Warsaw. The cost of this appeal: **€2.73 per hour**, billed per minute.

![H100 server specs](/images/h100-neofetch.png)
*AMD EPYC, 240 GB system memory, Nvidia H100 PCIe with 80 GB VRAM. The bench is ready.*

Three larger models took the stand. Same documents. Same prompt. Same temperature:

- <a href="https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct" target="_blank">**Llama 3.1 (70B)**</a> – the bigger sibling of the 8B that couldn't agree with itself
- <a href="https://huggingface.co/Qwen/Qwen2.5-72B-Instruct" target="_blank">**Qwen 2.5 (72B)**</a> – the bigger sibling of the 14B that was the lone dissenter on Terms of Service
- <a href="https://huggingface.co/Equall/SaulLM-54B-Instruct" target="_blank">**SaulLM 54B**</a> – a Mistral derivative fine-tuned on US and European legal texts, court rulings, and legislative documents

The question was straightforward: does scale resolve the disagreement? Does legal specialization?

The first model to take the bench was not a bigger generalist. It was a specialist.

SaulLM 54B is a legal-domain LLM, fine-tuned on court rulings, legislative documents, and legal texts from both sides of the Atlantic. The kind of model you bring in when the generalists can't agree. (A larger 141-billion parameter version also exists, but it didn't fit on the hardware. Even the H100's 80 GB of VRAM has limits.)

![SaulLM appearing in the model dropdown alongside local models](/images/saullm-enters-courtroom.png)
*The honourable chief justice. SaulLM 54B, presiding.*

SaulLM looked at the four documents and delivered its opinion with the quiet confidence of a model that has read a lot of case law. And it was fast. Classification in under two seconds. This is what you expect when an H100 meets a model that doesn't waste compute. Three out of four: not a contract. Only the MoU got a confident yes.

But in the interest of judicial transparency, a potential conflict of interest must be disclosed.

**SaulLM is built on Mixtral.** Same model family as Mistral Nemo, the hanging judge from the local court who voted NO on every single document. The legal specialist and the generalist share the same DNA, but their verdicts do not fully reflect it: SaulLM matched Mistral's vote on three out of four documents.

But not on the fourth.

The MoU is where legal training made the difference. Mistral 12B rejected it (no binding language, not a real contract). SaulLM accepted it (named parties, legal obligations, signature block). The legal specialist recognized the contractual structure that its generalist parent dismissed.

**Legal training didn't make the model more permissive. It made it more precise.** It still rejected the licenses and the ToS despite the prompt nudge, but it identified the MoU as what it structurally is: an agreement between named parties with defined obligations. Legal school didn't lower the bar. It taught the model where the bar actually stands.

The two remaining cloud models were the larger siblings of the local models, and we wanted to test whether verdicts run along family lines, the way ideology runs along party lines on the US Supreme Court.

- <a href="https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct" target="_blank">**Llama 3.1 70B**</a> classified all four documents as CONTRACT. Every single one. Its 8B version was cautious, mostly saying no. Its 70B version said yes to everything. Scale didn't stabilize the decision boundary. It moved it entirely to the other side.
- <a href="https://huggingface.co/Qwen/Qwen2.5-72B-Instruct" target="_blank">**Qwen 2.5 72B**</a> classified three out of four as CONTRACT. It agreed with its 14B sibling on the GPL (no), ToS (yes), and MoU (yes), but flipped on CC BY-SA. The smaller model said no. The bigger model decided a Creative Commons license qualifies as a "legal agreement." A more generous reading, not necessarily a better one.

There was one unplanned finding about speed. Qwen 72B on the H100 actually ran slower than Qwen 14B on the MacBook Air. A quantization kernel incompatibility meant the €2.73-per-hour GPU was being outpaced by a laptop on a kitchen table.

The H100 managed 9.7 tokens per second on the MoU analysis. The MacBook did 16.4. <a href="https://www.youtube.com/watch?v=OF_5EKNX0Eg" target="_blank">This is not a commentary on Nvidia's hardware.</a> It is what happens when a software layer between the model and the silicon isn't optimized for the GPU's architecture. **Infrastructure matters as much as the model itself.**

With all twenty-four classifications complete, the combined picture looked like this:

<table style="width:100%; border-collapse:collapse; text-align:center;">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" style="text-align:center; border:none; font-weight:normal; font-size:0.85em; color:#888; padding-bottom:0;">Local</th>
      <th colspan="3" style="text-align:center; border:none; border-left:2px solid #ccc; font-weight:normal; font-size:0.85em; color:#888; padding-bottom:0;">Remote</th>
    </tr>
    <tr>
      <th style="text-align:left;">Document</th>
      <th style="text-align:center; background:#dbeafe;">Llama 8B</th>
      <th style="text-align:center; background:#ffedd5;">Mistral 12B</th>
      <th style="text-align:center; background:#dcfce7;">Qwen 14B</th>
      <th style="text-align:center; background:#dbeafe; border-left:2px solid #ccc;">Llama 70B</th>
      <th style="text-align:center; background:#ffedd5;">SaulLM 54B</th>
      <th style="text-align:center; background:#dcfce7;">Qwen 72B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left;"><a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank">GPL v3</a></td>
      <td style="text-align:center; background:#dbeafe;">🤷‍♂️</td>
      <td style="text-align:center; background:#ffedd5;">❌</td>
      <td style="text-align:center; background:#dcfce7;">❌</td>
      <td style="text-align:center; background:#dbeafe; border-left:2px solid #ccc;">✅</td>
      <td style="text-align:center; background:#ffedd5;">❌</td>
      <td style="text-align:center; background:#dcfce7;">❌</td>
    </tr>
    <tr>
      <td style="text-align:left;"><a href="https://creativecommons.org/licenses/by-sa/4.0/legalcode.en" target="_blank">CC BY-SA 4.0</a></td>
      <td style="text-align:center; background:#dbeafe;">❌</td>
      <td style="text-align:center; background:#ffedd5;">❌</td>
      <td style="text-align:center; background:#dcfce7;">❌</td>
      <td style="text-align:center; background:#dbeafe; border-left:2px solid #ccc;">✅</td>
      <td style="text-align:center; background:#ffedd5;">❌</td>
      <td style="text-align:center; background:#dcfce7;">✅</td>
    </tr>
    <tr>
      <td style="text-align:left;"><a href="https://www.termsfeed.com/public/uploads/2021/12/sample-terms-of-service-template.pdf" target="_blank">ToS</a></td>
      <td style="text-align:center; background:#dbeafe;">❌</td>
      <td style="text-align:center; background:#ffedd5;">❌</td>
      <td style="text-align:center; background:#dcfce7;">✅</td>
      <td style="text-align:center; background:#dbeafe; border-left:2px solid #ccc;">✅</td>
      <td style="text-align:center; background:#ffedd5;">❌</td>
      <td style="text-align:center; background:#dcfce7;">✅</td>
    </tr>
    <tr>
      <td style="text-align:left;"><a href="https://www.justice.gov/sites/default/files/ovw/legacy/2008/10/21/sample-mou.pdf" target="_blank">MoU</a></td>
      <td style="text-align:center; background:#dbeafe;">✅</td>
      <td style="text-align:center; background:#ffedd5;">❌</td>
      <td style="text-align:center; background:#dcfce7;">✅</td>
      <td style="text-align:center; background:#dbeafe; border-left:2px solid #ccc;">✅</td>
      <td style="text-align:center; background:#ffedd5;">✅</td>
      <td style="text-align:center; background:#dcfce7;">✅</td>
    </tr>
  </tbody>
</table>

<p style="text-align:center; font-size:0.9em; margin-top:0.5em;">✅ contract &emsp; ❌ not contract<br><span style="background:#dbeafe; padding:2px 8px;">Meta</span> &emsp; <span style="background:#ffedd5; padding:2px 8px;">Mistral</span> &emsp; <span style="background:#dcfce7; padding:2px 8px;">Alibaba</span></p>

*The verdict of what actually constitutes a contract is in. It is... confusing.*

Six models. Four documents. **No stable coalition.** The Mistral family (Mistral 12B and its legal derivative SaulLM) was the strictest, rejecting almost everything.

The Llama family was the most chaotic: the 8B mostly said no, the 70B always said yes. Same architecture, same training lineage, completely opposite behavior at different scales.

And both Qwen and Llama got more permissive at scale, not more precise. Bigger models said yes more often. That is not the same as being right more often.

The only near-consensus was the MoU: five of six models classified it as a contract. On everything else, the court was split.

## So What?

This experiment was never about finding the "right" answer. The GPL v3 is genuinely ambiguous. Reasonable lawyers disagree about whether open-source licenses are contracts (or so the author is told, being neither a lawyer nor anything remotely adjacent to one). Reasonable models do the same.

**A single model is not enough for classification gates on ambiguous documents.** Temperature 0.1 can still produce different results on successive runs. Confidence scores read 90 to 100% even when the model is contradicting itself.

And scaling up does not converge on truth: Llama 70B's 4/4 YES is not more correct than Llama 8B's mostly NO. It is a different bias, not a better one.

The most defensible set of decisions came from SaulLM, the legal specialist. It didn't need the most parameters. It needed the right training data. If you are choosing between a bigger generalist and a smaller specialist for a domain-specific classification task, this experiment suggests the specialist is worth a serious look.

In practice, a production system probably needs multiple models, a voting mechanism, and a human in the loop for the cases where the models split. **When they disagree, that is not a failure. That is information.** The mistake is building a system that pretends ambiguity doesn't exist.
