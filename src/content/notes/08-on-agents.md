---
title: "On Agents: Sufficiently Powerful, Necessarily Economical, Occasionally Correct"
summary: "Nvidia says small language models are the future of agentic AI. It is a position paper: arguments, references, no experiment.<br><br>So we ran one. A frontier model and an 8-billion-parameter laptop model drove the same agent loop against the Austrian company registry &ndash; and <strong>the small model failed the simplest mission imaginable, five times, no two failures alike</strong>, before acing a harder one.<br><br>Nothing failed at thinking. Everything failed in the plumbing."
date: "June 2026"
published: 2026-06-12
tags: ["agents", "mcp", "small-language-models", "nvidia", "firmenbuch"]
stack: ["Fable-5", "Qwen3:8B", "MCP", "Ollama"]
---

<h2>Quick Brief</h2>
<ul>
<li><strong>Experiment:</strong> Nvidia claims small language models are the future of agentic AI &ndash; in a position paper, without an experiment. So we ran one: a cloud LLM and a local SLM drove the same agent loop against the Austrian company registry, on missions for which a script had already computed the answers.</li>
<li><strong>Why it matters:</strong> Everyone building agents has to pick a model size. Nvidia's pitch says small is enough &ndash; but nobody says where too small begins.</li>
<li><strong>Key finding:</strong> The big model did everything right, every time, at $0.35 a run or less. The small model understood every task &ndash; and still botched the simplest one: writing out a fifty-entry list. Given a five-entry answer, it was flawless. Small models fail not at understanding but at mechanics &ndash; they can do the work, but only with more architecture and a more precise workflow wrapped around them.</li>
</ul>

<h2>Context</h2>

<p>The model wars are over. Long live the agent wars.</p>

<p>Not long ago, your choice of model was practically a confession of faith. Then the models caught up with one another and became &ndash; clich&eacute; alert &ndash; <a href="/notes/07-llm-limbo" target="_blank">a commodity</a>. The fog of war on the model front has lifted, and what it reveals is&hellip; that the front has merely shifted. To the agentic front.</p>

<p>The route there ran through the early AI workplace &ndash; in retrospect, the scene of a remarkable allocation of talent. Expensively educated professionals spent their days copying information into ChatGPT and pasting the output somewhere else &ndash; where another expensively educated professional would promptly copy it into ChatGPT again.</p>

<p>At some point, someone noticed that the humans in this workflow were contributing little beyond Ctrl-C and Ctrl-V. If one model's output can simply be passed to another model, why keep the middlemen? Silicon Valley, which has never met a middleman it didn't want to cut out, responded with characteristic enthusiasm. That enthusiasm is now a venture-backed product category: agents.</p>

<p>Businesses are sold, Argentina is sold even harder: its Senate is reviewing a new corporate category in Argentine law, <a href="https://www.ft.com/content/f93022fe-43f7-437d-abd8-06c457c0a43c" target="_blank">the non-human corporation</a> &ndash; entities operated by AI agents or robots, limited liability included. Human shareholders may participate, but are not required.</p>

<p>Unsurprisingly, the AI industry's arms supplier has views on all of this too. Surprisingly, not the ones you would expect. <strong><em>Small Language Models are the Future of Agentic AI</em></strong>, <a href="https://arxiv.org/abs/2506.02153" target="_blank">declared Nvidia's research arm in June 2025</a>. SLMs, the paper argues, are "sufficiently powerful, inherently more suitable, and necessarily more economical" for most of what agents do. Not bigger models, smaller ones. From the people selling the chips.</p>

<img src="/images/articles/08-on-agents/nvidia-paper-header.png" alt="Header of Nvidia's arXiv paper: Small Language Models are the Future of Agentic AI" style="max-width:620px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>Your dealer thinks you should cut back.</em></p>

<p>Since their paper explicitly calls for contributions and critique, we decided to do our part. One last job for the middlemen, then.</p>

<h2>Theatre of Operations</h2>

<p>An agent is the continuation of a language model by other means. Those other means being: a loop.</p>

<p>In fairness to the hype, <strong>the model receives not only a prompt but also a menu of tools</strong> it may call as it sees fit. Based on the task, it decides which calls to make &ndash; and whatever a tool returns is fed straight back into the model as fresh input. This repeats, call after call, until the model considers the job from the original prompt done, and stops.</p>

<p>Inside the loop, however, still sits a language model &ndash; large or small &ndash; and it does what language models do: it answers. To test those answers properly, you need questions whose answers are objectively right or wrong, gradable by a script rather than by impression. "Summarise this nicely" cannot be scored. What is needed is something verifiable &ndash; right or wrong, nothing in between.</p>

