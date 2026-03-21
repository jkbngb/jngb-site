---
title: "Regulation Radar: What Four LLMs Made of 890 EU Laws"
summary: "The EU published 890 pieces of binding legislation in six months – over five million words of regulations, decisions, and directives. We pointed four language models at the pile and checked their classifications against the human librarians who have been tagging EU law since 1995.<br><br>Not one regulation was classified identically by all four models. A 70B reasoning model that pauses to think before answering outperformed a 141B legal specialist trained specifically on law. <strong>The biggest model was not the best, and the most confident were not the most correct.</strong><br><br>But when the models did agree with each other, they tended to <strong>agree with the humans too</strong> – which turned out to be the more interesting finding."
date: "March 2026"
published: 2026-03-20
tags: ["eu-regulation", "cloud-gpu", "document-classification", "model-disagreement", "reasoning-models"]
stack: ["EUR-Lex", "Anthropic API", "EuroLLM:22B", "SaulLM:141B", "DeepSeek-R1:671B"]
---

## Quick Brief

- **Experiment:** Four open-source LLMs read 890 EU regulations and classified them by thematic domain and regulatory impact – one on a MacBook Air, the rest on rented H100s in Paris, no external API involved. Where possible, results were compared against EuroVoc, the EU's own classification system.
- **Why it matters:** The fact that LLMs can read regulation was never really in question. What actually matters is whether their output is consistent enough to act on – and what happens when you check it against human judgement.
- **Key finding:** A 70B reasoning model that pauses to think before answering outperformed a 141B legal specialist trained specifically on law. On most regulations, the models agreed on the core subject – but not one was classified identically by all four. When they did agree, accuracy against the human baseline went up. When they didn't, a human in the loop becomes advisable.

## Context

The neat thing about bureaucracies is that they produce vast amounts of structured text. Which, in theory, should make them ground zero for language models.

In the six months to March 2026 (17 September to 17 March, to be precise), the European Union published **890 pieces of binding legislation.** Over five million words of regulations, decisions, and directives – roughly ten times the length of *War and Peace*, published in half a year.

Somebody has to read all of that.

All EU legislation is publicly available through <a href="https://eur-lex.europa.eu/content/welcome/about.html" target="_blank">EUR-Lex</a> – well-known to EU legal practitioners and arguably invisible to everyone else. A <a href="https://publications.europa.eu/webapi/rdf/sparql" target="_blank">SPARQL endpoint</a> lets you query legislation like a database. A bulk download API called <a href="https://op.europa.eu/en/web/cellar" target="_blank">CELLAR</a> delivers full texts programmatically, in all 24 official EU languages, with structured metadata attached. A very well-organised government filing cabinet with an API.

