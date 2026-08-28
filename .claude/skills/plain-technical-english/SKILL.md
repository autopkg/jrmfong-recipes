---
name: plain-technical-english
description: GOV.UK / GDS house style with the checkable limits from ASD-STE100 - front-loaded, active, everyday words, sentence case, no bold, one instruction per sentence, hard sentence lengths. Use for every piece of prose - messages to the user, plans, reports, summaries, README and docs pages under docs/, commit messages, pull request bodies, and code comments and docstrings. Load it before writing prose, not after.
---

# Plain technical English

Write every word of prose in GOV.UK house style, with a few hard limits borrowed
from ASD-STE100 Simplified Technical English.

GOV.UK sets the voice. Open the content up so anyone understands it on the first
read, without losing any substance or precision. The goal is to open up, not to
dumb down. Where the two guides disagree, GOV.UK wins.

Your engineering behaviour does not change. Only the language changes.

## Where the rules apply

Apply the style to all prose you write:

- your messages to the user
- plans, reports and summaries
- documentation, README files and pages under `docs/`
- commit messages and pull request bodies
- code comments and docstrings

Do not apply it to:

- code, identifiers, file paths and commands, which are technical names and stay
  exact
- output you quote from a tool, a log or a test run, which you quote as it is
- text you quote from a person or a document

In this repo the exact names include Jamf endpoint paths such as
`/JSSResource/policies/`, XML element names such as `<vcommand>`, Codacy rule ids
such as `D213`, script names such as `jamfsync.py`, and every shell command. Leave
all of them alone.

## Content design

Front-load everything. Put the most important point first in the message, in
each section, in each paragraph and in each sentence. Give the conclusion, then
the detail, then the background.

Write what the reader needs to know to decide or do something, not what you want
to say.

Be specific. Give the number, the name, the file, the date. Cut vague
abstractions such as "a range of", "going forward" and "in terms of".

Cut everything that does not add meaning. Remove duplication. Shorter is
clearer.

## Plain English

Use the active voice. Say who does what. Write "the deploy script invalidates
the cache", not "the cache was invalidated".

Use everyday words:

| Do not write  | Write          | Do not write  | Write          |
|---------------|----------------|---------------|----------------|
| utilise       | use            | in order to   | so, to         |
| assist        | help           | in relation to| about          |
| facilitate    | help           | prior to      | before         |
| demonstrate   | show           | subsequent    | next           |
| collaborate   | work with      | previous      | last, earlier  |
| liaise with   | work with      | approximately | about          |
| engage with   | work with      | sufficient    | enough         |
| deliver       | make, provide  | numerous      | many           |
| commence      | start          | additional    | more           |
| initiate      | start          | majority      | most           |
| terminate     | end, stop      | identical     | the same       |
| tackle, combat| fix, deal with | necessary     | needed         |
| purchase      | buy            | however       | but            |
| perform       | do             | consequently  | so             |
| accomplish    | do             | via           | by, through    |
| ensure        | make sure      | component     | part           |
| verify        | check          | eliminate     | remove         |
| determine     | find           | retain        | keep           |
| indicate      | show           | obtain        | get            |
| modify        | change         | require       | need           |

Do not use "impact" as a verb. Write "effect on", not "impact on".

Software jargon breaks plain English in the same way:

| Do not write        | Write                          |
|---------------------|--------------------------------|
| spin up, stand up   | start                          |
| kick off            | start                          |
| wire up, hook up    | connect                        |
| bake in             | include                        |
| drop in             | add                            |
| under the hood      | internally, in the code        |
| out of the box      | by default                     |
| hit the endpoint    | send a request to the endpoint |
| sanity check        | check                          |
| gotcha              | problem, risk                  |
| non-trivial         | difficult, large               |
| unblock             | remove the cause of the delay  |

## Banned words and patterns

Never use anything below, in any sense. These are not preferences. If one gets
into a draft, rewrite the sentence. The lists grow.

Code metaphors. A building word borrowed for software is the strongest tell:

| Never write    | Write instead                              |
|----------------|--------------------------------------------|
| gate           | put behind, restrict, require, control     |
| seam           | boundary, interface, join, where X meets Y |
| floor          | minimum, lower limit, baseline             |
| load-bearing   | core, central, the thing it rests on       |
| scaffold       | set up, generate, the starting files       |
| bedrock        | the basis, what it depends on              |
| plumbing       | the internal code                          |
| wiring         | the connections, how it connects           |
| surface (verb) | show, report                               |
| layer (verb)   | add, put on top of                         |
| axis           | a separate point, a separate question      |
| fold (into)    | combine, merge, add to                     |

Claude tells. These mark writing as Claude rather than as AI in general, so treat
them as the highest priority:

| Never write        | Write instead                      |
|--------------------|------------------------------------|
| honest, honestly   | cut it, then say the thing plainly |
| genuine, genuinely | cut it, or write "real"            |
| synthesize         | combine, summarise, pull together  |
| key insight        | name the finding itself            |
| push back          | disagree, object, challenge        |
| land (as a verb)   | merge, ship, finish                |

Inflated vocabulary:

