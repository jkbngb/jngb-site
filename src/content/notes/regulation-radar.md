---
title: "Regulation Radar: What Four LLMs Made of 890 EU Laws"
summary: "The EU published 890 regulations in six months. Five million words. Professional librarians have been classifying them since 1995. We pointed four language models at the same pile – one running on a MacBook Air, three on eight Nvidia H100 GPUs – and checked their homework against the humans.<br><br><strong>Not a single regulation was classified the same way by all four models.</strong> But a 70B reasoning model that pauses to think before answering outperformed a 141B legal specialist trained specifically on law.<br><br>The biggest model was not the best. The most confident were not the most correct. And when the models did agree, they were usually right."
date: "March 2026"
published: 2026-03-20
tags: ["eu-regulation", "cloud-gpu", "document-classification", "model-disagreement", "reasoning-models"]
stack: ["Anthropic API", "EuroLLM-22B", "SaulLM-7B", "SaulLM-141B", "DeepSeek-R1:671B"]
---

## Quick Brief

- **Experiment:** Four open-source LLMs read 890 EU regulations and classified them by thematic domain and regulatory impact – one on a MacBook Air, three on eight Nvidia H100 GPUs on a rented machine in Paris, no external API involved. Where possible, results were compared against EuroVoc, the EU's own classification system.
- **Why it matters:** LLMs can read regulation. That was never really in question. What actually matters is whether their output is consistent enough to act on, and what happens when you check it against human judgement.
- **Key finding:** A reasoning model half the size of a legal specialist produced better classifications. On most regulations, the models agreed on the core subject – but not one was classified identically by all four. When they did agree, their accuracy against the human baseline went up. When they didn't, you needed a person.

## Context

The neat thing about bureaucracies is that they produce vast amounts of structured text. Which, in theory, should make them ground zero for language models.

In the six months to March 2026, the European Union published **890 pieces of binding legislation.** Over five million words of regulations, decisions, and directives – roughly ten times the length of *War and Peace*, published in six months.

Somebody has to read all of that.

Every one of these 890 regulations is publicly available through <a href="https://eur-lex.europa.eu/content/welcome/about.html" target="_blank">EUR-Lex</a> – one of the **most thoroughly catalogued legal databases on the planet**, well-known to EU legal practitioners and largely invisible to everyone else. EUR-Lex is not a website you browse. It is infrastructure. A <a href="https://publications.europa.eu/webapi/rdf/sparql" target="_blank">SPARQL endpoint</a> lets you query legislation like a database. A bulk download API called <a href="https://op.europa.eu/en/web/cellar" target="_blank">CELLAR</a> delivers full texts programmatically, in all 24 official EU languages, with structured metadata attached. It is, essentially, a very well-organised government filing cabinet with an API.

But a filing cabinet is only useful if you know what is in it. The EU doesn't just publish legislation – it **tags** it. Every regulation gets classified using <a href="https://op.europa.eu/en/web/eu-vocabularies/concept-scheme/-/resource?uri=http://eurovoc.europa.eu/100141" target="_blank">EuroVoc</a>, a controlled vocabulary of roughly 7,000 terms organised into **21 top-level thematic domains** – "Agriculture", "Trade", "Finance", "Energy", and so on. The tagging is done by professional librarians at the Publications Office, and has been running since 1995.

The <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> in this series asked six models to classify ambiguous legal documents. They disagreed extensively – but there was no ground truth to grade against. This time, the librarians provided one. Sort of. EuroVoc classifications are derived – granular descriptors rolled up to 21 top-level domains – so the mapping is not always clean. But it is structured, consistent, and publicly available. Considerably better than no benchmark at all.

So: 890 regulations, a public taxonomy, and a human baseline to grade against. The conventional approach to regulatory monitoring is to give the documents to an analyst, who reads them, highlights the important bits, and has ChatGPT open in a second tab. The unconventional approach is to notice that **the filing cabinet already has an API** – and that language models can read. You do not put a steam engine on a horse. You build a railway.

## The Pipeline

Before any model reads anything, the data needs to arrive. The pipeline works in stages.

**Stage 1: Fetch.** A SPARQL query hits the EUR-Lex endpoint and retrieves all secondary legislation published in the last six months – 890 documents. For each: the CELEX identifier, title, date, document type, and the EuroVoc descriptors assigned by the human librarians. This is the ground truth we will grade against.

