---
title: "When LLMs Disagree: Testing Local Models on Contract Classification"
summary: "The nice thing about document classification is that it sounds simple.<br><br>The less nice thing is that it becomes considerably less simple the moment you hand the same legal document to three different <strong>open-source LLMs running on a laptop</strong> – and get two different answers back.<br><br>All three models were confident. One said yes, two said no.<br><br>The interesting part isn't which one was right. It's <strong>what this kind of disagreement tells you about how AI systems actually need to be built</strong>."
date: "2026-02"
tags: ["local-llm", "privacy", "document-processing", "pipeline-architecture"]
stack: ["Python", "Ollama", "llama3.1:8b", "mistral-nemo:12b", "qwen2.5:14b"]
---

## Quick Brief

- **Experiment**: evaluation of whether legal contract analysis can run entirely on a local laptop using open-source LLMs.
- **Why it matters**: many organizations are reluctant to send sensitive documents (contracts, financial records, internal agreements) to AI systems outside their organization.
- **Key insight**: the model itself is only a small part of the system. Most of the work happens in the surrounding pipeline – and ambiguous documents can still make different models disagree.

## Context

Organizations are increasingly enthusiastic about using AI on their documents. They are somewhat less enthusiastic about sending those documents to someone else's API.

Which raises a fairly practical architectural question: **how far can document analysis go if everything stays local?**

To explore this, I built a small prototype pipeline that processes uploaded PDFs and attempts to classify and extract information from legal contracts using locally hosted LLMs.

## Experiment Setup

The experiment was deliberately simple: upload a document, **decide whether it is a contract**, and if so extract useful information from it.

Under the hood, the system is mostly a pipeline. The model itself only appears halfway through the process.

![Pipeline: from PDF upload to structured output](/images/pipeline-diagram.svg)
*Most of the steps have nothing to do with AI.*

Three open-source models were evaluated:

- <a href="https://ollama.com/library/llama3.1:8b" target="_blank">Llama 3.1 (8B)</a>
- <a href="https://mistral.ai/news/mistral-nemo" target="_blank">Mistral Nemo (12B)</a>
- <a href="https://huggingface.co/Qwen/Qwen2.5-14B" target="_blank">Qwen2.5 (14B)</a>

All models ran locally using Ollama.

The hardware was intentionally modest: Apple MacBook Air (M3) with 16GB RAM. The goal was not peak performance but to evaluate whether local inference is practical for structured document workflows.

Test documents were chosen to represent both clear and ambiguous document categories.

## Observations

A few patterns appeared fairly quickly during testing.

### Performance

The models ran successfully on modest hardware. They were just not in a hurry.

Simple classification tasks required roughly 20-30 seconds.
Full contract extraction on longer documents could take more than 13 minutes.

So while the pipeline works, it is not particularly fast.

In practice, runtimes like these would limit fully local pipelines to batch-style workflows rather than interactive applications.

### Behavior on Clear vs Ambiguous Documents

The models behaved consistently when the classification task was unambiguous.

As a simple control test, a CV was uploaded first. All three models correctly identified that the document was not a contract and stopped processing.

A second test used a generic NDA without identifying names. Here again, the models agreed: all three classified the document as a contract and proceeded to extract participants and potential risk indicators.

So far, the models appeared to have a fairly clear idea of what a contract looks like.

![Contract Engine: Model disagreement on GNU GPL v3 classification](/images/contract-engine-jobs.png)
*Apparently the problem "contract / not contract" is slightly harder than <a href="https://www.youtube.com/watch?v=tWwCK95X6go" target="_blank">"hotdog / not hotdog"</a>.*

The divergence appeared once the document category became legally ambiguous. A [GNU General Public License v3](https://en.wikipedia.org/wiki/GNU_General_Public_License) was used as the next test document.

At this point the models behaved a bit like lawyers: they disagreed.

- **Mistral** classified the document as not a contract. Its reasoning: *"The document is a GNU General Public License, which grants permissions and sets conditions for using, modifying, and distributing software."*
- **Qwen** reached the same conclusion and stopped further processing. Its reasoning: *"The text is a license agreement, specifically the GNU General Public License version 3, which outlines permissions and conditions for software distribution but does not contain named parties or specific legal obligations typical of a contract."*
- **Llama 3.1** reached the opposite conclusion. It classified the document as a contract and continued with full information extraction. Once it did, the system produced structured output: 33 clauses, 24 obligations, and 3 identified risks. Among the extracted risks were a termination trigger rated as high risk (*"automatically terminate your rights under this License…"*) and an unlimited liability clause.

![Contract Engine: Llama 3.1 structured extraction from the GNU GPL v3](/images/contract-engine-analysis.png)
*Once the model decides the document is a contract, the analysis proceeds with confidence.*

This suggests that model behavior remains relatively stable for clearly defined document types, but becomes less reliable once categories are legally or semantically ambiguous – which, conveniently, remains a fairly common situation in law.

## Key Findings

1. **Local execution of the models was possible on modest hardware, but processing times were substantial.** Even relatively small documents required several minutes of processing, with full extraction taking up to 13 minutes on a standard, off-the-shelve laptop.
2. **Model agreement remained high for clearly defined document types.** Once the category became legally or semantically ambiguous, however, the models began to diverge.
3. **This turns model disagreement into a system design problem.** Without fine-tuning or additional guardrails, model outputs may vary significantly on ambiguous inputs.

## Implications

Local LLM inference already appears viable for privacy-sensitive pre-processing tasks such as:

- document classification
- contract detection
- metadata extraction

However, processing time remains a meaningful constraint. Multi-minute runtimes make fully local pipelines better suited to batch-style workflows than interactive applications.

In practice, deploying such systems would likely require a **hybrid architecture**.

Local models handle initial classification and preprocessing, while ambiguous or complex cases escalate to stronger models running in a controlled VPC environment.

Additional safeguards would also be necessary:

- more capable hardware to reduce processing time
- domain-specific fine-tuning to improve classification consistency
- validation layers to detect ambiguous or unreliable outputs

## Next Steps

Two directions appear particularly promising.

1. **Improving runtime performance and reliability.** This could involve smaller domain-tuned models or more efficient preprocessing pipelines to reduce the overall workload before inference.
2. **Hybrid architecture.** Adopting a hybrid setup. In such a system, local models handle initial document classification and preprocessing, while ambiguous or complex cases escalate to stronger models running in a controlled VPC environment.

This kind of hybrid pipeline may offer a practical balance between data privacy, performance, and model capability.

In other words: local models for triage, stronger models for judgment.
