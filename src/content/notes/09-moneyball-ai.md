---
title: "Moneyball AI: Running Agents on a Raspberry Pi"
summary: "Nvidia &ndash; which sells the big chips &ndash; says agents mostly need small ones, and last time we came away half-convinced. The open question was how small you can actually go. So we drafted a bench of sub-billion-parameter models, wired them to the Austrian company registry through an MCP server, and set the cheapest loose on a Raspberry Pi.<br><br><strong>A half-billion-parameter model ran the whole pipeline</strong> &ndash; picked the tools, chained them, produced the right file, counts identical to a control script &ndash; and broke at exactly one step: writing the answer down.<br><br>Everything worked but the confirmation message."
date: "July 2026"
published: 2026-07-15
tags: ["agents", "mcp", "small-language-models", "nvidia", "firmenbuch", "raspberry-pi"]
stack: ["Hammer-2.1:0.5B", "Danube-3:500M", "SmolLM-2:360M", "llama.cpp", "MCP"]
---

<h2>Quick Brief</h2>
<ul>
  <li><strong>Experiment:</strong> Three sub-billion-parameter open models drive an agent against the Austrian company registry. The task is built so it cannot be done in a single call &ndash; the model has to chain several, with the data kept in files, out of its head. Each answer is graded against a precomputed key.</li>
  <li><strong>Why it matters:</strong> <a href="https://arxiv.org/abs/2506.02153" target="_blank">Nvidia says agents mostly need small models</a>, not big ones, and <a href="/notes/08-on-agents" target="_blank">it seems they are on to something</a>. What nobody has pinned down is how small a model you can get away with and still drive a useful agent.</li>
  <li><strong>Key finding:</strong> A half-billion-parameter model ran the whole pipeline correctly &ndash; the right companies in the right file, counts identical to a non-LLM control script. The one thing it could not do was report the result in plain words. Everything worked but the confirmation message.</li>
</ul>

<h2>Context</h2>

<p>The modern Klondike is not found in the hills of the Yukon but in vast warehouses whose primary raw material is electricity &ndash; the next frontier, they say, is space. Inside these modern mines, the shovels cost five figures apiece, making the shovel salesman one of the richest men in town.</p>

<p>A shovel salesman getting rich during a gold rush is hardly remarkable. Things start to get interesting when said shovel salesman publishes a white paper arguing that spoons are the future.</p>

<p>No gold rush is complete without its familiar choir of sceptics: the street preacher forecasting ruin, the wife begging her husband not to bet the farm on a hole in the ground. Voices, typically, with little to win and much to lose. Yet it is almost unheard of for the shovel salesman himself to be counted among them.</p>

<p>Stranger still is the silence that met him. Take the advice and the potential savings run to fortunes; ignore it, and you keep overpaying for shovels you can barely get. The claim is hardly wild: break a big job into enough small, repetitive steps, and each one is simple enough for a spoon to handle. Welcome to the world of agentic AI.</p>

<p>We decided to take the shovel salesman at his word. Partly because it sounds sensible, and partly because we could not have afforded a shovel without betting the farm. So we grabbed a spoon and started digging.</p>

<h2>The Curious Case of the Shovel Seller</h2>

<p>The most trustworthy advice is the kind that costs the adviser something. The barber who says you do not need a haircut yet; the mechanic who can find nothing wrong with the car. You listen, because people rarely talk themselves out of a sale without a reason. So when the world's foremost seller of AI hardware publishes a paper <strong>implying its customers are buying far more than they need</strong>, it is worth reading closely.</p>

<p>The seller, obviously, is Nvidia, whose only real competition is the waiting list for more Nvidia. The paper, from its own research lab, carries the unhedged title <a href="https://arxiv.org/abs/2506.02153" target="_blank"><em>Small Language Models are the Future of Agentic AI</em></a>, and its case is that the narrow, repetitive errands filling an agent's day do not need a giant model. A small one &ndash; cheap, unglamorous, able to run on a laptop &ndash; is, in the paper's words, &ldquo;sufficiently powerful, inherently more suitable, and necessarily more economical.&rdquo;</p>