**Stage 2: Download.** The CELLAR API delivers the full text of each regulation. For classification, the full text is overkill – a 400,000-word implementing regulation about carbon border adjustments does not need to be read in its entirety to know it belongs under "Energy" and "Trade". The pipeline extracts the **preamble**: title, recitals, and the opening articles. Typically 1,000–3,000 tokens – enough to understand what the regulation does, without drowning the model in annexes.

**Stage 3: Classify.** Each regulation gets **two prompts.** The <a href="/classify-sectors.txt" target="_blank">first</a> asks the model to assign the document to one or more of the 21 EuroVoc domains – the thematic "what is this about?" question. The <a href="/classify-impact.txt" target="_blank">second</a> asks for an **impact assessment**: is this ROUTINE (an administrative amendment nobody outside a specific agency will notice), MODERATE (new requirements for a specific sector), or HIGH (significant new obligations across multiple sectors, major compliance deadlines – on the scale of an AI Act or GDPR)?

**Stage 4: Route.** A deliberate system design choice. If a regulation is classified as **HIGH impact**, the pipeline does not just log it and move on. For the genuinely important regulations – the ones a compliance team would actually need to read – you want the best available model writing the briefing, not the cheapest one. So the system immediately routes that regulation to **Claude Sonnet** via the Anthropic API for a detailed editorial summary: what the regulation does, who is affected, what the deadlines are, and what the worst-case consequence looks like. (Claude Sonnet's exact parameter count and infrastructure are not public – it is a frontier model running on Anthropic's hardware, not something you replicate on a rented GPU cluster.) The cheap open-source model does triage on all 890 documents. The expensive frontier model only sees the ~15 that matter. **95% cost savings** versus routing everything through Claude.

![Pipeline: fetch, download, extract, classify domain, classify impact, route HIGH to Claude, evaluate](/images/regulation-radar-pipeline.svg)
*The pipeline from query to classified corpus. The model is a swappable component – same pipeline, different model, different results.*

The experiment: run this pipeline with **four different models** at the classification stage. Same 890 regulations, same two prompts, same routing logic. Then compare – with the humans, and with each other.

## The Off-the-Shelf Option

If you are going to build a system like this, the dream is running it in real time. A regulation gets published, the pipeline picks it up, and a classified, assessed, briefed result appears in seconds. No cloud costs, no data leaving the machine, no vendor dependency.

The constraints of a consumer machine make that dream distant. An Apple MacBook Air with **16 GB of unified memory** can realistically run models up to about 7 billion parameters in quantised form. That rules out anything above the small end of the model spectrum.

Since we are dealing with legal text, the choice fell on an old acquaintance: <a href="https://huggingface.co/papers/2403.03883" target="_blank">**SaulLM-7B**</a>, a legal-domain model fine-tuned on court rulings and legislative text. It is the smaller sibling of the 54B model from the <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> – the one that needed an H100 to run. This one fits on a laptop.

The local setup uses the same components as the previous experiments: <a href="https://ollama.com/" target="_blank">**Ollama**</a> handles model management and serves the model as a local API. On Apple Silicon, it uses **Metal** for GPU acceleration – the M3's integrated GPU, not just the CPU. The model is a swappable component in the pipeline: same code, same prompts, different model running underneath. The bottleneck is the model doing inference on the GPU, not RAM or CPU.

It took **15 hours and 41 minutes.** Roughly one minute per regulation: read the preamble, classify by domain, assess impact, return a structured JSON response. 1,780 prompts total. Thirty watts.

That is slow enough that you would not want to sit and watch it, and fast enough that you can leave it running overnight and have results in the morning. But the real question is not speed – it is whether the results are any good. We will get to that shortly.

SaulLM-7B classified **30 regulations as HIGH impact** – more than any other model would. It rated 83% as MODERATE. Only 12% as ROUTINE. It produced 11 parse errors – documents where the model returned something other than valid JSON.

The MacBook Air is a remarkable piece of engineering. But just because it *can* run a language model on EU legislation overnight does not mean it *should.*

The more interesting question is **when local hardware catches up.** Not just in intelligence – a 2028 model with 7B parameters will likely be smarter than a 2026 one, thanks to better distillation and training techniques. But more importantly, in **speed.** Apple's M-series chips have delivered roughly 3x the machine learning inference throughput from M1 to M4 in four years. If dedicated inference chips – something beyond Apple's Neural Engine – join CPUs and GPUs as standard laptop components, a specialised model before 2030 might process a regulation in a few seconds rather than a minute. That would bring the total from sixteen hours down to perhaps thirty minutes.

