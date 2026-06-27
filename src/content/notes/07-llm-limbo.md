---
title: "LLM Limbo: Quantising Gemma 4 to Bits and Pieces"
summary: "Quantisation is rounding. Round a model's weights to fewer bits and one of two things happens: the same model now fits on smaller, cheaper hardware, or the high-end GPU has room to spare for many more parallel jobs. Either way, the bill drops.<br><br>Google's Gemma 4 &ndash; a new open-weight model that <strong>reads text but also processes pictures and audio</strong> &ndash; was put through progressively lower precisions across three sizes, from a 31-billion-parameter flagship down to a 2.3-billion-parameter phone-sized featherweight, to find where compression starts to break things.<br><br>Text reading held all the way down to three bits per weight. Vision broke first; at two bits, the model produced random tokens and nothing more. <strong>Compression is gentle on easy tasks and ruinous on hard ones</strong> &ndash; the trick is matching the model to the job, not the other way round."
date: "June 2026"
published: 2026-05-25
tags: ["quantization", "local-llm", "multimodal", "benchmark"]
stack: ["Gemma-4", "FP8", "AWQ", "GPTQ", "HQQ"]
---

## Quick Brief

- **Experiment:** We took quantised versions of Google's Gemma 4 and ran them through two tasks &ndash; reading invoices as text, and as images &ndash; then pushed quantisation further to see how far Gemma 4 can be crushed before it breaks.
- **Why it matters:** Inference is where AI gets expensive. Quantisation &ndash; running models in lower precision so they fit on smaller, cheaper hardware &ndash; is the standard way to bring the GPU bill down. The pitch (shrink the model by 75%, lose nothing) is appealing and therefore needs testing.
- **Key finding:** Compression had no measurable effect on simple tasks like reading text, even at three bits per weight. Complex tasks &ndash; reading from images &ndash; degraded much faster. The economic upside is not just faster inference but cheaper kit: the same model either fits on smaller, cheaper hardware, or packs many more parallel jobs onto a single H100.

## Context

It has become a cliché to say AI is going commodity. Clichés earn their reputation for a reason.

A commodity is what you get when **every supplier's product is basically the same**, the price drifts toward marginal cost, customers stop caring who made it, and competition migrates from the shop floor to the back office. The textbook example is electricity: a kilowatt-hour is a kilowatt-hour, nobody pays extra for *artisanal* electricity, and the customer remembers only the bill.

Language models are heading the same way. The quality gap between providers shrinks each quarter, and at the same time agentic pipelines are breaking the work into many small chained calls, which means **no single call has to be brilliant when fifty more follow it**. Both pressures push in the same direction: what providers compete on becomes cost per call, latency, and throughput. Welcome to the meter.

Every utility, eventually, has its efficiency moment. For electricity it was the LED bulb: same brightness, a tenth of the watts, identical fitting. The room stayed exactly as bright; electricity consumption quietly dropped by a factor of ten.

For language models, the equivalent has been sitting in plain sight for years. It is called *rounding*.

## Matrix Multiplications All the Way Down

At its core, AI is matrix multiplication. Strip away the chatbot interface, the helpful personality, the carefully tuned refusals and the trillion words of training data, and at the bottom you find one operation, done a lot.

From the outside it feels like magic. Up close, it is high-school linear algebra: the input gets encoded as a list of numbers, multiplied by a matrix of trained weights, fed into the next matrix, and so on for anywhere from a few dozen layers to several hundred. Done at industrial scale, this pedestrian operation has shown an <a href="https://karpathy.github.io/2015/05/21/rnn-effectiveness/" target="_blank">unreasonable effectiveness</a> at imitating the written word.

<img src="/images/articles/07-llm-limbo/matrix-tweet.png" alt="Tweet by @forloopcodes: 'i still can't believe this is your virtual girlfriend' over a 3x3 matrix multiplication" style="max-width:480px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>High-school linear algebra, in production.</em></p>

The funny thing about modern AI chips is that they are not really constrained by maths any more. An H100 can multiply numbers together at <a href="https://resources.nvidia.com/en-us-hopper-architecture/nvidia-tensor-core-gpu-datasheet" target="_blank">frankly irresponsible speeds</a>. **The problem is getting the numbers to the chip quickly enough.**

