---
title: "Who Even Needs Nvidia? Classifying EU Laws Without a GPU"
summary: "The AI industry has spent considerable effort establishing that text classification is a job for large language models. The models are impressive, the hardware is expensive, and the results – it turns out – are not.<br><br>We tested TF-IDF – a method old enough to vote, with no neural network and no understanding of language whatsoever – against four LLMs on 890 EU regulations. <strong>It outperformed the best of them by 24 percentage points.</strong><br><br>The method that counts words beat the method that supposedly understands them. Which raises an uncomfortable question about what we have all been paying for."
date: "April 2026"
published: 2026-03-27
tags: ["eu-regulation", "classical-ml", "text-classification", "tf-idf", "benchmark"]
stack: ["TF-IDF", "LogisticRegression", "FastText"]
---

## Quick Brief

- **Experiment:** TF-IDF + Logistic Regression and a FastText classifier were trained on 64,000 historical EU regulations and tested on the same 890 documents that four LLMs classified in the <a href="/notes/03-regulation-radar" target="_blank">previous experiment</a>. Same test set, same ground truth, same 21 EuroVoc domains.
- **Why it matters:** The AI industry's default assumption is that text classification requires large language models, which require GPUs, which require Nvidia. This experiment tests whether that assumption survives contact with actual data.
- **Key finding:** The simplest method won. TF-IDF with a linear classifier – five minutes of training on a MacBook, no GPU – outperformed the best-performing LLM by 24 percentage points. More text, more features, and more parameters all made things worse.

## Context

Famously, every problem looks like a nail if you have a hammer. And the hammer of the moment is the large language model – an extremely large hammer. The hammer itself is often free: open-source models like DeepSeek and Llama can be <a href="https://huggingface.co/" target="_blank">downloaded by anyone</a>. What costs money is the workbench you need to swing it. A single Nvidia H100 GPU costs about as much as a mid-range car, and the <a href="/notes/03-regulation-radar" target="_blank">previous experiment</a> needed eight of them.

Four of those hammers, pointed at 890 EU regulations, produced underwhelming results. The best model – <a href="https://huggingface.co/deepseek-ai/DeepSeek-R1" target="_blank">DeepSeek-R1</a> with 70 billion parameters – agreed with the human librarians roughly half the time. The others did worse. At €23 per hour in GPU rental, the cost-per-correct-answer was starting to look like a bad trade.

Which raised a question that, in the current climate, borders on heresy: **what if we do not need the hammer at all?**

Not a smaller hammer. No hammer. No neural network, no embeddings, no attention heads, no GPU. The kind of statistical text classification that existed before anyone had even heard of a transformer – the kind that runs on a laptop, trains in minutes, and costs (virtually) nothing.

Picture a filing clerk. Not a clever one. A system that has spent thirty years in the same basement archive, sorting documents into the same 21 filing drawers. It does not understand the documents. It has never read one cover to cover in its life. But it has seen 64,000 of them pass across its desk, and it has noticed a few things. Documents containing the word "fisheries" go into the Agriculture drawer. Documents containing "tariff quota" go into Trade. It does not know what a tariff quota *is*. It just knows where it goes.

This is, in essence, what we are about to test. Whether a filing clerk with a word-frequency spreadsheet and no understanding of language whatsoever can outperform an oracle with a data centre.

## WTF is TF-IDF?

In basic economics, the price of a good is determined by its relative scarcity. The rarer it is, the more valuable it becomes. **TF-IDF applies this principle to words.**

Every EU regulation contains "regulation", "shall", and "European Union". Those words tell you nothing – they appear in everything. But a regulation that contains "fisheries", "tariff quota", and "third-country imports" is almost certainly about trade and agriculture.

TF-IDF formalises that intuition: multiply how often a word appears in a document (the **T**erm **F**requency) by how rare it is across the entire corpus (the **I**nverse **D**ocument **F**requency). Common words score near zero. Distinctive words score high.