Fast enough to run over a coffee break? Maybe. Fast enough for real-time monitoring of incoming legislation? Not yet. And for batch processing at scale – classifying hundreds of regulations at once – there will remain a need for something more powerful than what fits in a laptop. Which brings us to the rented hardware.

## More Power

If consumer hardware is not ready, specialised hardware should be. The question is whether throwing significantly more compute at the problem produces significantly better results – or just the same mediocre output, faster.

For the three remaining models, we rented a <a href="https://www.scaleway.com/en/" target="_blank">Scaleway</a> GPU instance in Paris. **Eight Nvidia H100 SXMs.** Eighty gigabytes of VRAM each, 640 GB total, connected via NVLink – a setup that could comfortably run most open-source models in existence (with one notable exception, as we would discover).

At €23 per hour, the clock was ticking from the moment the instance booted. The inference server was <a href="https://docs.vllm.ai/" target="_blank">**vLLM**</a> with **tensor parallelism** – meaning the model's weights are split across all eight GPUs so they work together as one, rather than each card running its own copy. This is what makes 140-billion-parameter models possible on hardware that only has 80 GB per card. The same pipeline code runs as on the laptop, with the model endpoint swapped from a local Ollama server to the remote vLLM instance. No external API, no data leaving the machine – the models run on rented hardware under our full control.

Three models, run sequentially:

<a href="https://huggingface.co/blog/eurollm-team/eurollm-22b" target="_blank">**EuroLLM-22B**</a> – yes, the EU funded the training of its own language model. Trained on all 24 official EU languages as part of the <a href="https://eurollm.eu/" target="_blank">EuroLLM project</a>, a consortium of European research institutions. This is the institutional candidate: the EU's model reading the EU's regulations.

<a href="https://huggingface.co/Equall/SaulLM-141B-Instruct" target="_blank">**SaulLM-141B**</a> – the big sibling of the laptop model. Same legal training data, twenty times the parameters. The expectation was straightforward: bigger model, same specialisation, better results.

And then there was <a href="https://huggingface.co/deepseek-ai/DeepSeek-R1" target="_blank">**DeepSeek-R1**</a>.

## 642 GB into 640 GB

The original plan included DeepSeek-R1 – the full **671-billion-parameter reasoning model** from the Chinese AI lab DeepSeek. At FP8 quantisation, its weights alone require approximately **642 GB of VRAM.**

The cluster has 640 GB.

Three attempts were made. Each produced an out-of-memory crash at the model-loading stage – before a single token of regulation was read. The weights themselves filled the GPUs to 98.7% capacity with zero bytes left for anything else. The model physically did not fit.

The pivot was <a href="https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B" target="_blank">**DeepSeek-R1-Distill-Llama-70B**</a> – the largest distilled reasoning variant. Distillation works like this: DeepSeek ran their full 671B model on a large set of problems, collected all the step-by-step reasoning traces it produced, and then used those traces as training data to teach a smaller model to reason the same way. The "student" in this case is **Meta's Llama 3 70B** – an American base model that learned Chinese-style chain-of-thought reasoning. At ~140 GB, it loaded with room to spare.

Why include a reasoning model at all? Most classification tasks do not require chain-of-thought. You read the text, you assign a label. But EU regulation is not always straightforward – a regulation about carbon border adjustments touches "Energy", "Trade", "Environment", and possibly "Industry" depending on how you read it. A model that **thinks through the ambiguity before committing to an answer** might handle those multi-domain cases better than one that just pattern-matches. This model produces visible `<think>` tokens – you can literally watch it reason, step by step, before it gives its final classification.

## The Runs

All three GPU models finished in about half an hour each.

![Eight H100 GPUs completely idle – 0 MiB, 0%](/images/regulation-radar-gpu-idle.png)
*Eight H100s sitting empty. 0 MiB VRAM, 0% utilisation, ~120 watts each.*

![All 8 GPUs at 100% utilization, 75 GB VRAM each](/images/regulation-radar-gpu-loaded.png)
*Model loaded. 75 GB per card, all eight at full utilisation. €23 per hour well spent.*

**EuroLLM-22B:** 30.7 minutes, zero errors across 1,780 prompts. It classified 79% of regulations as ROUTINE and flagged exactly **one** as HIGH impact.