Picture a kitchen where the chefs can chop a thousand carrots a second, but the runners delivering carrots arrive one at a time. The chefs are fast; the runners are the bottleneck, so the chefs spend most of their day with knives in hand, waiting for the next carrot to arrive. This limitation is known as **memory wall**. The H100, currently the de facto industry standard, shifts roughly three trillion bytes a second across its memory bus &ndash; a great deal of carrot, still not enough to keep the chefs busy.

Quantisation helps because the chunks of carrot being delivered get smaller: each runner now carries more per trip. A 1024-bit memory bus can carry sixty-four 16-bit weights per cycle, twice as many 8-bit ones, or four times as many 4-bit ones. **Same lane, smaller parcels, more throughput.**

Rounding numbers is straightforward. Rounding them without breaking the network is a small academic field of its own. The flavour we care about here is **weight quantisation &ndash; rounding the model's parameters after training is done**. The field splits into a zoo of acronyms (GPTQ, AWQ, HQQ, K-quants, and a dozen more) &ndash; introduced each as it shows up.

A motivated AI engineer could quantise a model from scratch. The good ones don't re-invent the wheel. They go to the wheel shop &ndash; <a href="https://huggingface.co/" target="_blank">HuggingFace</a>, in this trade &ndash; and on the subject of quantised Gemma 4, it is well stocked. Where it isn't, we'll make the wheel ourselves. That bridge for later.

## Setting the Bar

David Hasselhoff is unlikely to feature prominently in the history of artificial intelligence. He should. Decades before ChatGPT, he was already holding extended conversations with KITT, the artificially intelligent Pontiac Trans Am from *Knight Rider*. Hasselhoff was, by some margin, the more replaceable component of the partnership.

He also recorded what may retrospectively qualify as the first mainstream song about weight quantisation: the 1991 single "<a href="https://www.youtube.com/watch?v=38JdxqN6hLo" target="_blank">Do the Limbo Dance</a>". Admittedly this requires a slightly aggressive reading of the lyrics. But once seen, it cannot be unseen: confronted with a low bar held by two strangers, the Hoff argues that the only correct response is to bend backwards and pass under it. The lower the bar, the better the dancer.

<img src="https://m.media-amazon.com/images/I/61pqUtq5ssL.jpg" alt="David Hasselhoff, Do the Limbo Dance single cover" style="max-width:272px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>The Hoff, visibly thrilled at the prospect of activation-aware per-channel weight quantisation with group-wise scaling factors.</em></p>

The dancer, when it comes to quantisation, is the model. The bar is the number of bits assigned to each weight. "How low can you go?" turns out to be one of the central operational questions in modern AI: **every reduction in precision makes models cheaper to run, easier to fit into memory and faster to serve**. Lower the bar too far and the dancer hits the floor &ndash; or the model stops working, which in this metaphor amounts to the same thing.

The wheel shop &ndash; HuggingFace, again &ndash; sells more than wheels. It also stocks datasets, and on this particular shelf we knew what to look for, because we had stocked it ourselves: <a href="https://huggingface.co/datasets/jngb-labs/InvoiceBenchmark" target="_blank">the 200 synthetic invoices</a> from a <a href="/notes/06-too-dangerous-to-release" target="_blank">previous experiment</a>, each with a known correct total, forty deliberately broken. Each invoice goes in twice &ndash; once as plain text, once as an image. Two questions every time. *What is the total? Do the numbers add up?*

<a href="/article-07-prompt.txt" target="_blank">The prompt</a> was intentionally austere: no chain-of-thought, no system preamble, just the document and the question. The point was to take everything else out of the equation and watch what compression alone does to an almost insultingly simple task.

## The Dancers

Our model of choice is Google's new kid on the block: Gemma 4. The family comes in four sizes &ndash; a 31B flagship, a 26B Mixture-of-Experts sibling, a 4.5B laptop model, and a 2.3B phone-sized featherweight. We left the MoE for another day and stuck to the three dense models.

All members of the family ship with senses bolted on &ndash; a vision encoder and an audio tower, on top of what was, until recently, just a next-word predictor. Open-weight phone-sized models that read pictures and process audio are a recent development; not long ago this lived only behind closed APIs. More on the eyes shortly.

