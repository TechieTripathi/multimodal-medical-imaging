---
layout: opener
section: 2
---

# How does a computer read an X-ray and a report?

<p>Everything becomes numbers. The trick is making the numbers for a picture and its description agree.</p>

<!--
**Time:** ~0.5 min
**Objective:** Pose the question Part 2 answers.
**Say:** Part two opens the box. A computer cannot look at a picture or read a sentence; it can only do arithmetic. So we will see how an image becomes numbers, how a sentence becomes numbers, and how a model learns to make the two sets of numbers agree when they describe the same thing.
**Transition:** Start with what a neural network actually does.
**Sources:** None — section opener.
-->

---
section: 2
layout: artifact
clicks: 4
tag: actual
tagText: 'ResNet-50 feature maps (a general photo model) on our CT slice'
run: cnn_features.json
sources: [he2016resnet]
---

::title::
# A neural network is a stack of pattern detectors

::default::
<NeuralNetIntuition />

<!--
**Time:** ~1.5 min
**Objective:** Build an intuition for layers: simple patterns first, larger patterns later.
**Say:** A neural network is a long chain of simple steps, organised in layers. Each layer looks for patterns in the output of the layer before. These are real outputs from a well-known network, ResNet-50, when we feed it our patient's CT slice. [click] The early layer responds to edges and brightness: the outline of the body, the vessels. [click] A middle layer responds to textures and outlines. [click] A late layer works on a coarse 14 by 14 grid and responds to large patterns. [click] Finally, a last layer turns those patterns into an answer, but only after the network has been trained on many labelled examples.
**Example:** Like a team: one person spots lines, the next spots shapes made of lines, the last says "that is a lung".
**Try / Notice:** The early maps are sharp and detailed; the late maps are blocky because each square summarises a large region.
**Ask:** None.
**Caveat:** This ResNet-50 was trained on everyday photographs, not medical images; we use it only to show what layers look like. The three channels per layer were picked automatically from hundreds as ones that light up on part of the image.
**Transition:** But what exactly does the network receive? Numbers.
**Sources:** he2016resnet — the ResNet architecture. Run: data/runs/cnn_features.json.
-->

---
section: 2
layout: artifact
clicks: 3
tag: real-data
tagText: 'stored pixel values of our patient’s X-ray'
sources: [lidc2015data, dosovitskiy2021vit]
---

::title::
# To a computer, an X-ray is a grid of numbers

::default::
<PixelsToNumbers />

<!--
**Time:** ~2 min
**Objective:** Make "image = numbers" concrete with real stored values.
**Say:** Our patient's chest X-ray is 2022 by 2022 pixels. Each pixel stores one number, here between about 0 and 15,000, for how much X-ray got through. [click] Zoom into the small yellow square. [click] These are the real stored numbers from the file. Brighter means a higher number. [click] Many modern image models, called vision transformers, first shrink the image to 224 by 224 pixels and cut it into 16 by 16 patches: 196 patches, which the model then treats a bit like words in a sentence.
**Example:** A spreadsheet with four million cells, where the cell value sets the brightness.
**Try / Notice:** The numbers change gradually across the grid: there are no sharp edges in this small patch of lung.
**Ask:** What do you think is lost when 4 million pixels become 50,000?
**Caveat:** The 224 × 224 resize is the standard input for the model we use later (BiomedCLIP). Shrinking an X-ray this much discards fine detail; Part 4 returns to this.
**Transition:** Text goes through the same kind of conversion.
**Sources:** lidc2015data — the X-ray; dosovitskiy2021vit — vision transformers and 16×16 patches.
-->

---
section: 2
layout: artifact
clicks: 2
tag: actual
tagText: 'BiomedCLIP’s own tokenizer, running in this page'
run: ../biomedclip/tokenizer_cases.json
sources: [devlin2019bert, zhang2025biomedclip]
---

::title::
# Text is cut into pieces called tokens

::default::
<TokenizerDemo />

<!--
**Time:** ~1.5 min
**Objective:** Show that text becomes numbers through tokens, using the real vocabulary of the model we use later.
**Say:** A text model cannot read letters either. First the sentence is cut into pieces called tokens. [click] Common words stay whole: "nodule", "lobe", "left". Rarer words are split into pieces that the model knows; the pieces marked in orange continue the word before. [click] Each token is then just a number: its position in a vocabulary of about 29,000 pieces. This is the real tokenizer of BiomedCLIP, running live in this page.
**Example:** "Cardiopulmonary" is one token, because it appears often in medical abstracts; "cardiomegaly" is split into four pieces.
**Try / Notice:** Type any sentence, for example a phrase from your own field, and watch how it is split.
**Ask:** Which words from your speciality do you think will be split up?
**Caveat:** Tokens are only the first step; the model then turns the sequence of tokens into one fingerprint. The vocabulary was learned from PubMed abstracts, so everyday words may split oddly.
**Transition:** So both pictures and words become numbers. What do those numbers look like at the end?
**Sources:** devlin2019bert — WordPiece tokens in BERT-style models; zhang2025biomedclip — BiomedCLIP's text encoder. Tested against the reference tokenizer by scripts/test-wordpiece.mjs.
-->

