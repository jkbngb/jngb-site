---
title: "Regulation Radar: What Four LLMs Made of 890 EU Laws"
summary: "The EU published 890 pieces of binding legislation in six months – over five million words of regulations, decisions, and directives. We pointed four language models at the pile and checked their classifications against the human librarians who have been tagging EU law since 1995.<br><br>Not one regulation was classified identically by all four models. A 70B reasoning model that pauses to think before answering outperformed a 141B legal specialist trained specifically on law. <strong>The biggest model was not the best, and the most confident were not the most correct.</strong><br><br>But when the models did agree with each other, they tended to <strong>agree with the humans too</strong> – which turned out to be the more interesting finding."
date: "March 2026"
published: 2026-03-20
tags: ["eu-regulation", "cloud-gpu", "document-classification", "model-disagreement", "reasoning-models"]
stack: ["EUR-Lex", "Anthropic API", "EuroLLM:22B", "SaulLM:141B", "DeepSeek-R1:671B"]
---

## Quick Brief

- **Experiment:** Four open-source LLMs read 890 EU regulations and classified them by thematic domain and regulatory impact – one on a MacBook Air, three on eight Nvidia H100 GPUs on a rented machine in Paris, no external API involved. Where possible, results were compared against EuroVoc, the EU's own classification system.
- **Why it matters:** The fact that LLMs can read regulation was never really in question. What actually matters is whether their output is consistent enough to act on – and what happens when you check it against human judgement.
- **Key finding:** A 70B reasoning model that pauses to think before answering outperformed a 141B legal specialist trained specifically on law. On most regulations, the models agreed on the core subject – but not one was classified identically by all four. When they did agree, accuracy against the human baseline went up. When they didn't, a human in the loop becomes advisable.

## Context

The neat thing about bureaucracies is that they produce vast amounts of structured text. Which, in theory, should make them ground zero for language models.

In the six months to March 2026 (17 September to 17 March, to be precise), the European Union published **890 pieces of binding legislation.** Over five million words of regulations, decisions, and directives – roughly ten times the length of *War and Peace*, published in half a year.

Somebody has to read all of that.

All EU legislation is publicly available through <a href="https://eur-lex.europa.eu/content/welcome/about.html" target="_blank">EUR-Lex</a> – well-known to EU legal practitioners and largely invisible to everyone else. A <a href="https://publications.europa.eu/webapi/rdf/sparql" target="_blank">SPARQL endpoint</a> lets you query legislation like a database. A bulk download API called <a href="https://op.europa.eu/en/web/cellar" target="_blank">CELLAR</a> delivers full texts programmatically, in all 24 official EU languages, with structured metadata attached. A very well-organised government filing cabinet with an API.