**SaulLM-141B:** ~34 minutes, **51 parse errors** – nearly 6% of documents where the model returned something other than valid JSON. This happens because large language models generate free text, not structured data. Even when the prompt says "respond in JSON format", a verbose model can wander off-format: returning explanatory paragraphs where a JSON object was expected, wrapping JSON in markdown code fences the parser does not anticipate, or mixing natural language into the middle of a structured response. The biggest model in the experiment had the worst discipline.

**DeepSeek-R1-Distill-70B:** ~31 minutes, one parse error. Sixteen HIGH, 43% MODERATE, 56% ROUTINE – the most balanced distribution of the four.

## Checking the Answer Key

Before looking at how the models compare to each other, the first question is: **how do they compare to the humans?**

Each regulation in the EU corpus is tagged with one or more of the 21 EuroVoc domains by professional librarians. Each model was asked to do the same thing. The overlap between a model's domain assignments and the human assignments gives us a score: 1.0 would mean perfect agreement with the librarians. 0.0 would mean no overlap at all.

A reminder: this ground truth is **derived**. The librarians assign granular concept descriptors from a ~7,000-term vocabulary, which get rolled up to the 21 top-level domains. It is a reasonable benchmark, not a perfect one.

| Model | Params | Runtime | Overlap with humans |
|---|:---:|:---:|:---:|
| SaulLM-7B (MacBook) | 7B | 940 min | 0.33 |
| EuroLLM-22B (H100 x8) | 22B | 30.7 min | 0.47 |
| SaulLM-141B (H100 x8) | 141B | ~34 min | 0.50 |
| **DeepSeek-R1-70B (H100 x8)** | **70B** | **~31 min** | **0.56** |

*Overlap with humans: how closely each model's domain assignments match the librarians' classifications. 1.0 = perfect match, 0.0 = no overlap. DeepSeek is bold because it won.*

**The reasoning model wins.** What does that mean concretely? When DeepSeek assigns domains to a regulation, those domains overlap with the human librarians' assignments **56% of the time.** SaulLM-141B – twice the size, trained specifically on legal text – manages 50%. The model that pauses and thinks before answering beats the model with more parameters and more legal training data.

The size ordering would predict: 141B > 70B > 22B > 7B. The actual ordering is: **70B > 141B > 22B > 7B.** More parameters did not compensate for not thinking.

But 0.56 is not exactly a ringing endorsement. The best model agrees with the human librarians just over half the time. That raises the question of *where* it agrees and where it doesn't.

### Domain-level overlap with human classifications