---
section: 2
layout: artifact
clicks: 2
tag: actual
tagText: 'BiomedCLIP image embeddings, six public datasets'
run: biomedclip_embedding_map.json
sources: [zhang2025biomedclip]
---

::title::
# Every image becomes a fingerprint of numbers

::default::
<EmbeddingMap />

<!--
**Time:** ~2 min
**Objective:** Introduce embeddings as fingerprints, with a real map from a real model.
**Say:** After all its layers, the image encoder of BiomedCLIP turns every picture into a list of 512 numbers. Call it the image's fingerprint, or in the jargon, its embedding. We cannot draw 512 dimensions, so here each fingerprint is squashed down to two numbers and placed on a map. These are 44 real images from six public datasets. [click] Look where they landed: X-rays together, retina photos together, pathology together. [click] Nobody told the model what kind of image each one was. Similar pictures simply get similar fingerprints.
**Example:** Like a library where similar books end up on nearby shelves without anyone reading the labels.
**Try / Notice:** Hover over any thumbnail to enlarge it.
**Ask:** Why might CT and X-ray land near each other?
**Caveat:** Squashing 512 numbers to two (PCA) keeps only about 37% of the variation here, so distances on this map are approximate.
**Transition:** Text gets a fingerprint too. The trick is to make the two kinds agree.
**Sources:** zhang2025biomedclip — the model. Run: data/runs/biomedclip_embedding_map.json.
-->

---
section: 2
layout: artifact
clicks: 2
tag: teaching
---

::title::
# Two encoders, one shared space

::default::
<SharedSpace />

<!--
**Time:** ~2 min
**Objective:** Introduce the idea of a shared space where matching images and words end up close.
**Say:** Here is the key idea of models like CLIP. We have two separate encoders: one turns images into fingerprints, one turns text into fingerprints of the same length. Think of each fingerprint as a position on a map. Images land somewhere on the map. [click] Before training, the descriptions land anywhere; "a brain MRI" is nowhere near the MRI. [click] Training moves things so that each description lands next to the images it describes.
**Example:** Like learning a second language: at first the word and the object are unconnected; with practice they become linked.
**Try / Notice:** The words slide towards their pictures in the last step.
**Ask:** None.
**Caveat:** The real space has hundreds of dimensions, not two, and real positions are never this neat. Next we see real ones.
**Transition:** How does training achieve this? By comparing many pairs at once.
**Sources:** None — conceptual; the method is shown on the next slides.
-->

---
section: 2
layout: artifact
clicks: 3
tag: actual
tagText: 'BiomedCLIP on six IU chest X-rays and their report sentences'
run: biomedclip_contrastive.json
sources: [radford2021clip, zhang2025biomedclip, demnerfushman2016iu]
---

::title::
# Training compares many pairs at once

::default::
<ContrastiveMatrix />

<!--
**Time:** ~2 min
**Objective:** Explain contrastive learning with a batch matrix, then confront it with a real result.
**Say:** Here are six chest X-rays and, on the left, a sentence from each one's report. During training, the model sees a batch like this and scores every picture against every sentence. [click] At the start, every picture looks equally like every sentence. [click] Training rewards a high score on the diagonal, the true pairs, and a low score everywhere else. Repeat this over millions of pairs: that is contrastive learning, the method behind CLIP. [click] Now the real thing. These are BiomedCLIP's actual scores for these six real X-rays. The correct sentence wins for only two of the six. Subtle findings such as a scoliosis or a small granuloma are hard to see at this resolution, and several sentences describe small details.
**Example:** Like a matching exercise in an exam: draw lines between six pictures and six captions.
**Try / Notice:** Click any cell to see its image and sentence with the exact score.
**Ask:** Why might "small calcified granulomata" be hard to match from a 224-pixel image?
**Caveat:** Steps one and two are a cartoon of training. Step three is real, from a model that was trained on figure captions from scientific papers, not on these reports. The report sentences are quoted exactly as written.
**Transition:** What exactly is the score in each cell? Cosine similarity.
**Sources:** radford2021clip — contrastive training (CLIP); zhang2025biomedclip — BiomedCLIP; demnerfushman2016iu — the X-rays and reports.
-->

---
section: 2
layout: artifact
clicks: 2
tag: actual
tagText: 'BiomedCLIP embeddings of our patient’s X-ray, computed live'
run: biomedclip_ranking.json
sources: [radford2021clip, zhang2025biomedclip]
---

::title::
# Cosine similarity: do two arrows point the same way?

::default::
<CosineExplorer />