Back at the wheel shop, the 31B aisle was well stocked: <a href="https://huggingface.co/google/gemma-4-31B-it" target="_blank">BF16 from Google</a>, <a href="https://huggingface.co/RedHatAI/gemma-4-31B-it-FP8-block" target="_blank">FP8 from Red Hat</a>, <a href="https://huggingface.co/QuantTrio/gemma-4-31B-it-AWQ" target="_blank">AWQ Q4 from QuantTrio</a>. One of each into the trolley. The 4.5B aisle had a community-maintained <a href="https://huggingface.co/Vishva007/gemma-4-E4B-it-W4A16-AutoRound-GPTQ" target="_blank">4-bit GPTQ build</a> from an individual contributor; that one in too. The 2.3B model had no under-four-bit options &ndash; we would have to make that wheel ourselves, in a moment.

By 2026 standards the 31B is modest &ndash; frontier closed-source models are an order of magnitude bigger &ndash; but 59&nbsp;GiB of weights does not fit on a 16&nbsp;GB MacBook Air. So we had to resort to our Neocloud of choice, <a href="https://www.scaleway.com/en/" target="_blank">Scaleway</a>, to rent out a single Nvidia H100 for &euro;2.73 an hour (served via vLLM in an <a href="https://hub.docker.com/r/vllm/vllm-openai/tags" target="_blank">official Docker image</a>, because pip refused to cooperate). The bar is set. The heavyweight walks up to it first.

## Round One: The Heavyweight Bends

Welcome to the warm-up round. A 31-billion-parameter language model is about to read a total off a synthetic invoice &ndash; not exactly frontier reasoning, somewhere between asking what is two plus two and what colour is the sky. This is a sanity check, before we start crushing things.

<img src="/images/articles/07-llm-limbo/invoice-umbrella.png" alt="INV-2026-0042 from Umbrella Corporation" style="max-width:520px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>INV-2026-0042 from Umbrella Corporation. In unrelated news, Milla Jovovich, formerly in the killing-zombies line of work, has lately <a href="https://github.com/milla-jovovich" target="_blank">moved into open-source AI</a>.</em></p>

The bar is set at sixteen bits &ndash; full height, no bending required. The model arrives at full precision (BF16, the format Google shipped it in). Two hundred invoices in, two hundred correct totals out. 100 per cent, at 1.10 seconds per invoice. A spectator at the back points out the model is not actually quantised yet, and returns to their drink.

The bar drops to eight bits. To clear it, the model is compressed using **FP8 &ndash; every weight now stored in half the digits it had before**. Uniform rounding, no favourites. 100 per cent, now at 0.77 seconds per invoice. Polite applause.

Bar drops to four bits. The method this time is **AWQ &ndash; same idea as FP8, but with a twist: a brief calibration pass picks out the weights that matter most and rounds those less harshly than the rest.** 100 per cent, in 0.60 seconds. Sanity check complete. Warm-up over.

The quantisation literature is full of elegant curves showing graceful accuracy degradation as precision falls. Ours resembled a ruler laid flat on the page. On a task this simple, fewer bits bought faster inference and nothing else.

The seats are filling up. The next contender approaches the bar &ndash; same model, same precision, but **this time it has to see the invoice rather than read it**. That a language model can see at all is the interesting bit now.

## Round Two: The Models Have Eyes

One of the things that makes Gemma 4 special is that it can also see and listen. A language model, as the name suggests, only processes text &ndash; pictures have to be converted into something it can read first.

The trick is to bolt on a translator. A vision encoder &ndash; a separate neural network &ndash; chops the image into patches and converts each into a vector of numbers; a small adapter hands those vectors to the language model in the format it uses for words. The model never sees a picture; **it reads a description of the picture, written by an encoder with opinions of its own about what it just looked at.** The whole pipeline now depends on that encoder being reliable. If it misreads a digit, the language model has no way to know. The definition of garbage in, garbage out.

Back to the limbo floor. Same 31B, same H100, same prompt &ndash; **invoices arriving as PNGs instead of plain text**. The bar is back at full height.