<div style="max-width:480px;margin:1.8rem auto;padding:1.5rem 2rem;background:#faf8f5;border:1px solid #e8e0d8;border-radius:6px;font-family:'Georgia','Times New Roman',serif;">
<div style="text-align:center;margin-bottom:1.2rem;">
<span style="font-size:1.1rem;letter-spacing:0.02em;">TF-IDF(t, d) = TF(t, d)</span>
<span style="font-size:1.1rem;padding:0 0.3rem;">×</span>
<span style="font-size:1.1rem;">log</span>
<span style="font-size:1.1rem;margin-left:2px;"><sup style="font-size:0.85rem;">N</sup>&frasl;<sub style="font-size:0.85rem;">df(t)</sub></span>
</div>
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:0.78rem;color:#888;line-height:1.6;">
<em>t</em> = a word. <em>d</em> = a document. <em>N</em> = total documents in the corpus (64,000).<br>
<em>df(t)</em> = how many documents contain that word.<br>
The rarer the word, the higher the score.
</div>
<div style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid #e8e0d8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:0.78rem;color:#666;line-height:1.7;">
<strong>"regulation"</strong> — appears in nearly every document. IDF ≈ 0.05. Worthless.<br>
<strong>"fisheries"</strong> — appears in ~3,000 of 64,000. IDF ≈ 3.1. Getting somewhere.<br>
<strong>"swordfish"</strong> — appears in 47 documents. IDF ≈ 7.2. Forty-seven EU regulations mention swordfish, in case you were wondering.
</div>
</div>

The maths fits on a napkin and **the entire model fits on a laptop**. Feed the TF-IDF scores into a logistic regression – 21 classifiers, one per domain, each drawing a line between "this is Agriculture" and "this is not Agriculture" – and you have a multi-label text classifier that trains in five minutes.

No understanding, no reasoning, no attention heads – just counting.

But counting requires something to count against. The filing clerk's trick is not intelligence – it is memory. And the EU, to its credit, provides an almost unreasonably good one.

For those just tuning in: all EU legislation is publicly available through <a href="https://eur-lex.europa.eu/" target="_blank">EUR-Lex</a>, with a <a href="https://publications.europa.eu/webapi/rdf/sparql" target="_blank">SPARQL endpoint</a> for querying legislation like a database and a bulk-download API called <a href="https://op.europa.eu/en/web/cellar" target="_blank">CELLAR</a> that delivers full texts programmatically in all 24 official EU languages. A very well-organised government filing cabinet that understands HTTP. The <a href="/notes/03-regulation-radar" target="_blank">previous experiment</a> covered the infrastructure in detail.

81,450 historical regulations sit in that database (as of March 17, 2026). CELLAR returned full texts for 65,906 of them. The remaining 15,544 date mostly from the 1990s, an era when "digitised" meant the regulation existed on a floppy disk somewhere in Luxembourg.

The setup was simple. **64,000 of those historical regulations become the training data** – each one already tagged by professional librarians at the EU's Publications Office, who have been classifying legislation into 21 thematic domains since 1995. **The 890 recent regulations from the previous experiment become the test set** – the same documents the LLMs already attempted, graded against the same human baseline.

The LLMs showed up to the exam cold. They saw the regulation, saw the list of 21 domains, and winged it. Zero-shot. No training data, no examples, no prior exposure to the EU's taxonomy.

The filing clerk studied 64,000 past exams first. Same test, very different preparation.

## The Undercard

But TF-IDF has a blind spot: it treats every word as independent. "Fishery", "fisheries", and "fishing" are three unrelated inputs. A human immediately sees they belong together. TF-IDF does not.

<a href="https://fasttext.cc/" target="_blank">FastText</a>, developed at Meta (the company formerly known as Facebook) in 2016, was supposed to fix this. It breaks words into character fragments – "fishery" becomes `<fis`, `fish`, `ishe`, `sher`, `hery`, `ery>` – and learns weights for each fragment. Words that share fragments get treated similarly. It is, in effect, a filing clerk that understands "agricultural policy" and "agriculture regulation" belong in the same drawer.

Whether that extra cleverness helps on documents drafted by the most linguistically predictable institution on the European continent is a separate question.

## Scoreboard, Such As It Is