<p>Our go-to dataset, <a href="/notes/03-regulation-radar" target="_blank">EU regulations</a>, would not do this time: laws can be classified, but hardly graded to the cent. We needed numbers &ndash; balance sheets, ratios, birth years &ndash; wrapped in just enough words for natural-language questions to bite. Enter the Austrian company registry.</p>

<p>Austria keeps a meticulous inventory of its companies, the <a href="https://justizonline.gv.at/jop/web/firmenbuchabfrage" target="_blank">Firmenbuch</a>, and every Kapitalgesellschaft &ndash; every company whose owners enjoy limited liability &ndash; must file its annual accounts there, by law. Better still: Brussels has declared company registers <a href="https://eur-lex.europa.eu/eli/reg_impl/2023/138/oj" target="_blank">"high-value datasets"</a> and ordered them opened up. The registry now answers machine queries free of charge.</p>

<p>For our experiment, we do not need the whole register. We kept the active GmbHs with at least three consecutive years of accounts, the latest filed in 2025: in total 33,282 companies, converted from the ministry's XML into JSON and loaded into a cloud database, with <strong>an MCP server bolted on top</strong> so that a language model can access it. Each company is one document: the balance sheet, the income statement where the law requires one, the ratios we compute from both, and the people who sign &ndash; role and birth year.</p>

<p><strong>Should you wish to interrogate the Austrian economy yourself:</strong> <a href="https://targetradar-web.gentledesert-2dec9d58.germanywestcentral.azurecontainerapps.io/agent" target="_blank">be our guest</a>. Agents get the MCP endpoint, humans get buttons. Free of charge, for as long as our Claude token budget holds.</p>

<img src="/images/articles/08-on-agents/firmenbuch-goes-agentic.png" alt="Screenshot of the Firmenbuch goes Agentic web interface" style="max-width:620px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>Designed for humans, inspired by agents.</em></p>

<p>The theatre is set. Time to inspect the arsenal.</p>

<h2>The Arsenal</h2>

<p>A good soldier is not judged on enthusiasm but on whether the hill got taken. The same goes for financial analysts, with the hills traded in for spreadsheets: what counts is not the confidence of the delivery, but whether the numbers are right. The agents in this experiment will be judged like analysts.</p>

<p>So the test is an analyst's working day, compressed: questions of escalating difficulty &ndash; look up one number, then filter and rank. Each one comes with an answer key, computed in advance.</p>

<p>The answer key comes from a plain Python script. No loop, no tools, no opinions &ndash; it skips the MCP entirely (MCPs are for clankers) and asks the database directly, in the database's own language. It costs nothing, answers in under a second, and has no concept of ambiguity. Its one weakness: somebody has to write a new one for every question. That somebody, of course, is <a href="https://www.linkedin.com/in/jakob-neugebauer/" target="_blank">the middleman</a>.</p>

<p>First assignment, deliberately the simplest we could write: <strong>name the 50 oldest Gesch&auml;ftsf&uuml;hrer in the database.</strong> No filters, no ratios, one sort &ndash; the registry records each signer's birth year, the script orders by it and takes the top 50. Done, in 0.69 seconds.</p>

<p>A few data points from <a href="/article-08-runs.json" target="_blank">the list</a>. The ages run from 88 to 100, median 90.5; at the top, born 1926 and still the registered signatory, FN 065005x. (Companies appear here by Firmenbuch number only. Whether the DSGVO requires this, we do not know &ndash; we obey in advance.) One wrinkle for the grading: a crowd of 88-year-olds ties at the bottom of the list, so the grader does not demand one exact set of FN numbers &ndash; it checks that all 39 aged 89-plus are present, that every remaining seat holds a genuine 88-year-old, and that the count is 50.</p>

<p>Now the other side. An agent needs three things. A <a href="/article-08-system-prompt.txt" target="_blank">system prompt</a>, fixing its behaviour: answer only from the data, companies by number only, admit what you could not verify. A <a href="/article-08-missions.txt" target="_blank">user prompt</a>: the question. And the ability to call tools &ndash; which, in our case, means one thing: <a href="https://www.youtube.com/watch?v=HyzlYwjoXOQ" target="_blank">an MCP server</a>.</p>

<p>In short: <strong>an MCP server is an interpreter between two parties that cannot talk to each other.</strong> Models speak only text; databases speak only queries. MCP turns the model's worded request into a real query, and the rows back into text the model can read. That is the whole job &ndash; and the whole point: build the interpreter once, and anything that writes text can use the database. Flagship or featherweight. We are about to send both.</p>
<img src="/images/articles/08-on-agents/architecture.svg" alt="The agent loop: model, MCP server as interpreter, registry behind" style="max-width:680px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>The whole trick, drawn, slightly simplified. The model thinks, the MCP translates, the loop repeats &ndash; and the bill grows at every arrow.</em></p>