A new contestant approaches. The dancer reaches the bar. And &ndash; *oh, what's this?* The dancer touches the bar! A first! The dancer keeps going, clears it: 90.5 per cent at 1.15 seconds per invoice. One hundred and eighty-one read correctly, nineteen missed, before we have touched a single bit.

The replays roll on what went wrong: thousands separators going missing, negative signs falling off, refunds posting as charges. The encoder is fumbling small details; the language model passes whatever it gets along.

Bar drops to eight bits, same FP8 build as before. The score goes up to 91.5 per cent &ndash; surprising, but well within noise range. Polite, almost suspicious applause.

Bar drops to four bits. The crowd leans in.

0 per cent. The dancer reaches the bar; the bar comes crashing down.

The four-bit AWQ build, it turns out, does not actually support Gemma 4's vision encoder. **Feed it an image and the multimodal pipeline quietly returns nothing useful.** The kind of failure a benchmark catches in an afternoon and a production deployment finds three weeks after launch.

Halfway through the card, the scoreboard looks like this:

<table>
<thead>
<tr>
<th style="text-align:left;">Model</th>
<th style="text-align:center;">Bits</th>
<th style="text-align:left;">Method</th>
<th style="text-align:left;">What it does</th>
<th style="text-align:center;">Text</th>
<th style="text-align:center;">Vision</th>
</tr>
</thead>
<tbody>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">16</td><td><a href="https://en.wikipedia.org/wiki/Bfloat16_floating-point_format" target="_blank">BF16</a></td><td>Full precision &ndash; the model as Google shipped it</td><td style="text-align:center;">100%</td><td style="text-align:center;">90.5%</td></tr>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">8</td><td><a href="https://www.exxactcorp.com/blog/hpc/what-is-fp8-fp6-fp4" target="_blank">FP8</a></td><td>Half the bits per weight, pre-rounded by Red Hat</td><td style="text-align:center;">100%</td><td style="text-align:center;">91.5%</td></tr>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">4</td><td><a href="https://huggingface.co/papers/2306.00978" target="_blank">AWQ</a></td><td>Quarter of the bits, with a calibration pass to protect the important weights</td><td style="text-align:center;">100%</td><td style="text-align:center;">0%</td></tr>
</tbody>
</table>

<small>Three precisions, two modalities, the same H100 and the same prompt. The text column has not moved. The vision column has either held or collapsed.</small>

Time to shrink the dancer.

## Round Three: The Mid-Card

A smaller dancer takes the floor. The E4B &ndash; 4.5 billion parameters, Google's "laptop class," a sixth the size of the 31B. Same architecture, same vision encoder, just less of everything.

Reminder, for anyone tuning in halfway through. **A smaller model and a quantised one are two different ways of shrinking.** The smaller model has fewer weights; the quantised model has the same weights stored in fewer bits. Both reduce the freight on the memory bus; only the smaller model also reduces the model's capacity to think.

Two precisions in the bag for the E4B &ndash; only sixteen and four bits, nothing in between on the shelf. The four-bit build is GPTQ, from an individual contributor on HuggingFace. GPTQ and AWQ are the same family &ndash; both round each weight down to one of sixteen values, both use a small calibration set. The differences between them are largely academic, but for the curious: AWQ identifies the most important weights up front and protects them. **GPTQ rounds the model one layer at a time, then quietly adjusts the next layer to make up for whatever the previous layer's rounding got wrong.**

Bar at sixteen bits, text. 99.5 per cent, at 0.21 seconds per invoice. Down to four bits, still 99.0 per cent at the same speed. A model six times smaller than the heavyweight, quantised to a quarter of its disk size, reading invoices almost indistinguishably from the heavyweight at full precision. The announcer suppresses a yawn.

Invoices switch to pictures. Sixteen bits: 60.5 per cent. A thirty-point gap to the heavyweight on the same images. Four bits: 38.5 per cent. A further twenty-two points off the table for one bit removed. The Q4 build did not destroy the vision pipeline the way the AWQ 31B did. It just made it cumulatively, dispiritingly worse.

Two dancers down. The scoreboard:

<table>
<thead>
<tr>
<th style="text-align:left;">Model</th>
<th style="text-align:center;">Bits</th>
<th style="text-align:left;">Method</th>
<th style="text-align:left;">What it does</th>
<th style="text-align:center;">Text</th>
<th style="text-align:center;">Vision</th>
</tr>
</thead>
<tbody>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">16</td><td><a href="https://en.wikipedia.org/wiki/Bfloat16_floating-point_format" target="_blank">BF16</a></td><td>Full precision &ndash; the model as Google shipped it</td><td style="text-align:center;">100%</td><td style="text-align:center;">90.5%</td></tr>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">8</td><td><a href="https://www.exxactcorp.com/blog/hpc/what-is-fp8-fp6-fp4" target="_blank">FP8</a></td><td>Half the bits per weight, pre-rounded by Red Hat</td><td style="text-align:center;">100%</td><td style="text-align:center;">91.5%</td></tr>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">4</td><td><a href="https://huggingface.co/papers/2306.00978" target="_blank">AWQ</a></td><td>Quarter of the bits, with a calibration pass to protect the important weights</td><td style="text-align:center;">100%</td><td style="text-align:center;">0%</td></tr>
<tr><td>Gemma 4 E4B (4.5B)</td><td style="text-align:center;">16</td><td><a href="https://en.wikipedia.org/wiki/Bfloat16_floating-point_format" target="_blank">BF16</a></td><td>Full precision</td><td style="text-align:center;">99.5%</td><td style="text-align:center;">60.5%</td></tr>
<tr><td>Gemma 4 E4B (4.5B)</td><td style="text-align:center;">4</td><td><a href="https://picovoice.ai/blog/what-is-gptq/" target="_blank">GPTQ</a></td><td>Quarter of the bits, rounded layer by layer</td><td style="text-align:center;">99.0%</td><td style="text-align:center;">38.5%</td></tr>
</tbody>
</table>

A pattern is crystallising. **Compression is gentle on easy tasks and ruinous on complex ones.**

## Round Four: Off the Shelves

By now the announcer has a question for the room: **how far can we shrink a model before it loses the ability to read at all?** The off-the-shelf precisions stopped breaking text three rounds ago. To find the floor, we need to keep going.

The smallest dancer takes the floor: the E2B, 2.3 billion parameters, designed for a phone or a low-end laptop GPU. The wheel shop stocked only the full-precision BF16. Nothing quantised. So this round is short.

Sixteen bits, text: 100 per cent, at 0.18 seconds per invoice. Indistinguishable from the heavyweight fourteen times its size. Even the featherweight clears the bar without breaking stride.

Sixteen bits, picture: 12 per cent. Twenty-four invoices out of two hundred. At 2.3-billion-parameter capacity the encoder cannot see properly. **Vision appears to be the first capability to leave when you shrink the model.** Below a certain size you stop getting a multimodal model and start getting a language model with a hallucinating intern bolted to the side.

The bar cannot go any lower in this room. To find where text reading actually breaks, we head back to the garage and weld a smaller wheel ourselves.

## Finding the Floor

Garage doors close. The sanctioned event is over. The rules in here are whatever we can make work.

Before the crushing, the modding. The eyes and ears are dead weight by now &ndash; the vision encoder couldn't read invoices at full precision (12 per cent), the audio tower was never part of the experiment, and both turn out to break the quantisation tool's memory budget. So we open the chassis and rip them out: 1,411 tensors removed, 600 kept. A text-only language model: 2.3 billion parameters, no eyes, no ears.

It took longer than anticipated. Several tools failed &ndash; AutoGPTQ wouldn't compile, GPTQModel crashed on Gemma 4's odd attention shapes, and so forth. HQQ on the stripped E2B was the one that finally worked. Patience, as it turns out, is the AI engineer's first virtue.

We picked <a href="https://github.com/mobiusml/hqq" target="_blank">HQQ</a>: same family as AWQ and GPTQ, but calibration-free. Where the others use a small dataset to learn which weights deserve protection, **HQQ skips that step and picks the rounding from a mathematical formula that looks only at the spread of values inside each weight matrix**. Quicker, but blinder about which weights actually matter.

And... it worked! At three bits per weight, the stripped E2B fits in 5.95 GB of VRAM, generates valid JSON, and reads 91 per cent of invoices correctly. Not a hundred, but functional. The entire language model &ndash; 2.3 billion parameters of compressed weights &ndash; fits in the GPU memory of a six-year-old gaming laptop.