Both methods ran all three input variants on a 16 GB MacBook Air. Three variants, because the previous experiment fed the LLMs the Preamble plus opening Articles, and we wanted to test whether more text helps:

**Preamble only** (~350 words): the concentrated signal. The "Whereas" recitals – why does this regulation exist?

**Preamble + Articles** (~830 words, truncated at 16,000 characters): what the LLMs received in the previous experiment. Preamble plus the actual legal rules.

**Full Text** (~3,100 words): everything, including technical annexes, tariff tables, and product codes.

TF-IDF finished all three variants in 30 minutes. FastText, despite its name, took five and a half hours. Then we put both sets of results next to the LLMs from the <a href="/notes/03-regulation-radar" target="_blank">previous experiment</a> – same 890 regulations, same human ground truth – and looked at the scoreboard.

<table style="font-size:0.88rem;">
<thead><tr><th style="text-align:left;min-width:160px;">Method</th><th style="text-align:center;">Input</th><th style="text-align:center;">Hardware</th><th style="text-align:center;">F1</th><th style="text-align:center;">Time</th></tr></thead>
<tbody>
<tr style="background:rgba(40,140,40,0.1);"><td><strong>TF-IDF</strong></td><td style="text-align:center;">Preamble</td><td style="text-align:center;">MacBook Air</td><td style="text-align:center;"><strong>0.799</strong></td><td style="text-align:center;"><strong>5 min</strong></td></tr>
<tr><td>TF-IDF</td><td style="text-align:center;">Preamble + Articles</td><td style="text-align:center;">MacBook Air</td><td style="text-align:center;">0.792</td><td style="text-align:center;">8.5 min</td></tr>
<tr><td>FastText</td><td style="text-align:center;">Preamble</td><td style="text-align:center;">MacBook Air</td><td style="text-align:center;">0.787</td><td style="text-align:center;">55 min</td></tr>
<tr><td>FastText</td><td style="text-align:center;">Preamble + Articles</td><td style="text-align:center;">MacBook Air</td><td style="text-align:center;">0.786</td><td style="text-align:center;">92 min</td></tr>
<tr><td>TF-IDF</td><td style="text-align:center;">Full Text</td><td style="text-align:center;">MacBook Air</td><td style="text-align:center;">0.774</td><td style="text-align:center;">15 min</td></tr>
<tr><td>FastText</td><td style="text-align:center;">Full Text</td><td style="text-align:center;">MacBook Air</td><td style="text-align:center;">0.771</td><td style="text-align:center;">~4 hours</td></tr>
<tr style="border-top:2px solid #ddd;"><td>DeepSeek-R1-70B</td><td style="text-align:center;">Preamble + Articles</td><td style="text-align:center;">8× H100</td><td style="text-align:center;">0.562</td><td style="text-align:center;">~31 min</td></tr>
<tr><td>SaulLM-141B</td><td style="text-align:center;">Preamble + Articles</td><td style="text-align:center;">8× H100</td><td style="text-align:center;">0.501</td><td style="text-align:center;">~34 min</td></tr>
<tr><td>EuroLLM-22B</td><td style="text-align:center;">Preamble + Articles</td><td style="text-align:center;">8× H100</td><td style="text-align:center;">0.473</td><td style="text-align:center;">~31 min</td></tr>
<tr><td>SaulLM-7B</td><td style="text-align:center;">Preamble + Articles</td><td style="text-align:center;">MacBook Air</td><td style="text-align:center;">0.327</td><td style="text-align:center;">~16 h</td></tr>
</tbody>
</table>

*Same 890 regulations. Same human baseline. The LLMs ran zero-shot. The classical methods studied 64,000 past exams first.*

Read it top to bottom. **Every classical method – every single one, including the worst-performing variant on the worst input – outperformed the best LLM.** The gap between the cheapest statistical method and the most expensive language model is not a rounding error. It is 24 percentage points.

The filing clerk scored 0.80. The best oracle scored 0.56. Counting words beat understanding them. Strip it down: 26,000 learned weights versus 70 billion parameters – a ratio of 2.7 million to one – at a cost of €0 versus €23 per hour. The filing clerk won.

## Obviously

