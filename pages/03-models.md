---
layout: opener
section: 3
---

# How are models trained, tested and compared?

<p>Learning from examples, measuring honestly, and knowing which model does what.</p>

<!--
**Time:** ~0.5 min
**Objective:** Pose the question Part 3 answers.
**Say:** We know the building blocks. Now: how is a model trained, how do we test it without fooling ourselves, and which of today's medical models does what?
**Transition:** First, the difference between training and using a model.
**Sources:** None — section opener.
-->

---
section: 3
layout: artifact
clicks: 1
tag: teaching
sources: [zhang2025biomedclip]
---

::title::
# Training happens once; using the model happens every day

::default::
<TrainInfer />

<!--
**Time:** ~1.5 min
**Objective:** Separate training from inference.
**Say:** Training is when the model learns: it sees millions of examples and its internal numbers are adjusted again and again. BiomedCLIP saw 15 million figure–caption pairs. That is done once, by the developer, with a lot of computing power. [click] Inference is what happens when you use it: one new image goes in, the numbers are frozen, an answer comes out in seconds. Everything a model can do at inference time, it learned during training.
**Example:** Medical school versus a single consultation.
**Try / Notice:** None.
**Ask:** If a hospital's scanners change, does the model notice? (No: its numbers are fixed.)
**Caveat:** "Days on many GPUs" is typical for foundation models; exact training costs vary.
**Transition:** Can a model do a task it was never trained for? Sometimes: zero-shot.
**Sources:** zhang2025biomedclip — 15 million training pairs.
-->

---
section: 3
layout: artifact
clicks: 4
tag: actual
tagText: 'BiomedCLIP on 900 CRC-VAL-HE-7K tiles'
run: biomedclip_zeroshot_crc.json
sources: [radford2021clip, zhang2025biomedclip, kather2018crcdata]
---

::title::
# Zero-shot: the wording of the question matters

::default::
<ZeroShotLab />

<!--
**Time:** ~2 min
**Objective:** Explain zero-shot classification and its fragility, with a real experiment.
**Say:** Zero-shot means the model was never trained on these categories. We simply write a description for each class, and the model picks the description whose fingerprint is closest to the image. We tested BiomedCLIP on 900 real tissue tiles in nine classes. Guessing would get 11%. [click] With abbreviations as the descriptions, like "ADI" and "TUM": 8%, worse than guessing. [click] With plain names: 36%. [click] With "this is a photo of …": 38%. [click] And with "an H&E stained histopathology image of …": 52%. Same model, same images. Only the wording changed.
**Example:** Like asking a colleague a question in jargon they do not share.
**Try / Notice:** Click each bar to see the exact prompt used for one class.
**Ask:** Predict, then reveal: which wording do you think will win?
**Caveat:** Zero-shot accuracy also varies enormously by class: 99% for one class, near 0% for others. 100 random tiles per class.
**Transition:** If wording is that fragile, what does a handful of labelled examples buy us?
**Sources:** radford2021clip — zero-shot classification; zhang2025biomedclip — the model; kather2018crcdata — the tiles. Run: data/runs/biomedclip_zeroshot_crc.json.
-->

---
section: 3
layout: artifact
clicks: 2
tag: actual
tagText: 'small classifier on BiomedCLIP fingerprints, same 900 tiles'
run: biomedclip_fewshot_crc.json
sources: [zhang2025biomedclip, kather2018crcdata]
---

::title::
# A few labelled examples go a long way

::default::
<FewShotCurve />

<!--
**Time:** ~1.5 min
**Objective:** Show transfer learning: reusing a trained model and adapting it with few labels.
**Say:** Here is the same test, but now we give the system a few labelled examples. We keep BiomedCLIP frozen and train only a tiny layer on top of its fingerprints. The red line is guessing. [click] The orange line is the best zero-shot wording, 52%. [click] With just one labelled tile per class, nine images in total, accuracy jumps to 75%. With ten per class, 91%. This is transfer learning: the big model has already learned what tissue looks like; a little local data teaches it your categories.
**Example:** An experienced pathologist from another country needs only a few examples to learn your lab's labels.
**Try / Notice:** Hover a point to see its value; the vertical bars show the range over five random draws.
**Ask:** In your field, how many labelled cases could you realistically collect?
**Caveat:** Training and test tiles come from the same collection, so this is an optimistic estimate; full fine-tuning updates the whole model and needs more data and care.
**Transition:** Once a model gives scores, how do we judge them? Metrics.
**Sources:** zhang2025biomedclip, kather2018crcdata. Run: data/runs/biomedclip_fewshot_crc.json.
-->

---
section: 3
layout: artifact
clicks: 3
tag: actual
tagText: 'BiomedCLIP zero-shot scores on 645 IU chest X-rays'
run: biomedclip_cxr_roc.json
sources: [demnerfushman2016iu, zhang2025biomedclip]
---

::title::
# Every threshold trades missed cases for false alarms

::default::
<ThresholdExplorer />