As far as we can tell, no one else has published a Gemma 4 this small that still reads. So, not without pride, <a href="https://huggingface.co/jngb-labs/gemma4-E2B-text-3bit" target="_blank">we uploaded ours to HuggingFace</a>. For anyone who eventually wants Google's flagship multimodal architecture running on a six-year-old gaming laptop.

The crowd is fired up now. Can the dancer go lower? We set the bar at two bits per weight. We send the dancer through. And &ndash; *OH.*

Two bits. 5.68 GB of VRAM. Parse rate, 0 per cent. Random tokens. No JSON, no coherent English, no structure of any kind. Same architecture, same dataset, same prompt, with one bit per weight less &ndash; and the lights went out. Not "somewhat worse." Not "noisy." *Off.* The boundary between functional and dead is exactly one bit wide.

The dancer is on the floor. The bar is being held by no one. We withstood the temptation to upload the 2-bit version to HuggingFace as well, on the grounds that a model returning noise on every input would serve no one. So, with the floor located, on to what it all means.

## The Verdict

The scoreboard, with the dust settled:

<table>
<thead>
<tr>
<th style="text-align:left;">Model</th>
<th style="text-align:center;">Bits</th>
<th style="text-align:left;">Method</th>
<th style="text-align:left;">What it does</th>
<th style="text-align:center;">Text</th>
<th style="text-align:center;">Vision</th>
</tr>
</thead>
<tbody>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">16</td><td><a href="https://en.wikipedia.org/wiki/Bfloat16_floating-point_format" target="_blank">BF16</a></td><td>Full precision</td><td style="text-align:center;">100%</td><td style="text-align:center;">90.5%</td></tr>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">8</td><td><a href="https://www.exxactcorp.com/blog/hpc/what-is-fp8-fp6-fp4" target="_blank">FP8</a></td><td>Half the bits per weight</td><td style="text-align:center;">100%</td><td style="text-align:center;">91.5%</td></tr>
<tr><td>Gemma 4 31B</td><td style="text-align:center;">4</td><td><a href="https://huggingface.co/papers/2306.00978" target="_blank">AWQ</a></td><td>Quarter bits, calibrated</td><td style="text-align:center;">100%</td><td style="text-align:center;">0%</td></tr>
<tr><td>Gemma 4 E4B (4.5B)</td><td style="text-align:center;">16</td><td><a href="https://en.wikipedia.org/wiki/Bfloat16_floating-point_format" target="_blank">BF16</a></td><td>Full precision</td><td style="text-align:center;">99.5%</td><td style="text-align:center;">60.5%</td></tr>
<tr><td>Gemma 4 E4B (4.5B)</td><td style="text-align:center;">4</td><td><a href="https://picovoice.ai/blog/what-is-gptq/" target="_blank">GPTQ</a></td><td>Quarter bits, layer-wise</td><td style="text-align:center;">99.0%</td><td style="text-align:center;">38.5%</td></tr>
<tr><td>Gemma 4 E2B (2.3B)</td><td style="text-align:center;">16</td><td><a href="https://en.wikipedia.org/wiki/Bfloat16_floating-point_format" target="_blank">BF16</a></td><td>Full precision</td><td style="text-align:center;">100%</td><td style="text-align:center;">12%</td></tr>
<tr><td>Gemma 4 E2B (2.3B)</td><td style="text-align:center;">3</td><td><a href="https://github.com/mobiusml/hqq" target="_blank">HQQ</a></td><td>Three bits, calibration-free, eyes and ears removed</td><td style="text-align:center;">91%</td><td style="text-align:center;">&ndash;</td></tr>
<tr><td>Gemma 4 E2B (2.3B)</td><td style="text-align:center;">2</td><td><a href="https://github.com/mobiusml/hqq" target="_blank">HQQ</a></td><td>Two bits &ndash; dead</td><td style="text-align:center;">0%</td><td style="text-align:center;">&ndash;</td></tr>
</tbody>
</table>

<small>Same 200 invoices, same H100, same prompt.</small>

Read it bottom to top: two bits is the cliff, three bits the practical floor for text. Above four bits, text reading is bulletproof across every model size; vision is a different story, holding for some builds and collapsing for others.