The result is less counterintuitive than it first appears, once you stop and think about what actually happened.

The LLMs worked zero-shot. They saw a regulation and a list of 21 domains, and were asked to classify on the spot. No training data, no examples, no prior exposure to the EU's taxonomy. This is like handing someone an exam in a subject they have never studied and being surprised when they score 56%.

TF-IDF, by contrast, had seen 64,000 examples of exactly this mapping. It learned that "fisheries" correlates with AGRICULTURE. Not because it has any concept of what a fish is, but because it has counted 19,555 documents tagged AGRICULTURE and noticed that quite a few of them included the word "fish". It does not comprehend language – it counts words. But on a classification task with a stable taxonomy and abundant training data, **counting turns out to be enough.**

The LLMs "understand" language in some deeper sense – they can reason about edge cases, explain their thinking, handle ambiguity. But they had never studied the specific exam they were taking. The filing clerk studied nothing else.

## (Not So) FastText

FastText's trick is breaking words into character fragments to catch spelling variants. This is genuinely useful when your corpus looks like it was written at 2 AM on a phone: "amazinggg", "soooo good", "u wot m8?"

The approach will presumably justify itself the day the Council of the European Union starts drafting legislation along the lines of *"Whereas the fisherieees r like soooo important 2 the EU economy ngl, the Council hereby establishes smth smth tariff quota idk lol."*

That day has not come, and you will search 64,000 EU regulations in vain for a single "lol". What you will find is "Agri-Foodstuffs" – spelled identically, in the same font, by the same committee, in the same building, since 1995. The EU does not do linguistic creativity. It does repetition. And repetition is exactly what TF-IDF was designed for.

FastText brought a solution to a problem that Brussels has never had. And because it learns weights for every character fragment of every word – rather than just counting whole words – it needs considerably more time to do so. It trained eleven times longer than TF-IDF on the Preamble variant and scored lower on every single input variant. More computation, more complexity, worse result.

The pattern extended to the input itself. Across both methods, Preamble-only text consistently outperformed Preamble + Articles, which outperformed Full Text.

Preamble text contains 62,000 unique words. Full Text contains 432,000. Most of that expansion is legal boilerplate, product codes, and technical specifications – noise that dilutes the classification signal. Full Text averaged 3,127 tokens per document versus 343 for Preamble: nine times more text to process, for a worse result.

If you are building a document classification pipeline, **feeding the model the entire document is not just wasteful – it is actively harmful.** The classifier does better with less.

## What This Suggests

**Not every problem is a nail.** A linear model trained on word frequencies – technology from the early 2000s, running on a laptop – outperformed everything with a GPU attached to it, by 24 percentage points.

**Some problems are nails.** If you do not have 64,000 labelled documents (and most organisations do not), the LLM is the only option. And for tasks that require actual understanding – summarising, impact assessment, cross-referencing existing law – the filing clerk cannot even show up. It can tell you where the document goes. It cannot tell you what it means.

**The bottleneck is the data, not the model.** During development, TF-IDF scored 0.58 when trained on just 5,000 documents and 0.80 on the full 64,000. Same model, same code, same laptop. A 13× increase in training data improved the result more than the difference between any two methods. This will not come as a shock to anyone who has ever worked with data.

## So What?

We strapped 70 billion parameters to eight rented GPUs, pointed the result at 890 EU regulations, and the best model agreed with the human librarians about half the time. The GPU cluster cost €23 per hour. Then a filing clerk with a word-frequency spreadsheet – running on a MacBook that was already paid for, no wifi or API key required – beat it by 24 points.

The useful question was never "which tool is best?" It was "which tool is best *for this step?*" A regulation needs to be classified, then summarised, then cross-referenced with existing law. The filing clerk handles the first step. The LLM is indispensable for the other two. A pipeline that uses each tool where it actually works – the clerk for sorting, the oracle for reading – would be faster, cheaper, and more accurate than sending everything to the biggest model available.

So who even needs Nvidia? For the sorting step – the part where you decide which drawer a document belongs in – nobody. For the reading step – the part where you need to understand what it actually says – still everyone. For the time being, Nvidia's quarterly earnings are safe.

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