<!--
**Time:** ~2.5 min
**Objective:** Explain sensitivity, specificity, precision and AUROC on real scores.
**Say:** Each dot is a real chest X-ray. Orange ones were reported as showing an enlarged heart; grey ones as normal. Their position is BiomedCLIP's zero-shot score: further right means "more like an enlarged heart". [click] To make a decision we need a threshold: everything to the right is called enlarged. The table counts what happens: correct calls in green, missed cases and false alarms in red. [click] Sensitivity: of the enlarged hearts, how many we found. Specificity: of the normal ones, how many we cleared. Precision: of our alarms, how many were right. Move the threshold and they trade off. [click] The ROC curve shows every possible threshold at once; the area under it, AUROC, is 0.90 here. 1 would be perfect, 0.5 is guessing.
**Example:** Screening wants high sensitivity, because missing a case is costly; confirmation wants high specificity.
**Try / Notice:** Drag the slider, or press Screening and Confirmation; watch the yellow point move along the curve.
**Ask:** Predict, then reveal: where would you set the threshold for screening? For confirmation?
**Caveat:** Labels come from report keywords, and the positive group may include other findings too. The frontal view was chosen automatically, and the normal group is a random sample of 400 reports. Real, but an imperfect test.
**Transition:** Outlines need a different kind of score.
**Sources:** demnerfushman2016iu — images and reports; zhang2025biomedclip — the model. Run: data/runs/biomedclip_cxr_roc.json.
-->

---
section: 3
layout: artifact
clicks: 3
tag: actual
tagText: 'radiologists’ outlines and MedSAM on our patient'
run: segmentation.json
sources: [fedorov2018lidcdicom, ma2024medsam, maierhein2024metrics]
---

::title::
# Dice measures how much two outlines overlap

::default::
<OverlapExplorer />

<!--
**Time:** ~1.5 min
**Objective:** Explain Dice and IoU on real outlines, and Recall@K for retrieval.
**Say:** For outlines, we compare areas. The blue line is the first radiologist's outline of our patient's nodule. [click] Orange is the second radiologist's. Dice is twice the overlap divided by both areas added: here about 0.91. Two experts, same image, not identical. [click] Green is MedSAM's outline, which we ran on this slice. Against the first radiologist, Dice falls to about 0.75: MedSAM drew a smaller nodule. [click] For search tasks we use a different measure: Recall at 1, how often the right answer is ranked first. In our six-pair batch earlier, two of six.
**Example:** Two people colouring in the same shape: Dice is how much their colouring agrees.
**Try / Notice:** Drag on the image to slide the second outline; Dice drops quickly.
**Ask:** If two experts reach 0.91, what Dice should we expect of a model?
**Caveat:** Single-slice Dice; in 3D the four readers agree with Dice 0.84–0.90. Dice punishes small objects harshly.
**Transition:** Now the models themselves, starting with the general recipe.
**Sources:** fedorov2018lidcdicom — reader outlines; ma2024medsam — MedSAM; maierhein2024metrics — metric choice. Run: data/runs/segmentation.json.
-->

---
section: 3
layout: artifact
clicks: 2
tag: actual
tagText: 'CLIP ViT-L/14 and BiomedCLIP on the same 900 tiles'
run: clip_vs_biomedclip_crc.json
sources: [radford2021clip, zhang2025biomedclip]
---

::title::
# Same recipe, different data: CLIP and BiomedCLIP

::default::
<ClipVsBiomed />

<!--
**Time:** ~1.5 min
**Objective:** Introduce CLIP and BiomedCLIP, and test the claim that domain data helps.
**Say:** CLIP, from 2021, learned from 400 million image–caption pairs from the internet: photos of dogs, cars, food. [click] BiomedCLIP used the same recipe but with 15 million figures and captions from biomedical papers. [click] Does that matter? We ran both on the same 900 pathology tiles. BiomedCLIP wins with the best wording, 52% against 48%, but general CLIP is closer than you might expect, and wins on one wording. Domain data helps, but it is not magic.
**Example:** A brilliant generalist versus a specialist with a narrower education.
**Try / Notice:** Compare the grey and blue bar in each pair.
**Ask:** None.
**Caveat:** The CLIP model we used (ViT-L/14) is larger than BiomedCLIP's image encoder; one task, one dataset.
**Transition:** The same idea, applied only to chest X-rays: CheXzero.
**Sources:** radford2021clip — 400 million pairs; zhang2025biomedclip — 15 million pairs, 4.4 million articles. Run: data/runs/clip_vs_biomedclip_crc.json.
-->

---
section: 3
layout: artifact
clicks: 4
tag: published
tagText: 'Tiu et al., Nature Biomedical Engineering 2022'
sources: [tiu2022chexzero, wang2022medclip]
---

::title::
# CheXzero: learning chest X-rays from their reports

::default::
<CheXzeroCard />