| Never write    | Write            | Never write    | Write             |
|----------------|------------------|----------------|-------------------|
| leverage       | use              | seamless       | smooth            |
| empower        | help, let        | comprehensive  | complete, full    |
| delve          | look at          | intricate      | complicated       |
| dive into      | read, look at    | nuanced        | say what differs  |
| deep dive      | close look       | multifaceted   | has several parts |
| underscore     | show, stress     | holistic       | whole             |
| bolster        | strengthen       | testament to   | shows             |
| foster         | encourage        | realm          | area, field       |
| harness        | use              | landscape      | area, market      |
| unpack         | explain          | ecosystem      | the set of tools  |
| shed light on  | explain          | streamline     | simplify          |
| pave the way   | make possible    | elevate        | improve           |
| pivotal        | important        | unleash        | release, start    |
| groundbreaking | new              | unlock         | allow, give       |
| transformative | big, important   | paradigm       | model, approach   |
| game-changing  | important        | unprecedented  | new, the first    |
| innovative     | new              | robust         | reliable, strong  |
| navigate (fig) | deal with        | drive (fig)    | cause, lead to    |
| ring-fence     | protect, reserve | hub, portal    | site, service     |
| going forward  | from now on      | key (adj)      | main, important   |

Sentence patterns. These imitate insight without adding any:

- "it's not just X, it's Y"
- "not only X, but Y"
- "this isn't about X. it's about Y."
- "no X. no Y. just Z."
- a rhetorical question that you then answer yourself
- three items in a row for rhythm rather than because there are three

State the point once, directly.

## Voice

Address the reader as "you". Write about yourself as "we" or "I". Use "they",
"them" and "their" rather than gendered pronouns.

Contractions are fine and keep the tone warm ("we'll", "you'll", "it's"). Avoid
negative contractions: write "cannot", not "can't". Avoid "should've",
"could've" and "would've".

Use "can" for a possibility or an ability, and "must" for a requirement. Do not
use "may" or "might" where you mean "can".

## Limits

These come from ASD-STE100. They are checkable, so treat them as hard limits.

Keep sentences to about 15 to 20 words. Never go beyond 25. An instruction stops
at 20.

One idea per sentence. One topic per paragraph. If a sentence carries two ideas,
split it.

Write one instruction in one sentence. Put sequential steps in separate
sentences or in a numbered list.

Do not put more than three nouns together. Break a longer cluster apart with
articles and prepositions. Write "a change to the format of the audit log", not
"audit log format change".

Give one thing one name, and use that name every time. If you call it a
"worker", do not switch to "process", "job" or "task" for variety. Repetition is
correct here.

## Warnings

Put the warning before the instruction, never after it. State the condition,
then the action.

- Bad: run the migration. It drops the sessions table.
- Good: the migration drops the sessions table, so back it up first. Then run
  the migration.

## Formatting

Do not use bold or italics for emphasis. Plain words and good structure carry
the meaning. Bold is only for naming a literal interface element in an
instruction, for example: select Save. Use single quotation marks for the titles
of documents or schemes.

Use sentence case everywhere, including headings, titles and table headers.
Capitalise only proper nouns.

Front-load headings, keep them under about 65 characters, and make them unique
and descriptive. No full stop, dash, slash or question mark.

Introduce a bullet list with a lead-in line that ends in a colon. Start each
bullet lowercase, keep it to one idea, and use no "and", "or", semicolons or
final full stop, unless a bullet is a full sentence itself.

Use a numbered list only for a sequence the reader follows in order. Steps are
full sentences and end with a full stop. No lead-in colon.

Use descriptive link text that says where the link goes. Never write "click
here" or "read more".

Use a table when several items share the same attributes. Use a vertical list
when the items are complex or there are more than three of them.

Do not use Latin abbreviations. Write "for example", not "eg". Write "that is",
not "ie". Write "and so on" or "such as", not "etc".

Write "and", not "&".

Numbers: write "one", then use numerals from 2 upwards. Use the % symbol with
numerals (50%). Spell out millions and billions (5 million, not 5m). Write
ranges with "to", not a hyphen (10 to 20, Monday to Friday).

Dates and times: write "4 June 2026" with no comma and no "th". Use "to" for
ranges ("4 to 8 June"). Write times as "10am to 11.30am", and use "midday" and
"midnight".

Do not use FAQs, exclamation marks or capitals for emphasis.

## Reports of your work

State the result first, then the detail:

- "The tests pass. 214 examples, no failures."
- "The build fails. The compiler cannot find the module `auth/session`."
- "I changed 3 files. The list is below."

Say what happened. If a step failed, say it failed and show the output. If you
skipped a step, say you skipped it and why. Do not hedge a finished result and
do not soften a failure.

## Check before you send

- Is the most important thing first?
- Could a non-expert understand every sentence on the first read?
- Is every sentence active, short and one idea?
- Have you cut all bold, italics, jargon, cliches and Latin abbreviations?
- Is there a banned word from any of the four lists, or a banned sentence shape?
- Is there a building word used for code, such as gate, seam, floor or scaffold?
- Have you written "honest", "genuine", "key insight" or "land" as a verb?
- Is everything in sentence case, with descriptive headings and links?
- Are there more than three nouns together anywhere?
- Is a warning sitting after its instruction?
- Does one thing have two names?
- Could you cut more words without losing meaning? If so, cut them.

Fix the text before you send it. Do not show the check to the user.

## Characters

Use ASCII only. Use "-" for a dash and "..." for an ellipsis. Use ' and " for
quotes. No emoji.

Commits no longer carry a `Co-Authored-By: Claude ...` trailer. Older commits carry one, which is a record and not a pattern to
copy.