<img src="/images/articles/09-moneyball-ai/nvidia-h100.png" alt="PNY NVIDIA H100 NVL PCIe retail listing priced at $35,349.91 with free shipping, an Add to Cart button, and 18 units in stock" style="max-width:620px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>The <a href="https://www.nvidia.com/en-us/data-center/h100/" target="_blank">industry-standard shovel</a>. The free shipping comes in handy given the fact that they are typically ordered by the thousands.</em></p>

<p>We did not take this on faith. <a href="/notes/08-on-agents" target="_blank">Last time</a> we ran a test: a cheap model on a laptop and an expensive frontier model, handed the same job against <a href="https://targetradar-web.gentledesert-2dec9d58.germanywestcentral.azurecontainerapps.io/agent" target="_blank">a database of Austrian companies</a>. On the question that mattered, both gave the same answer; where the cheap one flunked, we had already spotted the fix. <strong>Nvidia's theory survived its first contact with reality</strong>, and &ndash; frankly &ndash; we came away believers.</p>

<p>Which is the slightly awkward place this experiment begins. A believer does not ask whether small models work; we are satisfied they do. What is left is the harder question: <strong>how small can the model be?</strong> Somewhere beneath last time's model there is a floor &ndash; a model too small to drive an agent at all &ndash; and this time we went looking for it.</p>

<p>The rig is last time's, unchanged: thirty-odd thousand Austrian companies behind the same MCP server, every question marked against an answer worked out in advance. What changes is the model. Last time's was already a small one; this time we go smaller still &ndash; a bench of the tiniest open models we could find, none above a billion parameters.</p>

<p>Each model then faces a task no single query can answer &ndash; more on that later. With the rules laid out, drafting season can begin.</p>

<h2>The Draft</h2>

<p>Everyone is buying big &ndash; the frontier models, the multimodal ones, the do-everything ones. That is where the hype is, and the money with it. We have neither, so we go the other way and shop for the players no one else wants: the ones who do not dazzle, but <a href="https://www.youtube.com/watch?v=Bnvvn0xrV24" target="_blank">get on base</a>.</p>

<p>The bench, then. <a href="https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct" target="_blank">SmolLM2-360M</a>, a plain generalist; <a href="https://huggingface.co/MadeAgents/Hammer2.1-0.5b" target="_blank">Hammer-0.5B</a>, built for one job &ndash; calling tools; and <a href="https://huggingface.co/h2oai/h2o-danube3-500m-chat" target="_blank">H2O-Danube3-500M</a>, another generalist but from another lab. None above a billion parameters. The only thing we need from any of them is that it can make the call.</p>

<p>And since they are not frontier models &ndash; and since we are not made of money &ndash; there is no premium treatment to go with them. No multi-GPU Nvidia setup, no liquid cooling, no <a href="https://www.npr.org/2024/09/20/nx-s1-5120581/three-mile-island-nuclear-power-plant-microsoft-ai" target="_blank">retired nuclear plant dragged back online</a> to feed it &ndash; none of the comforts their larger cousins take for granted; they run on whatever is to hand. Which, it turns out, can include <strong>a Raspberry Pi rented by the hour in the cloud</strong>.</p>

<img src="/images/articles/09-moneyball-ai/mythic-beasts-pi.png" alt="Cloud Raspberry Pi pricing page: Pi 3 and Pi 4 plans from £5.75 a month with per-second billing, and a footer warning the service is aimed at hobbyists and should not run nuclear power station controls" style="max-width:620px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>The agent's new home, from &pound;5.75 a month. Behind every disclaimer, a story.</em></p>

<p>Once the Pi was up and running, it was clear from the start that the usual machinery would not fit. vLLM is built to feed a crowd from a rack of Nvidia cards, and a Pi is neither a crowd nor a rack. Ollama, last time's workhorse, refuses to let a model call a tool unless it ships with the right template, and ours do not. So we fell back on the old guard, <a href="https://github.com/ggml-org/llama.cpp" target="_blank">llama.cpp</a>: lighter, asks for no graphics card, and willing to let a small model at least try.</p>