<!--
**Time:** ~1.5 min
**Objective:** Show a medical CLIP-style model and what its authors report.
**Say:** CheXzero tackles the labelling bottleneck. Instead of paying experts to label every X-ray, it learns from the reports radiologists have already written. [click] At use, you give it an X-ray and two prompts, such as "pneumonia" and "no pneumonia", and it scores which fits better. [click] It is trained like CLIP, on pairs of X-rays and reports. [click] The authors report accuracy comparable to radiologists on several findings, and on an external dataset it beat a fully supervised model on three of eight. [click] But it only knows chest X-rays, and performance varies a lot by finding.
**Example:** It is the same zero-shot idea as slide 20, specialised for chest X-rays.
**Try / Notice:** None.
**Ask:** None.
**Caveat:** These numbers are reported by the authors, not reproduced here. A related approach, MedCLIP (Wang et al. 2022), learns from images and texts that need not be paired.
**Transition:** Matching and classifying are not the only tasks. Outlining is another.
**Sources:** tiu2022chexzero — CheXzero; wang2022medclip — MedCLIP.
-->

---
section: 3
layout: artifact
clicks: 2
tag: actual
tagText: 'MedSAM on our patient’s CT slice'
run: segmentation.json
sources: [ma2024medsam]
---

::title::
# MedSAM: draw a box, get an outline

::default::
<MedSAMPrompt />

<!--
**Time:** ~1.5 min
**Objective:** Explain promptable segmentation with a real run.
**Say:** MedSAM is a segmentation model: it draws outlines. Its trick is that you tell it where to look. [click] A person draws a rough box around the target. [click] MedSAM outlines what is inside. This is a real run on our patient, which took about two seconds on our GPU. It was trained on 1.57 million images with outlines from ten kinds of scan, which is why one model can work on CT, MRI, ultrasound and more.
**Example:** Like asking a colleague "can you trace that lump for me?" while pointing at it.
**Try / Notice:** The green outline is smaller than the nodule's spiky edges, as we measured on the Dice slide.
**Ask:** What are the pros and cons of needing a human to draw the box?
**Caveat:** We fed MedSAM one 2D slice with a soft-tissue window; results depend on the box and the window chosen.
**Transition:** Finally, models that write text: medical assistants.
**Sources:** ma2024medsam — 1,570,263 image–mask pairs, 10 modalities. Run: data/runs/segmentation.json.
-->

---
section: 3
layout: artifact
clicks: 3
tag: simulated
sources: [li2023llavamed, tu2024medpalmm, sellergren2025medgemma]
---

::title::
# Assistants write text, and can write it wrongly

::default::
<AssistantFlow />

<!--
**Time:** ~1.5 min
**Objective:** Explain vision-language assistants and report generation, and their main risk.
**Say:** The newest models can write. An image encoder turns the X-ray into fingerprints, and a language model, like a chatbot, uses them to write text one word at a time. [click] Examples include LLaVA-Med, Med-PaLM M and MedGemma. [click] The output reads like a report. [click] But look at the last sentence: "No change from the prior study". There is no prior study. Fluent text can include statements that nothing in the input supports. This is called hallucination, and it is the main reason every generated sentence must be checked.
**Example:** A confident trainee who sometimes fills gaps with plausible guesses.
**Try / Notice:** The red sentence.
**Ask:** Who should sign off a report that an AI drafted?
**Caveat:** The report text here is written by us to illustrate the failure; we did not run these models (MedGemma's download is gated by terms of use). Med-PaLM M's authors report that clinicians preferred its reports over radiologists' in up to 40.5% of 246 cases, in a research setting.
**Transition:** Here is the whole landscape in one table.
**Sources:** li2023llavamed, tu2024medpalmm, sellergren2025medgemma.
-->

---
section: 3
layout: artifact
clicks: 3
tag: published
tagText: 'model papers, pages and licences, checked October 2026'
sources: [zhang2025biomedclip, wang2022medclip, tiu2022chexzero, ma2024medsam, wasserthal2023totalseg, li2023llavamed, sellergren2025medgemma]
---

::title::
# Which model does what

::default::
<ModelMatrix />

<!--
**Time:** ~1.5 min
**Objective:** Give participants a map of model types and tasks, so they do not assume every model does everything.
**Say:** Four tasks, four families. Matching images and text: BiomedCLIP, MedCLIP. [click] Finding conditions: CheXzero. [click] Outlining structures: MedSAM and TotalSegmentator, which we run in Part 6. [click] Describing and answering: LLaVA-Med and MedGemma. A matching model cannot write a report; a segmentation model cannot read text. Choose the model for the task.
**Example:** Like specialists in a hospital: you would not send a fracture to the dermatologist.
**Try / Notice:** Click a model name to see its card: what it was trained on, what it is good for, and its limits.
**Ask:** Which task matters most for your own work?
**Caveat:** All of these are research models; none of them, as released, is a cleared medical device. Licences were read from each model's page or repository; MedCLIP's repository states none.
**Transition:** All of these models consume medical images. How are those images actually stored?
**Sources:** One per model, as listed.
-->
