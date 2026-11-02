---
layout: opener
section: 7
---

# What can go wrong, and who is responsible?

<p>Data, shift, privacy and checking. Most failures are not in the model.</p>

<!--
**Time:** ~0.5 min
**Objective:** Pose the question Part 7 answers.
**Say:** We have seen the models work and fail. The last part is about why they fail, and what we, as people who teach, research and treat, are responsible for.
**Transition:** It starts with the data.
**Sources:** None — section opener.
-->

---
section: 7
layout: artifact
clicks: 2
tag: real-data
tagText: 'from this session’s own datasets'
sources: [fedorov2018lidcdicom, demnerfushman2016iu, armato2011lidc]
---

::title::
# Data and labels are never perfect

::default::
<LabelNoise />

<!--
**Time:** ~2.5 min
**Objective:** Show label disagreement, label noise and representativeness with this session's data.
**Say:** Three problems, all from the data we used today. Experts disagree: the four radiologists rated our patient's nodule 5, 5, 5 and 4 for malignancy, and anywhere from 3 to 5 for spiculation; their outlines differ in volume by more than a cubic centimetre. [click] Labels taken from text are noisy: this X-ray was labelled "cardiomegaly" from its report keywords, but the report says the heart is at the upper limit of normal. [click] And who is in the data? Our X-ray, CT and MRI data all come from US hospitals. A model learns the population it saw.
**Example:** If the training answer key is uncertain, the model's "accuracy" is uncertain too.
**Try / Notice:** None.
**Ask:** Where do the labels in your own datasets come from?
**Caveat:** LIDC deliberately kept all four readers' opinions rather than forcing agreement, which is good practice.
**Transition:** Even with good labels, a model can fail when the images change.
**Sources:** fedorov2018lidcdicom; armato2011lidc — the four-reader design; demnerfushman2016iu.
-->

---
section: 7
layout: artifact
clicks: 2
tag: actual
tagText: 'BiomedCLIP on the same X-rays, changed in software'
run: biomedclip_shift.json
sources: [zech2018generalization, degrave2021shortcuts, geirhos2020shortcut]
---

::title::
# A new scanner can quietly lower accuracy

::default::
<ShiftIllustrator />

<!--
**Time:** ~2.5 min
**Objective:** Show domain shift with a real measurement and a published example.
**Say:** Here is our cardiomegaly test from Part 3, AUROC 0.90. [click] Now we change the same images slightly, as a different scanner or setting might: darker, lower contrast, blurred, lower resolution. Same patients, same hearts. The AUROC drops step by step, to about 0.85 at low resolution. Nobody would notice by looking at the score of a single image. [click] In practice it is worse. A study of chest X-ray models found that networks could tell which hospital an image came from 99.95% of the time, and pneumonia models performed worse at hospitals they had not seen. Models also pick up shortcuts: markers, text, positioning.
**Example:** A student who learned to spot pneumonia from the portable X-ray machine's label, not from the lungs.
**Try / Notice:** The bars shrink from left to right.
**Ask:** Has your hospital changed scanners in the last five years?
**Caveat:** Our changes are simulated in software, not real images from another hospital.
**Transition:** The other risk is to the patient's privacy.
**Sources:** zech2018generalization — 99.95% hospital identification; degrave2021shortcuts and geirhos2020shortcut — shortcut learning. Run: data/runs/biomedclip_shift.json.
-->

---
section: 7
clicks: 3
sources: [dpdp2023act, pib2025dpdprules, cdsco2026mdsw, dicomstandard]
---

# Privacy, security and regulation

<PrivacyChecklist />

<!--
**Time:** ~2.5 min
**Objective:** Set out the duties before patient images reach any AI system.
**Say:** Four duties. First, de-identify: blank the identifying tags, mask burned-in text, as we did with two letters on our patient's X-ray, and remember that a head CT can be turned back into a face. [click] Second, protect: never upload patient files to public AI tools or online notebooks. [click] Third, follow the law. In India, the Digital Personal Data Protection Act of 2023 covers personal data, and its Rules were notified in November 2025, coming into force in phases over 18 months. [click] Fourth, regulation: software meant for diagnosis can be a medical device. CDSCO published guidance on medical device software under the Medical Devices Rules in July 2026.
**Example:** Public datasets like ours were de-identified by their publishers; hospital files are not.
**Try / Notice:** None.
**Ask:** Who in your institution approves sharing imaging data for research?
**Caveat:** This is not legal advice. Laws and guidance change; check the current official texts and your ethics committee before any study.
**Transition:** Finally: how do we check what a model says?
**Sources:** dpdp2023act; pib2025dpdprules; cdsco2026mdsw; dicomstandard — de-identification profiles.
-->

---
section: 7
layout: artifact
clicks: 4
tag: simulated
sources: [fedorov2018lidcdicom, tu2024medpalmm]
---

::title::
# Check every sentence against the evidence

::default::
<ReportClaimChecker />

<!--
**Time:** ~2.5 min
**Objective:** Practise validation and human oversight of generated text; discuss explainability.
**Say:** Imagine an assistant wrote this report for our patient. Check it sentence by sentence. [click] "A 3 cm spiculated mass in the left lower lobe": supported; the CT shows it and four radiologists measured 32 to 34 millimetres. [click] "Suspicious for malignancy": supported by three of four readers, but it still needs a biopsy. [click] "No enlarged lymph nodes": nobody in our data checked that; a person must look. [click] "Unchanged since the previous scan": there is no previous scan. Invented. One invented sentence is enough to change management.
**Example:** Explanations such as heat maps can help a reviewer, but they show where a model looked, not whether it is right.
**Try / Notice:** Click any sentence to see its evidence.
**Ask:** Who signs this report, and how long would checking it take?
**Caveat:** The report is written by us to illustrate; we did not run a report-generation model. The evidence shown is real.
**Transition:** Let's pull it together.
**Sources:** fedorov2018lidcdicom — the readers' measurements and ratings; tu2024medpalmm — report generation research.
-->

---
section: 7
clicks: 1
---

# What to take home

<Takeaways />

<!--
**Time:** ~2.5 min
**Objective:** Consolidate the session and open questions; take questions.
**Say:** Four things to remember. Multimodal AI works by turning images and words into numbers that can be compared. The details of how medical images are stored, such as units, slice order and windows, change the results. Wording, preparation and changes in the data all move the scores. And a score is not a diagnosis: validate locally and keep a clinician in charge. [click] And for researchers in the room, four open problems worth working on, starting with models trained and tested on our own patients and scanners. The notebook and all the data sources are yours to take away. Questions?
**Example:** The companion notebook reproduces every real number in this deck.
**Try / Notice:** None.
**Ask:** Which of these research questions could your department take on?
**Caveat:** None.
**Transition:** Questions and discussion.
**Sources:** None — summary.
-->