<p>Models from HuggingFace (where else); the MCP server from last time, with minor adaptations, running alongside to field their queries; and the two prompts every agent gets &ndash; a <a href="/article-09-system-prompt.txt" target="_blank">system prompt</a> with the rules, a <a href="/article-09-user-prompt.txt" target="_blank">user prompt</a> with the question. We began with a test script: <strong>could each model even emit a tool call?</strong></p>

<p>First, the smaller generalist, SmolLM2, put to the test on a fraction of the parameters. Such was our faith in the shovel-maker's prophecy that we half-expected a home run. It was not. An answer came back, but in place of a tool call &ndash; the request that would have queried the registry &ndash; it returned a fistful of company names, invented on the spot. Had we taken the shovel-maker's prediction too literally?</p>

<p>Nervously, we sent the next batter to the plate &ndash; Danube, same size, different lab &ndash; and, as it turned out, a different way to fail. It invented nothing, but it never called the tool either; it read our instructions back and asked which tool we meant. Two up, two struck out, not a single tool called between them. One name left on the card.</p>

<h2>Hammertime</h2>

<p><strong>A language model can do one thing: produce text.</strong> It cannot look anything up or query a database &ndash; ask it for the machinery companies in Tirol and it can only guess. So you give it a <em>tool</em>: a function like <code>search_companies</code> it can ask to have run. It never runs the function; it merely writes a note in a specific format, while a program (the harness) sits outside in a loop, waiting. The moment a note arrives that fits the function's arguments, the program executes it and hands the answer back to the model.</p>

<img src="/images/articles/09-moneyball-ai/smollm2-tirol-loop.png" alt="SmolLM2 terminal output: a looping, invented list of machinery companies in Tirol" style="max-width:620px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>Tirol's machinery firms, according to SmolLM2: French, fictional, and on a loop.</em></p>

<p>A generalist can do this too, but it has to work out that a tool is needed and which one to call. And that takes room. Eight billion parameters have room to spare; under one billion, barely any &ndash; so the model just does whatever it reckons looks right. <strong>Hammer2.1-0.5b is a function-calling model</strong>: fine-tuned on <a href="https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k" target="_blank">sixty thousand function calls</a> until the call is pure reflex. Picture a veteran hearing fireworks and instinctively heading for the bushes, scanning for Charlie.</p>

<p>We watched, nervously, as the script wound up and threw the prompts at the model. Hammer swung &ndash; and put it clean out of the ballpark. All that brainwashing, drilled in for this exact moment, paid off: back came the precise call we needed, <code>search_companies(sector: machinery, bundesland: T)</code>, three times out of three. It was the very call the expensive model would have made.</p>

<p>The gate was cleared. Now the real experiment could begin.</p>

<p>As already mentioned, the real test is a question no single query can answer: the top three Bundesl&auml;nder with the most companies carrying over &euro;12 million in total assets, and how many each has &ndash; a plain hunt for the bigger fish. The MCP's search returns fifty rows at a time and will not add them up, so no single call can answer it.</p>

<p><strong>In theory, the model works in rounds.</strong> Round one: it asks for every company that fits, and the server writes them all to a file and returns the path to that file &ndash; not the rows. Round two: it asks the server to count that file by Bundesland, and the server reads the file and hands back nine numbers. All that is left is to read off the top three.</p>

<p>It is the same model throughout, one conversation growing turn by turn: each result is fed back in, and it decides the next move from there &ndash; no second model, no handoff, just a file path passed from one of its own calls to the next. The hundreds of rows never enter its head; it sees only the question, a path, and nine numbers.</p>

<p>Two questions in one, then: can something this small plan the moves at all &ndash; and does never holding the data let it run a job it could never carry? Time to find out.</p>

<h2>PTSD</h2>

<p>The setup was three lines: the two tools (one to ask the registry for every match and write them to a file, one to count that file), a one-line system prompt (call one tool at a time, answer when done), and the question. <em>Which three Bundesl&auml;nder hold the most companies above &euro;12 million in assets, and how many each?</em></p>