![The EU's SPARQL endpoint – a query interface for legislation](/images/regulation-radar-sparql.png)
*The filing cabinet. With an API.*

But a filing cabinet is only useful if you know what is in it. Therefore, the EU doesn't just publish legislation – it **tags** it. Every regulation gets classified using <a href="https://op.europa.eu/en/web/eu-vocabularies/concept-scheme/-/resource?uri=http://eurovoc.europa.eu/100141" target="_blank">EuroVoc</a>, a controlled vocabulary of roughly 7,000 terms organised into **21 top-level thematic domains** – "Agriculture", "Trade", "Finance", "Energy", and so on. The tagging is done by professional librarians at the Publications Office, and has been running since 1995.

A <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> asked six models to classify ambiguous legal documents. They disagreed extensively – but there was no ground truth to grade against. This time, the librarians provided one, sort of – they tag each regulation with specific terms from EuroVoc's ~7,000 concept vocabulary, and those terms sit within a fixed hierarchy that maps them to the 21 top-level domains. The models were asked to pick domains directly. So the comparison is not quite apples to apples, but it is structured, consistent, and publicly available, which is considerably better than no benchmark at all.

The conventional approach to regulatory monitoring is to give the documents to a compliance officer, who reads them, asks ChatGPT which parts matter, and writes a summary (also with ChatGPT). The unconventional approach is to notice that **the filing cabinet already has an API** – and that language models can read. You do not put a steam engine on a horse. You build a railway.

## The Railway

Before any model reads anything, the data needs to arrive. The pipeline works in stages.

**Stage 1: Fetch.** A SPARQL query hits the EUR-Lex endpoint and retrieves all secondary legislation published in the last six months – 890 documents. For each: the CELEX identifier, title, date, document type, and the EuroVoc descriptors assigned by the human librarians. This is the ground truth we will grade against.

**Stage 2: Download.** The CELLAR API delivers the full text of each regulation. For our classification, the full text is overkill – a 400,000-word implementing regulation about carbon border adjustments does not need to be read in its entirety to know it belongs under "Energy" and "Trade". The pipeline extracts the **preamble**: title, recitals, and the opening articles. Typically 1,000–3,000 tokens – enough to understand what the regulation does, without drowning the model in annexes.

**Stage 3: Classify.** Each regulation gets **two prompts.** The <a href="/classify-sectors.txt" target="_blank">first</a> asks the model to assign the document to one or more of the 21 EuroVoc domains – the thematic "what is this about?" question. The <a href="/classify-impact.txt" target="_blank">second</a> asks for an **impact assessment**: is this ROUTINE (an administrative amendment nobody outside a specific agency will notice), MODERATE (new requirements for a specific sector), or HIGH (significant new obligations across multiple sectors, major compliance deadlines – on the scale of an AI Act or GDPR)?

**Stage 4: Route.** Regulations classified as **HIGH impact** get routed to a separate model for a detailed editorial briefing – what it does, who is affected, what the deadlines are, what the worst case looks like. Ideally, the full document goes in here, not just the preamble. This can run on the same infrastructure or a different machine entirely, depending on the model and the size of the legislation.

<div class="pipeline-lightbox">
<img src="/images/regulation-radar-pipeline.svg" alt="Pipeline: fetch, download, extract, classify domain, classify impact, route HIGH to briefing model, evaluate" style="width:100%;cursor:zoom-in;" onclick="this.parentElement.classList.toggle('expanded')" />
<div class="pipeline-overlay" onclick="this.parentElement.classList.remove('expanded')"></div>
</div>

*From SPARQL query to classified regulation. Swap the model, keep everything else. Click to enlarge.*

<style>
.pipeline-lightbox { position: relative; }
.pipeline-lightbox img { transition: none; }
.pipeline-overlay { display: none; }
.pipeline-lightbox.expanded .pipeline-overlay {
  display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 999; cursor: zoom-out;
}
.pipeline-lightbox.expanded img {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
  max-width: 92vw; max-height: 92vh; width: auto; z-index: 1000; cursor: zoom-out;
  background: white; padding: 1.5rem; border-radius: 6px;
}
</style>

In this experiment, the routing goes to **Claude Sonnet** via the Anthropic API. At this point we would typically publish the model and hardware specs with utmost transparency – unfortunately, Anthropic does not publish theirs. This is also the one step where data leaves the organisation's infrastructure, though it does not have to: the briefing model can run internally if the use case demands it.

The open-source models classified between 1 and 30 regulations as HIGH out of 890 – roughly 1–3% of the corpus. Only those get sent to the expensive model. The other 97–99% never leave the building, which is where most of the cost savings come from.

The experiment: run this pipeline with **four different models** at the classification stage. Same 890 regulations, same two prompts, same temperature (0.1), same routing logic. Then compare – with the humans, and with each other.

For those who would rather skip the technical details and see what four language models think your business should be worried about: <a href="/reg-radar/" target="_blank">all 890 regulations, classified and briefed, are browsable here</a>.

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

<a href="https://huggingface.co/Equall/SaulLM-141B-Instruct" target="_blank">**SaulLM-141B**</a> – the largest in the SaulLM family. The 7B ran on the laptop, the 54B ran in the <a href="/notes/better-call-saullm" target="_blank">previous experiment</a>, this one weighs in at 141 billion parameters. Same legal training data, twenty times the size of the MacBook model. The expectation was straightforward: bigger model, same specialisation, better results.

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

*Eight H100s before and after being put to work.*

**EuroLLM-22B:** 30.7 minutes, zero errors across 1,780 prompts. The EU's own model read 890 pieces of EU legislation and concluded that virtually nothing of consequence had happened – 79% ROUTINE, and exactly **one** regulation flagged as HIGH impact. A model of institutional composure, if nothing else.

**SaulLM-141B:** ~34 minutes, and **51 parse errors** – nearly 6% of documents where the model returned something other than valid JSON. This is one of the less charming features of large language models: even when the prompt says "respond in JSON format", a verbose model can wander off-format, returning explanatory paragraphs where a JSON object was expected, wrapping JSON in markdown code fences the parser does not anticipate, or simply deciding mid-response that a structured answer would benefit from a preamble. The biggest model in the experiment had the worst discipline.

**DeepSeek-R1-Distill-70B:** ~31 minutes, one parse error. Sixteen HIGH, 43% MODERATE, 56% ROUTINE – the most balanced distribution of the four, and the only model that looked like it had actually thought about the question before answering. Which, given that it is a reasoning model, is presumably the point.

Those impact numbers – one model flagging 30 regulations as HIGH, another flagging one – deserve a closer look.

## The Impact Question

EuroVoc does not tag regulations as "high-impact" or "routine". There is no ground truth for this question – we can only compare the models to each other. And they do not agree.

<table style="font-size:0.85rem;max-width:580px;">
<thead><tr><th style="text-align:left;">Model</th><th style="text-align:right;">Routine</th><th style="text-align:right;">Moderate</th><th style="text-align:right;">High</th></tr></thead>
<tbody>
<tr><td>SaulLM-7B</td><td style="text-align:right;">109 <small style="color:#888;">(12%)</small></td><td style="text-align:right;">735 <small style="color:#888;">(83%)</small></td><td style="text-align:right;">30 <small style="color:#888;">(3%)</small></td></tr>
<tr><td>EuroLLM-22B</td><td style="text-align:right;">702 <small style="color:#888;">(79%)</small></td><td style="text-align:right;">187 <small style="color:#888;">(21%)</small></td><td style="text-align:right;">1 <small style="color:#888;">(0.1%)</small></td></tr>
<tr><td>SaulLM-141B</td><td style="text-align:right;">633 <small style="color:#888;">(71%)</small></td><td style="text-align:right;">211 <small style="color:#888;">(24%)</small></td><td style="text-align:right;">15 <small style="color:#888;">(2%)</small></td></tr>
<tr><td>DeepSeek-R1 70B</td><td style="text-align:right;">496 <small style="color:#888;">(56%)</small></td><td style="text-align:right;">378 <small style="color:#888;">(43%)</small></td><td style="text-align:right;">16 <small style="color:#888;">(2%)</small></td></tr>
<tr><td colspan="4" style="border-top:1px solid #ddd;padding-top:0.3rem;"><small style="color:#888;">Rows not summing to 100% reflect parse errors – regulations where the model failed to return valid output.</small></td></tr>
</tbody>
</table>

*Same 890 regulations, same prompt. One model flags 30 as high-impact. Another flags one.*

SaulLM-7B sees danger everywhere. EuroLLM sees almost none. A regulatory monitoring system built on any single model's impact assessment would **either drown in false alarms or miss things that matter**, depending entirely on which model you picked.

What does this look like in practice? A compliance team using SaulLM-7B as their regulatory radar would receive 30 high-priority alerts from six months of legislation – roughly one per week. The same team using EuroLLM would receive one. Total. In six months. Both systems would report high confidence in every single assessment. Neither would mention that the other one exists.

There is an irony here worth savouring: the smallest model in the experiment – the one that performed worst on every other metric, as we will see shortly – is also the most alarmed. The model that understands EU regulation least is the one most convinced it is all terribly important.

But none of this tells us which regulations are *actually* high-impact. It tells us that pointing a language model at a document and asking "does this matter?" produces an answer that says more about the model than about the document. Which raises a more fundamental question: **are these models actually any good at reading regulation in the first place?**

## Checking the Answer Key

There is no official ranking of which EU regulations matter most, so the impact question cannot be graded directly. But there is a reasonable proxy: if a model cannot correctly identify what a regulation is *about*, it probably should not be trusted to tell you how important it is.

And for domain classification, we do have an answer key – the librarians at the Publications Office have been tagging these regulations for thirty years. Their domain assignments are the closest thing to a ground truth we have – not perfect, since they tag at the granular level and we map to the 21 top-level domains, but structured, consistent, and considerably better than guessing.

The overlap between a model's assignments and the librarians' gives us a score: 1.0 would mean perfect agreement. 0.0 would mean the model might as well have picked domains at random.

<table style="font-size:0.88rem;">
<thead><tr><th style="text-align:left;min-width:130px;">Model</th><th style="text-align:center;">Params</th><th style="text-align:center;">Hardware</th><th style="text-align:center;">Runtime</th><th style="text-align:center;">Overlap</th></tr></thead>
<tbody>
<tr><td>SaulLM-7B</td><td style="text-align:center;">7B</td><td style="text-align:center;">MacBook Air M3</td><td style="text-align:center;">940 min</td><td style="text-align:center;">0.33</td></tr>
<tr><td>EuroLLM-22B</td><td style="text-align:center;">22B</td><td style="text-align:center;">H100 ×8</td><td style="text-align:center;">31 min</td><td style="text-align:center;">0.47</td></tr>
<tr><td>SaulLM-141B</td><td style="text-align:center;">141B</td><td style="text-align:center;">H100 ×8</td><td style="text-align:center;">~34 min</td><td style="text-align:center;">0.50</td></tr>
<tr style="font-weight:600;"><td>DeepSeek-R1-70B</td><td style="text-align:center;">70B</td><td style="text-align:center;">H100 ×8</td><td style="text-align:center;">~31 min</td><td style="text-align:center;">0.56</td></tr>
</tbody>
</table>

*Overlap with thirty years of librarian classifications. 1.0 = perfect match. Nobody got close. DeepSeek won with half the parameters and no legal training data.*

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

Which brings us back to impact classification – the question with no answer key. If agreement predicts accuracy on domains, it stands to reason it does the same for impact. **A regulation that all four models independently flag as HIGH is worth reading.** A regulation where SaulLM-7B says HIGH and the other three say ROUTINE is probably SaulLM-7B being SaulLM-7B. Not proof – but considerably better than trusting whichever model you happened to install.

## What This Suggests

**No single model is worth listening to alone.** But when all four converge, accuracy against the human baseline jumps by 29%. Wisdom of crowds, applied to language models – independent errors cancel out, shared signal reinforces.

**Reasoning beats size.** A 70B model with chain-of-thought outperformed a 141B legal specialist on every metric. The model that thinks before answering gives better answers. More parameters did not compensate for not thinking.

**Confidence is decorative.** All four models reported confidence above 0.85 on virtually every classification – including the wrong ones. Self-reported confidence measures rhetorical commitment, not correctness. The <a href="/notes/better-call-saullm" target="_blank">previous experiment</a> found the same thing.

**A human in the loop is not optional.** The best model overlapped with the human baseline just over half the time. Put differently: if you handed someone a stack of 890 domain classifications and said "the model did these", roughly 44% of them would not match what the professional librarians assigned. A system that presents a single model's output as authoritative will be wrong nearly as often as it is right – and confident about it every time.

**Local hardware is not ready.** A 7B model on a MacBook takes sixteen hours and produces the worst results by a wide margin. The trajectory suggests a consumer laptop before 2030 could do meaningfully better. Whether it will be fast enough for real-time use remains to be seen.

## So What

EU regulation is an almost unreasonably good test case for language model classification. Clean documents, public ground truth, stable taxonomy, high volume. If LLMs are going to work anywhere in regulatory monitoring, they should work here. Under those near-ideal conditions, the best model agreed with the human baseline just over half the time.

Replacement is the wrong frame. The more useful question is whether LLM output, aggregated across multiple models, can tell you ***where to look.*** A regulation that all four models agree on probably does not need a human to review. A regulation where they split 2–2 probably does.

Four models processed five million words of regulation – the three on rented GPUs in under two hours, the one on a laptop overnight. Their disagreements are structured enough to be useful – if you build around them rather than ignoring them.

Which, to be fair, is also true of most bureaucrats.

<nav id="scroll-toc" aria-label="Article sections"></nav>

<style>
#scroll-toc {
  position: fixed;
  left: 1.2rem;
  top: 2rem;
  z-index: 90;
  list-style: none;
  padding: 0;
  margin: 0;
  opacity: 0;
  transition: opacity 0.3s;
  max-height: 80vh;
  overflow-y: auto;
}
#scroll-toc.visible { opacity: 0.4; }
#scroll-toc.visible:hover { opacity: 1; }
#scroll-toc a {
  display: block;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 0.68rem;
  line-height: 1.3;
  color: #b5a393;
  text-decoration: none;
  padding: 0.2rem 0 0.2rem 0.7rem;
  border-left: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
#scroll-toc a:hover { color: #6d5d4b; }
#scroll-toc a.active {
  color: #33302e;
  border-left-color: #33302e;
  font-weight: 600;
}
@media (max-width: 1280px) { #scroll-toc { display: none; } }
</style>

<script>
(function() {
  const toc = document.getElementById('scroll-toc');
  if (!toc) return;
  const headings = Array.from(document.querySelectorAll('article h2, .note-content h2, .prose h2'));
  if (headings.length === 0) return;

  headings.forEach(function(h) {
    if (!h.id) h.id = h.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    const a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent;
    a.addEventListener('click', function(e) {
      e.preventDefault();
      h.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    toc.appendChild(a);
  });

  var links = toc.querySelectorAll('a');
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        links.forEach(function(l) { l.classList.remove('active'); });
        var match = toc.querySelector('a[href="#' + entry.target.id + '"]');
        if (match) match.classList.add('active');
      }
    });
  }, { rootMargin: '-10% 0px -80% 0px' });

  headings.forEach(function(h) { observer.observe(h); });

  window.addEventListener('scroll', function() {
    toc.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
})();
</script>