So what does quantisation change? Not the answers on a task this simple &ndash; reading a total off an invoice barely moved across precisions. Output *quality* on harder tasks: not tested here. What it changes is the economics of the underlying hardware &ndash; in two directions at once: the same model now fits on smaller, cheaper kit, or packs many more parallel jobs onto the same high-end chip.

<table>
<thead>
<tr>
<th style="text-align:left;">Model</th>
<th style="text-align:left; min-width:120px;">Precision</th>
<th style="text-align:center;">Model Weights</th>
<th style="text-align:center;">Free Memory</th>
<th style="text-align:center;">Parallel Sessions</th>
</tr>
</thead>
<tbody>
<tr><td>Gemma 4 31B</td><td>BF16</td><td style="text-align:center;">58.9 GiB</td><td style="text-align:center;">8.2 GiB</td><td style="text-align:center;">1.2&times;</td></tr>
<tr><td>Gemma 4 31B</td><td>Q8 (FP8)</td><td style="text-align:center;">31.5 GiB</td><td style="text-align:center;">35.7 GiB</td><td style="text-align:center;">5.2&times;</td></tr>
<tr><td>Gemma 4 31B</td><td>Q4 (AWQ)</td><td style="text-align:center;">20.3 GiB</td><td style="text-align:center;">46.8 GiB</td><td style="text-align:center;">6.8&times;</td></tr>
<tr><td>Gemma 4 E4B (4.5B)</td><td>Q4 (GPTQ)</td><td style="text-align:center;">9.8 GiB</td><td style="text-align:center;">57.4 GiB</td><td style="text-align:center;">130.9&times;</td></tr>
</tbody>
</table>

At full precision the 31B fills 58.9 of the H100's 80 gigabytes &ndash; barely room for one session. Compressed to four bits, the same model fills 20.3, leaving 46.8 for everything else. The H100 itself has not become faster. It has become a vastly larger room. Same chip, same model, same answers on this task &ndash; roughly seven times more capacity to run things in parallel. The compressed E4B pushes that into the high two-digits and beyond.

Or, read the other way: the same compressed model now also fits comfortably on far cheaper hardware that could not have run it at full precision in the first place.

Three acts, three models, one experiment. The shape of it, in three observations.

## What This Suggests

**On reading-style tasks, a heavily compressed model is probably fine.** Across every size and every precision down to three bits, every model in the experiment still read the invoice. The output side &ndash; whether the model still writes as well, reasons as well, hallucinates no more often &ndash; is harder to measure objectively, and we did not test that here.

**Hard tasks degrade fastest under compression.** Reading a number off a page is easy. Reading it off a picture is harder. Reading a picture and checking the maths is harder still. Compression takes that hierarchy at its word: easy tasks last, hard tasks first.

**A multimodal model is, primarily, still a text model.** No Gemma 4 read images as well as it read text. Hardly a surprise: a language model is built for text; the vision encoder is the part bolted on later. If a task can be reduced to text, reduce it to text.

## So What

The takeaway for anyone running models in production is simple. **The task determines the kit, not the other way round.**

An easy job &ndash; reading a number out of text, classifying, extracting a field &ndash; runs on a 2.3-billion-parameter model crushed to three bits, the kind that fits on a phone. A medium job &ndash; the same number, off a picture &ndash; needs a bigger model at full precision. A hard job &ndash; reasoning across documents, catching subtle errors &ndash; needs the biggest model on the rack and a human in the loop.

Quantisation does not change that hierarchy. **It can save hardware in two directions:** the same model now runs on cheaper kit, or the high-end chip has room to spare for many more parallel jobs. The point is not to shrink the big model. It is to send each task to the smallest model that still does it.

The bar has dropped about as low as it can. The dancer is still standing at three bits per weight &ndash; two is too low, and there is nothing in between. So the question of *How low can you go?* turns out to be exactly three bits. The Hoff smiles affirmatively and limbos off into the sunset.

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
  var toc = document.getElementById('scroll-toc');
  if (!toc) return;
  var headings = Array.from(document.querySelectorAll('article h2, .note-content h2, .prose h2'));
  if (headings.length === 0) return;

  headings.forEach(function(h) {
    if (!h.id) h.id = h.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    var a = document.createElement('a');
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