<p>At first it was flawless. Hammer called <code>export_search</code>, caught the file path that came back, fed it straight into <code>aggregate_file</code>, and got its nine numbers. Five hundred and twenty-three companies had moved through the pipeline and the model had touched none of them &ndash; it held a path and a column of counts, nothing more. The part we doubted it could do at all, it did on the first try.</p>

<p>Then we asked for the answer, and it seized up. We even took the tools away &ndash; nothing left to call, just the numbers and a request for three names. It called a tool anyway: handed back, word for word, the <code>aggregate_file</code> request it had just made. <strong>Drilled so hard to emit a function call, it had forgotten how to speak.</strong></p>

<img src="/images/articles/09-moneyball-ai/moneyball-whiteboard.jpg" alt="Moneyball whiteboard scene: Peter Brand presenting a data-heavy case to a reclined, sceptical Billy Beane" style="max-width:520px;display:block;margin:1.5rem auto;">
<p style="text-align:center;font-size:0.88rem;color:#5a5a5a;"><em>&ldquo;Billy, this is Hammer &ndash; a half-billion-parameter model that runs on a Raspberry Pi. Flawless at picking and calling tools, even from long, convoluted prompts. Its only defect is basically everything else you'd need it for.&rdquo;</em></p>

<p><strong>Mission Accomplished-ish.</strong> The server had written the right companies to a file and the counts came back identical to our control script's &ndash; the pipeline was sound to the last row. What the model could not do was tell us what the file held; the final step, reading nine numbers and naming three. We had to do it by hand, like cavemen.</p>

<p>As for the answer key we had to dig out ourselves: Ober&ouml;sterreich (127), Steiermark (88), and a dead heat between Lower Austria and Tirol on 67.</p>

<h2>What This Suggests</h2>

<p><strong>A model under a billion parameters drove the whole agent.</strong> It chose the tools and chained them correctly; the data never reached it, the server carried that. Twice now the shovel-seller's heresy has held up under test, and we are, against our instincts, turning believer. The paper even named the fix for where it broke &ndash; when real writing is needed, you pair models, one to call tools and another to talk &ndash; which is exactly the gap our run walked into.</p>

<p><strong>It breaks at writing, not at calling.</strong> Routing is cheap; the step that turns a result into the next input is where the parameters go. The only real writing our model ever had to do was the closing sentence &ndash; and that one sentence is the whole of what it got wrong. Calling is reflex; composing is the expensive part.</p>

<p><strong>We tried to swamp it with input &ndash; and couldn't.</strong> As a side quest we buried the question halfway through a fifty-page wall of <a href="https://www.worldfuturefund.org/Documents/maninarena.htm" target="_blank">Theodore Roosevelt</a>, certain the sheer volume would drown the small model. Against our predictions, it found the instruction and called the tool anyway. Big, messy input it shrugs off; the only wall we hit was producing the summary at the end.</p>

<h2>So What?</h2>

<p>We took the shovel salesman at his word, grabbed a spoon, and sent it digging. And dig it did &ndash; it chose where, worked in the right order, and, despite its size, never buckled under the weight. Yet it could not tell us what it had pulled up &ndash; though producing text was the one thing it was built for &ndash; so we hauled it up the last few metres ourselves. It was real, and exactly what we had asked for.</p>

<p>The deep veins are still there &ndash; where the gold sits under judgement, where one wrong turn costs a fortune, where the haul is too heavy for a spoon. Those still want a shovel, and a steady hand. We worked the shallow, well-lit ground, and never tested what the spoon does when the digging gets deep.</p>

<p>But the shallow ground runs a long way. A great deal of the day's labour &ndash; the fetching, the counting, the lists &ndash; is shallow work. And shallow work does not need a five-figure shovel. It needs a spoon, and someone who knows where to dig.</p>

<p>The shovel salesman predicted all of this; we only ran the test. And still the queue for shovels runs long. We are not worried about the shovel salesman &ndash; we are sure he has plenty of golden spoons up his sleeves. And when the next rush comes &ndash; maybe it really is in space, as they say &ndash; we guess he will be there too. Selling shovels, spoons, and everything in between.</p>

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