<table style="font-size:0.78rem;">
<thead><tr><th style="text-align:left;min-width:140px;">Domain</th><th style="text-align:center;font-size:0.72rem;">Docs</th>
<th style="text-align:center;font-size:0.72rem;">SaulLM-7B</th>
<th style="text-align:center;font-size:0.72rem;">EuroLLM-22B</th>
<th style="text-align:center;font-size:0.72rem;">SaulLM-141B</th>
<th style="text-align:center;font-size:0.72rem;">DeepSeek-R1-70B</th>
</tr></thead><tbody>
<tr><td style="font-size:0.78rem;">Agriculture</td><td style="text-align:center;color:#888;">250</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">34%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">80%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">83%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">84%</td></tr>
<tr><td style="font-size:0.78rem;">International Relations</td><td style="text-align:center;color:#888;">300</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">57%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">78%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">80%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">79%</td></tr>
<tr><td style="font-size:0.78rem;">Agri-Foodstuffs</td><td style="text-align:center;color:#888;">198</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">18%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">71%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">73%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">76%</td></tr>
<tr><td style="font-size:0.78rem;">Geography</td><td style="text-align:center;color:#888;">457</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">9%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">8%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">33%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">75%</td></tr>
<tr><td style="font-size:0.78rem;">European Union</td><td style="text-align:center;color:#888;">413</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">67%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">60%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">71%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">65%</td></tr>
<tr><td style="font-size:0.78rem;">Environment</td><td style="text-align:center;color:#888;">176</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">40%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">70%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">66%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">70%</td></tr>
<tr><td style="font-size:0.78rem;">Finance</td><td style="text-align:center;color:#888;">96</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">22%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">56%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">51%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">67%</td></tr>
<tr><td style="font-size:0.78rem;">Employment</td><td style="text-align:center;color:#888;">34</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">4%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">38%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">38%</td><td style="text-align:center;background:rgba(40,140,40,0.35);border-radius:2px;font-family:monospace;font-size:0.76rem;">67%</td></tr>
<tr><td style="font-size:0.78rem;">Transport</td><td style="text-align:center;color:#888;">90</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">31%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">56%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">63%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">60%</td></tr>
<tr><td style="font-size:0.78rem;">Energy</td><td style="text-align:center;color:#888;">29</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">10%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">17%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">39%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">56%</td></tr>
<tr><td style="font-size:0.78rem;">Industry</td><td style="text-align:center;color:#888;">161</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">24%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">51%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">54%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">54%</td></tr>
<tr><td style="font-size:0.78rem;">Trade</td><td style="text-align:center;color:#888;">442</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">45%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">51%</td><td style="text-align:center;background:rgba(80,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">51%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">47%</td></tr>
<tr><td style="font-size:0.78rem;">Business & Competition</td><td style="text-align:center;color:#888;">113</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">10%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">46%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">–</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">32%</td></tr>
<tr><td style="font-size:0.78rem;">Law</td><td style="text-align:center;color:#888;">196</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">34%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">29%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">46%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">40%</td></tr>
<tr><td style="font-size:0.78rem;">Social Questions</td><td style="text-align:center;color:#888;">142</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">19%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">23%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">26%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">45%</td></tr>
<tr><td style="font-size:0.78rem;">Production & Research</td><td style="text-align:center;color:#888;">127</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">27%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">9%</td><td style="text-align:center;background:rgba(180,160,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">33%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">20%</td></tr>
<tr><td style="font-size:0.78rem;">Economics</td><td style="text-align:center;color:#888;">59</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">12%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">29%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">16%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">20%</td></tr>
<tr><td style="font-size:0.78rem;">Education</td><td style="text-align:center;color:#888;">151</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">28%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">8%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">7%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">21%</td></tr>
<tr><td style="font-size:0.78rem;">Politics</td><td style="text-align:center;color:#888;">86</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">16%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">14%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">24%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">25%</td></tr>
<tr><td style="font-size:0.78rem;">International Organisations</td><td style="text-align:center;color:#888;">24</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">4%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">13%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">15%</td><td style="text-align:center;background:rgba(180,100,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">17%</td></tr>
<tr><td style="font-size:0.78rem;">Science</td><td style="text-align:center;color:#888;">24</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">12%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">8%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">8%</td><td style="text-align:center;background:rgba(180,40,40,0.25);border-radius:2px;font-family:monospace;font-size:0.76rem;">15%</td></tr>
</tbody></table>

*Each cell shows how well a model captures a specific domain compared to the human librarians. Darker = better overlap. Some domains ("Agriculture", "International Relations") are consistently well-captured. Others ("Science", "Education") are missed by everyone.*

## Where They Agree

Each regulation can belong to multiple domains at once – a regulation on agricultural trade subsidies might correctly belong to "Agriculture", "Trade", and "Economics" simultaneously. Each model assigns its own combination of 2 to 6 domains per regulation. The question is whether those combinations overlap.

Across all 890 regulations, not a single one was classified with the *exact same* set of domains by all four models. That sounds like total disagreement. It is not.

Think of it this way: with 21 possible domains and each model picking a different number, the chances of four models independently landing on the exact same combination are vanishingly small. But that does not mean they disagree on what the regulation is *about*.

On **57% of regulations, all four models agreed on at least one domain** – they all identified the same core subject. On **98%, at least three out of four** agreed on at least one domain. On every single regulation without exception, at least two models found common ground. The disagreement is about **breadth**, not about core subjects. A sanctions regulation gets tagged "International Relations" by everyone. The debate is whether it also gets "Trade", "Energy", "Politics", or all three.

And here is the finding the experiment was built to test: on the documents where models substantially agreed, **accuracy against the human ground truth was 29% higher** than on the documents where they diverged. The sample is small – only 5 documents out of 826 crossed the high-agreement threshold. But the direction is consistent.

**When the models agree, the agreement tends to mean something. When they don't, that is where you need a human.**

## The Impact Question

So far, we have been comparing domain classifications against a human benchmark. The models overlap with the librarians roughly half the time – imperfect but structured. The next question has no answer key: **how do the models assess regulatory impact?**

EuroVoc does not tag regulations as "high-impact" or "routine". There is no ground truth to grade against here. We can only compare the models to each other – and they do not agree.

<table>
<thead><tr><th></th><th style="text-align:center;">SaulLM-7B</th><th style="text-align:center;">EuroLLM-22B</th><th style="text-align:center;">SaulLM-141B</th><th style="text-align:center;">DeepSeek-R1 70B</th></tr></thead>
<tbody>
<tr><td><strong>ROUTINE</strong><br><small>Administrative, technical</small></td><td style="text-align:center;">109<br><small>12.2%</small></td><td style="text-align:center;">702<br><small>78.9%</small></td><td style="text-align:center;">633<br><small>71.1%</small></td><td style="text-align:center;">496<br><small>55.7%</small></td></tr>
<tr><td><strong>MODERATE</strong><br><small>Sector-specific requirements</small></td><td style="text-align:center;">735<br><small>82.6%</small></td><td style="text-align:center;">187<br><small>21.0%</small></td><td style="text-align:center;">211<br><small>23.7%</small></td><td style="text-align:center;">378<br><small>42.5%</small></td></tr>
<tr><td><strong>HIGH</strong><br><small>Major obligations, multi-sector</small></td><td style="text-align:center;">30<br><small>3.4%</small></td><td style="text-align:center;">1<br><small>0.1%</small></td><td style="text-align:center;">15<br><small>1.7%</small></td><td style="text-align:center;">16<br><small>1.8%</small></td></tr>
</tbody>
</table>

*Same 890 regulations, same prompt. One model flags 30 as high-impact. Another flags one.*

SaulLM-7B sees danger everywhere. EuroLLM sees almost none. A regulatory monitoring system built on any single model's impact assessment would either **drown in false alarms or miss things that matter**, depending entirely on which model you picked. This is not a calibration problem you can tune away. The models have fundamentally different thresholds for what constitutes "significant."

## What This Suggests

**Reasoning beats size.** A 70B model with chain-of-thought outperformed a 141B legal specialist on every metric. The model that thinks before answering gives better answers. More parameters did not compensate for not thinking.

**Agreement is rare but structured.** Zero exact-match agreement, but 57% convergence on core domains. When models converge, accuracy goes up. Multi-model agreement is a better signal than any single model's confidence score.

**Confidence is decorative.** All four models reported confidence above 0.85 on virtually every classification – including the wrong ones, and including the ones where they flatly contradicted each other. On tasks of this complexity, self-reported confidence measures rhetorical commitment, not correctness. The <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> found the same thing: every model reported 90–100% confidence, including on the cases where they disagreed with each other.

**Local hardware is not ready.** A 7B model on a MacBook takes sixteen hours and produces the worst results by a wide margin. The trajectory suggests a consumer laptop before 2030 could do meaningfully better. Whether it will be fast enough for real-time use remains to be seen.

**A human in the loop is not optional.** The best model overlapped with the human baseline just over half the time. Put differently: if you handed someone a stack of 890 domain classifications and said "the model did these", roughly 44% of them would not match what the professional librarians assigned. A system that presents a single model's output as authoritative will be wrong nearly as often as it is right – and confident about it every time.

A note on the electricity: the MacBook ran at 30 watts for sixteen hours. The GPU cluster drew up to 3,400 watts – roughly a clothes dryer and an electric kettle running simultaneously – for about 95 minutes. Total GPU rental cost: ~€81. The cluster is 113x the power draw and roughly 675x the cost. It is also the only configuration that produces a result you could hand to someone with a straight face.

![GPU telemetry over the full session](/images/regulation-radar-gpu-telemetry.png)
*GPU telemetry. The brief spikes at 19:10 are the 671B model trying – and failing – to load. The sustained plateau is the 70B distill at full utilisation. Peak cluster draw: 4,482 watts.*

## So What

EU regulation is an almost unreasonably good test case for language model classification. Clean documents, public ground truth, stable taxonomy, high volume. If LLMs are going to work anywhere in regulatory monitoring, they should work here.

Under those near-ideal conditions, the best model overlapped with the human baseline **just over half the time.** That is nowhere near replacing the professional librarians who maintain EuroVoc.

But replacement is the wrong frame. The more useful question is whether LLM output, aggregated across multiple models, can tell you *where to look.* A regulation that all four models agree on probably does not need a human to review. A regulation where they split 2–2 probably does. And a system that flags the disagreements – rather than presenting a single model's confident verdict as fact – is more honest about what these models can and cannot do.

890 regulations. Four models. Five million words. The ones on rented GPUs finished in under two hours; the one on a laptop took overnight. They are cheap relative to human review at scale. And their disagreements are structured enough to be useful – if you build around them rather than ignoring them.

Which, to be fair, is also true of most bureaucrats.