<!--
**Time:** ~2.5 min
**Objective:** Explain the score behind every image–text comparison, with one worked example.
**Say:** Think of each fingerprint as an arrow. Cosine similarity asks one question: do the two arrows point the same way? One means exactly the same direction, zero means unrelated, minus one means opposite. Drag the arrows to see it. [click] With three numbers each: multiply matching numbers and add them up, which gives 3. Divide by the two arrow lengths, and you get 0.77. [click] The model does exactly the same with 512 numbers. Here is our patient's X-ray against two descriptions. "A mass in the lung" scores 0.41; "a brain MRI" scores much lower. The page computed these just now from the real fingerprints.
**Example:** Two people giving directions: if they both point north-east, they agree, however far away each one thinks the place is.
**Try / Notice:** Drag the blue and orange arrow tips; the cosine updates.
**Ask:** None.
**Caveat:** For this model, real scores fall in a narrow band around 0.2 to 0.5; only the ranking between options is meaningful, not the number itself. A score is not a probability.
**Transition:** Comparing fingerprints is one way to connect images and text. Another lets each word look at the image directly.
**Sources:** radford2021clip — cosine similarity in CLIP; zhang2025biomedclip — the model. Run: data/runs/biomedclip_ranking.json.
-->

---
section: 2
layout: artifact
clicks: 4
tag: teaching
sources: [vaswani2017attention, alayrac2022flamingo]
---

::title::
# Attention: each word looks at the image

::default::
<CrossAttention />

<!--
**Time:** ~1.5 min
**Objective:** Give an intuition for attention and cross-attention.
**Say:** Some multimodal models go further than comparing two fingerprints. With cross-attention, each word in the text can look at the image and decide which parts matter for it. [click] "Nodule" looks at the lump. [click] "Left" looks at the left lung, which is on the right of the screen, because CT is viewed as if facing the patient. [click] "Lower" looks at the lower lobe. [click] And "spiculated" looks at the spiky edge of the nodule. Small words like "the" spread their attention thinly.
**Example:** Like reading a report while pointing at the image with your finger as each word comes up.
**Try / Notice:** Click any word to see where it would look.
**Ask:** Predict, then reveal: where should the word "margin" look?
**Caveat:** The regions are real anatomy on our patient's slice (lungs from TotalSegmentator, the nodule from the radiologists), but the word-to-region links are drawn by hand to explain the idea. Real attention maps are noisier, and they are not a reliable explanation of a model's reasoning.
**Transition:** Attention is one way to combine modalities. Where in the system should the combining happen?
**Sources:** vaswani2017attention — attention; alayrac2022flamingo — cross-attention between text and images.
-->

---
section: 2
layout: artifact
clicks: 2
tag: teaching
sources: [huang2020fusion]
---

::title::
# Where the data meet: early, middle or late

::default::
<FusionBuilder />

<!--
**Time:** ~2 min
**Objective:** Distinguish early, intermediate and late fusion and their trade-offs.
**Say:** There are three broad places to combine modalities. Early fusion joins the raw inputs and trains one model on everything. [click] Intermediate fusion gives each input its own encoder, then joins the fingerprints; this is what most modern systems do. [click] Late fusion trains separate models and only combines their answers, for example by voting.
**Example:** Early fusion is one doctor reading everything at once; late fusion is three specialists who never talk, each casting a vote.
**Try / Notice:** Press "Text missing" in each mode: early fusion breaks worst, late fusion copes but loses the benefit of learning across modalities.
**Ask:** In your setting, which data are most often missing?
**Caveat:** Real systems mix these patterns; the categories are a common way of describing them in reviews.
**Transition:** Images and text are not the only inputs. What about numbers from the record?
**Sources:** huang2020fusion — systematic review of image and health-record fusion that uses these categories.
-->

---
section: 2
layout: artifact
clicks: 3
tag: illustrative
sources: [huang2020fusion]
---

::title::
# Numbers from the record need care

::default::
<StructuredData />

<!--
**Time:** ~1.5 min
**Objective:** Show how structured clinical data enters a model, and why missing values are the central problem.
**Say:** Lab results and history are already numbers, but they need preparing. [click] Each is scaled to a similar range so no single value dominates. [click] And many are simply missing: the blood test was not done, the earlier scan is unknown. A careful model is told explicitly what is missing, with a separate flag, rather than being fed a silent zero. [click] Then the record joins the image fingerprint and the model learns from both.
**Example:** A zero for a blood test that was never taken is not the same as a measured zero.
**Try / Notice:** The orange cells are the missing values and their flags.
**Ask:** How complete are the records in your institution?
**Caveat:** The patient values here are invented for illustration; our real patient has no record in the public data.
**Transition:** That completes the building blocks. Next: how are such models trained and tested?
**Sources:** huang2020fusion — handling of structured EHR data alongside images.
-->