<p>So much for the theory. Time to put it into practice.</p>

<h2>First Engagement</h2>

<p>The flagship goes first: <a href="https://www.anthropic.com/news/claude-fable-5-mythos-5" target="_blank">Claude Fable 5</a> &ndash; the dumbed-down but publicly available edition of the model deemed too dangerous to be released.</p>

<p>It did not fumble once. One tool call per run &ndash; search by GF age, descending, limit 50: exactly the query an analyst would have written &ndash; then the answer. We asked three times; all 39 of the 89-plus club present every time, every remaining seat a genuine 88-year-old, and the three lists identical, company for company. It even attached footnotes nobody asked for, flagging the silently excluded companies without a recorded age and the tie at the bottom of the list. <strong>The simplest task of all, passed with flying colours</strong> &ndash; in 19 seconds and at $0.35 per run.</p>

<p style="margin-top:1.5rem;">That, however, was never Nvidia's claim. Their claim concerns the featherweights. So the same mission went to <a href="https://ollama.com/library/qwen3" target="_blank">Qwen3:8B</a>, an 8-billion-parameter open-weight model, running locally on the MacBook Air &ndash; the consumer-device deployment Nvidia's paper has in mind.</p>

<p>The first local run took nine minutes, against the flagship's nineteen seconds. Expected. Then the answer came back, and we checked how many of the fifty companies had made it in.</p>

<p>None. Zero out of fifty.</p>

<p>The tool call was identical. The data was identical. The culprit was a default. <a href="https://ollama.com" target="_blank">Ollama</a>, the program serving local models, rations a model's working memory, and the 13,000-token delivery flushed the rules and the question clean out of it. The model, left holding data with no brief, confidently delivered something anyway.</p>

<p>First lesson of the campaign: out-of-the-box gear is not field-ready. One setting later the problem was gone &ndash; though fifty slim rows had just filled a third of this model's head, and real databases serve heavier meals. Nvidia's prospectus is silent on portion control. We have an idea or two on the matter &ndash; they can wait for the verdict.</p>

<p>First, the rematch. This time the data fit. The database had done all the sorting, the MCP had handed over the final, correct list &ndash; the model's entire job was reading it back, line by line. Which went fine for ten lines. Then the needle stuck:</p>

<pre><code>..."137249m","281973t","216248m","238144m",
"137249m","281973t","216248m","238144m",
"137249m","281973t","216248m","238144m", ...</code></pre>

<p>Row eleven, forever.</p>

<p>A language model, you see, never copies &ndash; it re-writes, predicting every next word from what it sees. The flagship has capacity to spare for bookkeeping: row fourteen, row fifteen, row sixteen. The featherweight has no such luxury; halfway down a list of look-alike codes it loses its place and grabs the nearest pattern, which is the line it just wrote. Not a thinking problem &ndash; there was barely anything to think. A writing problem.</p>

<p>Before anyone nominates us for a Turing Award: the stutter has been in the books since 2019, as <a href="https://arxiv.org/abs/1904.09751" target="_blank">neural text degeneration</a>. The obvious workaround &ndash; <strong>let the server write the list into a file and have the model merely hand over the link</strong> &ndash; is a change to the tools, not to the model.</p>

<p>The first mission's books: the flagship answered three times &ndash; correctly and identically each time, in 19 seconds, at $0.35 a run. The featherweight answered five times in all &ndash; once on factory settings, four times with the memory fixed &ndash; never correctly, never the same way twice; every run after the fix started right and derailed at a different line. Free of charge, mind, at up to 27 minutes a run. Necessarily more economical, as promised. Sufficiently powerful is another matter.</p>

<p>Lesson learned, workaround filed &ndash; and one question left open: what does the featherweight do when the writing is within its powers? Mission two was designed to find out.</p>

<h2>Second Engagement</h2>

<p>The laundromat has acquired almost mythical status on finance social media, displacing the Goldman internship as the be-all and end-all of financial ambition. The appeal rests on recurring cash, minimal inventory, little labour, and customers who not only do the work themselves but pay for the privilege.</p>