![The EU's SPARQL endpoint – a query interface for legislation](/images/regulation-radar-sparql.png)
*The filing cabinet. With an API.*

But a filing cabinet is only useful if you know what is in it. Therefore, the EU doesn't just publish legislation – it **tags** it. Every regulation gets classified using <a href="https://op.europa.eu/en/web/eu-vocabularies/concept-scheme/-/resource?uri=http://eurovoc.europa.eu/100141" target="_blank">EuroVoc</a>, a controlled vocabulary of roughly 7,000 terms organised into **21 top-level thematic domains** – "Agriculture", "Trade", "Finance", "Energy", and so on. The tagging is done by professional librarians at the Publications Office, and has been running since 1995.

A <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> asked six models to classify ambiguous legal documents. They disagreed extensively – but there was no ground truth to grade against. This time, the librarians provided one, sort of – they tag each regulation with specific terms from EuroVoc's ~7,000 concept vocabulary, and those terms sit within a fixed hierarchy that maps them to the 21 top-level domains. The models were asked to pick domains directly. So the comparison is not quite apples to apples, but it is structured, consistent, and publicly available, which is considerably better than no benchmark at all.

The conventional approach to regulatory monitoring is to give the documents to a compliance officer, who reads them, asks ChatGPT which parts matter, and writes a summary (also with ChatGPT). The unconventional approach is to notice that **the filing cabinet already has an API** – and that language models can read. You do not put a steam engine on a horse. You build a railway.

## The Railway

Before any model reads anything, the data needs to arrive. The pipeline works in stages.

**Stage 1: Fetch.** A SPARQL query hits the EUR-Lex endpoint and retrieves all secondary legislation published in the last six months – 890 documents. For each: the CELEX identifier, title, date, document type, and the EuroVoc descriptors assigned by the human librarians. This is the ground truth we will grade against.

**Stage 2: Download.** The CELLAR API delivers the full text of each regulation. For classification, the full text is overkill – a 400,000-word implementing regulation about carbon border adjustments does not need to be read in its entirety to know it belongs under "Energy" and "Trade". The pipeline extracts the **preamble**: title, recitals, and the opening articles. Typically 1,000–3,000 tokens – enough to understand what the regulation does, without drowning the model in annexes.

**Stage 3: Classify.** Each regulation gets **two prompts.** The <a href="/classify-sectors.txt" target="_blank">first</a> asks the model to assign the document to one or more of the 21 EuroVoc domains – the thematic "what is this about?" question. The <a href="/classify-impact.txt" target="_blank">second</a> asks for an **impact assessment**: is this ROUTINE (an administrative amendment nobody outside a specific agency will notice), MODERATE (new requirements for a specific sector), or HIGH (significant new obligations across multiple sectors, major compliance deadlines – on the scale of an AI Act or GDPR)?

**Stage 4: Route.** Regulations classified as **HIGH impact** get routed to a separate model for a detailed editorial briefing – what it does, who is affected, what the deadlines are, what the worst case looks like. Ideally, the full document goes in here, not just the preamble. This can run on the same infrastructure or a different machine entirely, depending on the model and the size of the legislation.

![Pipeline: fetch, download, extract, classify domain, classify impact, route HIGH to briefing model, evaluate](/images/regulation-radar-pipeline.svg)
*From SPARQL query to classified regulation. Swap the model, keep everything else.*

In this experiment, the routing goes to **Claude Sonnet** via the Anthropic API. At this point we would typically publish the model and hardware specs with utmost transparency – unfortunately, Anthropic does not publish theirs. This is also the one step where data leaves the organisation's infrastructure, though it does not have to: the briefing model can run internally if the use case demands it.

The open-source models classified between 1 and 30 regulations as HIGH out of 890 – roughly 1–3% of the corpus. Only those get sent to the expensive model. The other 97–99% never leave the building, which is where most of the cost savings come from.

The experiment: run this pipeline with **four different models** at the classification stage. Same 890 regulations, same two prompts, same temperature (0.1), same routing logic. Then compare – with the humans, and with each other.

For those who would rather skip the technical details and see what four language models think your business should be worried about: <a href="/radar/" target="_blank">all 890 regulations, classified and briefed, are browsable here</a>.

## The Off-the-Shelf Option

Imagine this: a regulation gets published, and before you have finished your coffee, the pipeline has picked it up, classified it, assessed its impact, and produced a briefing – all on a laptop, no cloud costs, no data leaving the building.

That requires a model that actually fits on a laptop. An Apple MacBook Air with **16 GB of unified memory** can realistically run models up to about 7 billion parameters in quantised form, which rules out anything above the small end of the model spectrum. But small is still something.

Since we are dealing with legal text, the choice fell on an old acquaintance: <a href="https://huggingface.co/papers/2403.03883" target="_blank">**SaulLM-7B**</a>, a legal-domain model fine-tuned on court rulings and legislative text. It is the smaller sibling of the 54B model from the <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> – the one that needed an H100 to run. This one fits on a laptop. <a href="https://ollama.com/" target="_blank">**Ollama**</a> serves the model as a local API, using the M3's integrated GPU via Metal for inference.

![890 regulations downloaded and ready for classification](/images/regulation-radar-corpus.png)
*890 regulations, downloaded and waiting. Each one gets two prompts – domain and impact.*

890 regulations, two prompts each, fed through a 7B model on a laptop. It took **15 hours and 41 minutes** to get through all 1,780 prompts – roughly one minute per regulation to read the preamble, classify by domain, assess impact, and return a structured JSON response. You start it before bed, and by morning the laptop has opinions about 890 pieces of EU legislation.

Turns out, just because a MacBook Air *can* run a language model on EU legislation overnight does not mean it *should.*

Classifying hundreds of regulations at once – the actual use case for a regulatory monitoring system – requires something substantially more powerful than what fits in a laptop.

## "More Power!"

The <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> ran on a single Nvidia H100. This time, the plan was to test SaulLM-141B – twenty times the size of the laptop model – which does not fit on a single GPU. So what is better than one Nvidia H100? The answer, naturally, is eight Nvidia H100s.

A <a href="https://www.scaleway.com/en/" target="_blank">Scaleway</a> GPU instance with that kind of quota required a short phone call with Paris to request approval – and a promise not to block the machine too long. At €23 per hour, one might assume they would have every incentive to let you keep it running, but apparently not.

Request granted: **eight H100 SXMs**, eighty gigabytes of VRAM each, 640 GB total, connected via NVLink – a setup that could comfortably run most open-source models in existence, with one notable exception.

With the clock ticking, the first order of business was downloading 1.3 terabytes of model weights from <a href="https://huggingface.co/" target="_blank">Hugging Face</a> – 35 minutes of eight GPUs sitting completely idle. The inference server of choice was <a href="https://docs.vllm.ai/" target="_blank">**vLLM**</a> with **tensor parallelism**: the model's weights split across all eight GPUs so they work together as one, which is what makes 140-billion-parameter models possible on hardware with 80 GB per GPU.

The pipeline code is identical to the laptop setup – same prompts, same routing logic – with the model endpoint swapped from a local Ollama server to the remote vLLM instance. No third-party API, no data shared externally.

Three models, ran sequentially:

<a href="https://huggingface.co/blog/eurollm-team/eurollm-22b" target="_blank">**EuroLLM-22B**</a> – yes, the EU funded the training of its own language model. Trained on all 24 official EU languages as part of the <a href="https://eurollm.io/" target="_blank">EuroLLM project</a>, a consortium of European research institutions. This is the institutional candidate: the EU's model reading the EU's regulations.

<a href="https://huggingface.co/Equall/SaulLM-141B-Instruct" target="_blank">**SaulLM-141B**</a> – the big sibling of the laptop model. Same legal training data, twenty times the parameters. The expectation was straightforward: bigger model, same specialisation, better results.

And then there was <a href="https://huggingface.co/deepseek-ai/DeepSeek-R1" target="_blank">**DeepSeek-R1**</a>.

## 642 GB into 640 GB

The original plan included DeepSeek-R1 – the full **671-billion-parameter reasoning model** from the Chinese AI lab DeepSeek. At FP8 quantisation, its weights alone require approximately **642 GB of VRAM.**

The cluster has 640 GB.

Three attempts were made. Each produced an out-of-memory crash at the model-loading stage – before a single token of regulation was read. The weights themselves filled the GPUs to 98.7% capacity with zero bytes left for anything else. The model physically did not fit.

The pivot was <a href="https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B" target="_blank">**DeepSeek-R1-Distill-Llama-70B**</a> – the largest distilled reasoning variant. Distillation works like this: DeepSeek ran their full 671B model on a large set of problems, collected all the step-by-step reasoning traces it produced, and then used those traces as training data to teach a smaller model to reason the same way (<a href="https://arxiv.org/pdf/2501.12948" target="_blank">paper</a>). The "student" in this case is **Meta's Llama 3 70B** – an American base model that learned Chinese-style chain-of-thought reasoning. At ~140 GB, it loaded with room to spare.

Why include a reasoning model at all? Most classification tasks do not require chain-of-thought. You read the text, you assign a label. But EU regulation is not always straightforward – a regulation about carbon border adjustments touches "Energy", "Trade", "Environment", and possibly "Industry" depending on how you read it. A model that **thinks through the ambiguity before committing to an answer** might handle those multi-domain cases better than one that just pattern-matches. This model produces visible `<think>` tokens – you can literally watch it reason, step by step, before it gives its final classification.

All three GPU models finished in about half an hour each.

<div class="gpu-slider" style="position:relative;max-width:100%;overflow:hidden;border:1px solid #ddd;border-radius:4px;user-select:none;">
<img src="/images/regulation-radar-gpu-loaded.png" alt="After: 8 H100 GPUs at full load – 75 GB VRAM each" style="width:100%;display:block;" />
<div class="gpu-slider-overlay" style="position:absolute;top:0;left:0;width:50%;height:100%;overflow:hidden;pointer-events:none;">
<img src="/images/regulation-radar-gpu-idle.png" alt="Before: 8 H100 GPUs idle – 0 MiB VRAM" style="display:block;min-width:100%;width:100%;height:100%;object-fit:cover;" />
</div>
<div style="position:absolute;top:0;bottom:0;left:50%;width:3px;background:#8C6239;pointer-events:none;z-index:5;" class="gpu-slider-line"></div>
<input type="range" min="0" max="100" value="50" style="position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;cursor:ew-resize;z-index:10;margin:0;" />
<div style="position:absolute;top:8px;left:8px;background:rgba(0,0,0,0.6);color:#fff;padding:2px 8px;border-radius:3px;font-size:0.75rem;pointer-events:none;">Before</div>
<div style="position:absolute;top:8px;right:8px;background:rgba(0,0,0,0.6);color:#fff;padding:2px 8px;border-radius:3px;font-size:0.75rem;pointer-events:none;">After</div>
</div>

*Drag to compare. Eight H100s idle versus eight H100s at full utilisation.*

**EuroLLM-22B:** 30.7 minutes, zero errors across 1,780 prompts. It classified 79% of regulations as ROUTINE and flagged exactly **one** as HIGH impact.

**SaulLM-141B:** ~34 minutes, **51 parse errors** – nearly 6% of documents where the model returned something other than valid JSON. This happens because large language models generate free text, not structured data. Even when the prompt says "respond in JSON format", a verbose model can wander off-format: returning explanatory paragraphs where a JSON object was expected, wrapping JSON in markdown code fences the parser does not anticipate, or mixing natural language into the middle of a structured response. The biggest model in the experiment had the worst discipline.

**DeepSeek-R1-Distill-70B:** ~31 minutes, one parse error. Sixteen HIGH, 43% MODERATE, 56% ROUTINE – the most balanced distribution of the four.

## Checking the Answer Key

Four models have now classified 890 regulations. They were fast, they were confident, and they all produced structured output. The question nobody has answered yet: **were any of them right?**

The librarians at the Publications Office have been tagging these regulations for thirty years. Their domain assignments are the closest thing to a ground truth we have – not perfect, since they tag at the granular level and we map to the 21 top-level domains, but structured, consistent, and considerably better than guessing. The overlap between a model's assignments and the librarians' gives us a score: 1.0 would mean perfect agreement. 0.0 would mean the model might as well have picked domains at random.

| Model | Params | Hardware | Runtime | Overlap with humans |
|:---:|:---:|:---:|:---:|:---:|
| SaulLM-7B | 7B | MacBook Air M3 | 940 min | 0.33 |
| EuroLLM-22B | 22B | H100 x8 | 30.7 min | 0.47 |
| SaulLM-141B | 141B | H100 x8 | ~34 min | 0.50 |
| **DeepSeek-R1-70B** | **70B** | **H100 x8** | **~31 min** | **0.56** |

*Overlap with humans: how closely each model's domain assignments match the librarians' classifications. 1.0 = perfect match, 0.0 = no overlap. DeepSeek is bold because it won.*

**The reasoning model wins.** What does that mean concretely? When DeepSeek assigns domains to a regulation, those domains overlap with the human librarians' assignments **56% of the time.** SaulLM-141B – twice the size, trained specifically on legal text – manages 50%. The model that pauses and thinks before answering beats the model with more parameters and more legal training data.

The size ordering would predict: 141B > 70B > 22B > 7B. The actual ordering is: **70B > 141B > 22B > 7B.** More parameters did not compensate for not thinking.

But 0.56 is not exactly a ringing endorsement. If the best model assigns five domains to a regulation, roughly two or three of them will match the librarians' choices – and the rest won't. Good enough to tell you what a regulation is broadly about. Not good enough to replace the person who reads it.

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

*Darker green = closer to the librarians. "Agriculture" and "International Relations" are easy. "Science" and "Education" are near-invisible to all four models.*

## Where They Agree

Here is the number that sounds worst: across all 890 regulations, **not a single one** was classified with the exact same set of domains by all four models. Zero. None.

That sounds like total disagreement, but it is not. A regulation can belong to multiple domains at once – a regulation on agricultural trade subsidies might correctly belong to "Agriculture", "Trade", and "Economics" simultaneously. Each model picks its own combination of 2 to 6 domains. With 21 possible domains, the chances of four models independently landing on the exact same combination are vanishingly small. But that does not mean they disagree on what the regulation is *about*.

On **57% of regulations, all four models agreed on at least one domain** – they all identified the same core subject. On **98%**, at least three out of four found common ground. The disagreement is about **breadth**, not about core subjects. A sanctions regulation gets tagged "International Relations" by everyone. The debate is whether it also gets "Trade", "Energy", "Politics", or all three.

Which brings us to the finding the experiment was built to test: on the documents where models substantially agreed, **accuracy against the human ground truth was 29% higher** than on the documents where they diverged. When all four models converge on a domain, that domain tends to match what the librarians assigned. When they split, the classifications drift.

In other words: multi-model agreement is a better predictor of correctness than any single model's confidence score. And when the models don't agree, that is exactly where you want a human looking at the document.

## The Impact Question

Everything above had an answer key – imperfect, derived, but real. The next question has none: **how do the models assess regulatory impact?**

EuroVoc does not tag regulations as "high-impact" or "routine". There is no ground truth here. We can only compare the models to each other – and they do not agree.

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

**Confidence is decorative.** All four models reported confidence above 0.85 on virtually every classification – including the wrong ones, and including the ones where they flatly contradicted each other. On tasks of this complexity, self-reported confidence measures rhetorical commitment, not correctness. The <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> found the same thing: every model reported 90–100% confidence, including on the cases where they disagreed with each other.

**Agreement is rare but structured.** Zero exact-match agreement, but 57% convergence on core domains. When models converge, accuracy goes up. Multi-model agreement is a better signal than any single model's confidence score.

**Local hardware is not ready.** A 7B model on a MacBook takes sixteen hours and produces the worst results by a wide margin. The trajectory suggests a consumer laptop before 2030 could do meaningfully better. Whether it will be fast enough for real-time use remains to be seen.

**A human in the loop is not optional.** The best model overlapped with the human baseline just over half the time. Put differently: if you handed someone a stack of 890 domain classifications and said "the model did these", roughly 44% of them would not match what the professional librarians assigned. A system that presents a single model's output as authoritative will be wrong nearly as often as it is right – and confident about it every time.

A note on the electricity: the MacBook ran at 30 watts for sixteen hours. The GPU cluster drew up to 3,400 watts – roughly a clothes dryer and an electric kettle running simultaneously – for about 95 minutes. Total GPU rental cost: ~€81. The cluster is 113x the power draw and roughly 675x the cost. It is also the only configuration that produces a result you could hand to someone with a straight face.

![GPU telemetry over the full session](/images/regulation-radar-gpu-telemetry.png)
*GPU telemetry. The brief spikes at 19:10 are the 671B model trying – and failing – to load. The sustained plateau is the 70B distill at full utilisation. Peak cluster draw: 4,482 watts.*

## So What

EU regulation is an almost unreasonably good test case for language model classification. Clean documents, public ground truth, stable taxonomy, high volume. If LLMs are going to work anywhere in regulatory monitoring, they should work here. Under those near-ideal conditions, the best model agreed with the human baseline just over half the time.

Replacement is the wrong frame. The more useful question is whether LLM output, aggregated across multiple models, can tell you *where to look.* A regulation that all four models agree on probably does not need a human to review. A regulation where they split 2–2 probably does.

Four models processed five million words of regulation – the three on rented GPUs in under two hours, the one on a laptop overnight. Their disagreements are structured enough to be useful – if you build around them rather than ignoring them.

Which, to be fair, is also true of most bureaucrats.