<p>Regrettably, the Austrian company registry has no category for laundromats. So we went for the next best thing: a machinery builder in the industrial heartland, run by a Gesch&auml;ftsf&uuml;hrer of advanced years. Mission two, then: <em>"Which machinery companies in Ober&ouml;sterreich have a Gesch&auml;ftsf&uuml;hrer aged 70 or older?"</em></p>
<img src="/images/articles/08-on-agents/laundromat-meme.jpg" alt="Is this a pigeon meme: finance bro mistakes a database query for a laundromat" style="max-width:480px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>Fuzzy matching.</em></p>

<p>For the experiment, the question is convenient twice over: three filters to compose instead of one sort &ndash; and an answer short enough that the featherweight's pen should survive it.</p>

<p>The flagship went first. It asked, the MCP answered, and there was the list: five companies, the same five sitting on our answer key &ndash; three runs, three identical answers, thirteen seconds and $0.17 apiece. No surprises expected; none granted. The five directors carry 373 years between them, and one of their companies turns &euro;34m of revenue into an EBIT margin of 0.96 per cent. The laundromat dream, Austrian edition.</p>

<p>Then the chosen one &ndash; the weight class Nvidia's paper nominates for exactly this work. It took its time, four minutes of thinking out loud per run, at the usual price of nothing &ndash; but this time it finished: five codes is a list an 8B can write down. Its five matched the answer key exactly, and matched them again on the second run, and on the third. Given a question its pen survives, the featherweight is reliable.</p>

<p>So, for once, both analysts agreed. The difference sat in the small print underneath. The flagship attached, unprompted, the two ways the answer could still be quietly wrong &ndash; among them the 11,841 companies sitting in "unknown", invisible to any sector search. The featherweight attached nothing of the kind. <strong>One analyst does what you asked; the other tells you what you should have asked.</strong> The $0.17 buys the second.</p>

<p>Two missions completed, out of the infinitely many we could have flown. Time for the after-action review.</p>

<h2>What This Suggests</h2>

<p><strong>"Sufficiently powerful" survives &ndash; provided the answer is short.</strong> Across all 14 runs &ndash; the flagship's three and the featherweight's five on the list, then three each on the machinery question &ndash; both models chose the right tool with the right parameters at the first attempt, every time. The featherweight botched the fifty-entry list every time it tried &ndash; and delivered the five-entry answer perfectly, three times out of three. Small models do not fail at thinking. They fail at writing it down.</p>

<p><strong>"Inherently more suitable" holds only if the tools suit the model.</strong> The featherweight's memory failure was pure configuration: the runtime's default working memory was simply too small for the data, and nothing announced it. The stutter has known countermeasures too &ndash; a repetition guard we left untested, and the simpler cure of not making a model photocopy at all: keep results short, and for long lists have the server save a file and let the model return just the link. Small models need tools that carry the heavy text for them.</p>

<p><strong>"Necessarily more economical" depends on how busy the agent is.</strong> Per token, the small model wins by arithmetic &ndash; ours ran on electricity. But the savings carry a fixed cost: someone sizes the memory, catches the silent failures, stays on call. That pays off for an agent answering a hundred simple questions an hour. For one answering a hard question a day, $0.35 is a bargain. Either way the rule holds: every agent is an employee &ndash; you pay in tokens or in supervision.</p>

<p><strong>The triad is missing its fourth line: the expensive model ships an audit trail.</strong> Wherever both models answered, the answers were identical. Only the flagship documented, unprompted and every run, where its answer could mislead &ndash; the missing ages, the 11,841 unclassified companies &ndash; caveats that read like an auditor's working notes. If correctness is becoming a commodity, the audit trail is the premium tier.</p>

<h2>So What?</h2>

<p>The models, it turns out, were the least interesting part. Both of them &ndash; the large one and the small &ndash; translated plain-language questions into correct database queries fourteen times out of fourteen; the intelligence was a given. <strong>What separated success from failure was the workflow around the model</strong> &ndash; how much data flows in, how long the answer must be, which default somebody forgot to change.</p>

<p>Which is why, having set out to test it, we end up with nothing that challenges the general path Nvidia's paper outlines. Small models may well be the future of agentic AI &ndash; <strong>provided their tools stay simple, their portions stay small, and the architecture around them does the heavy lifting</strong>. Those are engineering details, not objections. The future, as so often, ships with some assembly required.</p>

<p>One caveat the paper would appreciate: everything we tested had a provably right answer. That is precisely the work agents will take over first &ndash; the lookups, the filters, the lists. Whether they can do the work that has no answer key, this correspondence cannot say. The closest we came was the small print: those unprompted caveats had no answer key either &ndash; and they were the one place the two models parted company.</p>

<p>As for everyone whose working day is lookups, filters and lists: time to finally buy that laundromat.</p>

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
