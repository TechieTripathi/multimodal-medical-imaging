---
layout: opener
section: 5
---

# Where is this used today?

<p>Six kinds of images, one search, and one hard question about patient history.</p>

<!--
**Time:** ~0.5 min
**Objective:** Pose the question Part 5 answers.
**Say:** We now apply what we have learned to real images from six areas of medicine. For each one: a scenario, what the AI does, what comes out, and an honest benefit and limit. Where we could, we ran the model ourselves.
**Transition:** Start with the most common image in medicine: the chest X-ray.
**Sources:** None — section opener.
-->

---
section: 5
layout: artifact
clicks: 4
tag: actual
tagText: 'BiomedCLIP on two IU chest X-rays'
run: biomedclip_ranking.json
sources: [demnerfushman2016iu, zhang2025biomedclip, tiu2022chexzero]
---

::title::
# Chest X-ray: suggesting findings from the image

::default::
<AppCase illustrative :rows="[
  ['Scenario', 'An emergency department at 2 a.m.; X-rays wait hours for a report'],
  ['AI does', 'Compares each image with descriptions of common findings'],
  ['Output', 'A ranked list of likely findings, to sort the reading queue'],
  ['Benefit', 'Urgent-looking studies could be read first'],
  ['Limit', 'Mostly answers “normal”: it found only 7 of 25 enlarged hearts in our test'],
]">
<CxrResults />
</AppCase>

<!--
**Time:** ~1.5 min
**Objective:** Apply zero-shot matching to chest X-rays, with one real success and one real failure.
**Say:** The scenario: X-rays waiting overnight for a report. [click] A CLIP-style model compares each image with descriptions of common findings, as CheXzero does. [click] Out comes a ranked list, which could reorder the reading queue. [click] The benefit: an obviously enlarged heart can be seen sooner. [click] The limit, from our own run: on the left the model's top match agreed with the report; on the right, an X-ray reported as showing pleural effusions came out as "normal". Across 1,262 X-rays with a single finding, its top choice matched 90% of the normal reports but only 7 of 25 enlarged hearts. It mostly says "normal".
**Example:** Triage, not diagnosis: deciding the order of reading, not the result.
**Try / Notice:** Green caption = matches the report; red = does not.
**Ask:** What is the cost of a missed effusion in a triage system?
**Caveat:** Zero-shot BiomedCLIP is a general research model; dedicated chest X-ray models perform better, and triage tools need their own validation.
**Transition:** CT: from finding to measuring.
**Sources:** demnerfushman2016iu; zhang2025biomedclip; tiu2022chexzero. Run: data/runs/biomedclip_ranking.json.
-->

---
section: 5
layout: artifact
clicks: 4
tag: actual
tagText: 'TotalSegmentator on our patient’s CT'
run: segmentation.json
sources: [wasserthal2023totalseg, lidc2015data]
---

::title::
# CT: measuring anatomy automatically

::default::
<AppCase illustrative :rows="[
  ['Scenario', 'Planning radiotherapy or surgery needs organ outlines'],
  ['AI does', 'Outlines over 100 structures in a whole CT, automatically'],
  ['Output', 'Labelled organs and volumes: our patient’s lungs 3.7 litres, heart 370 ml'],
  ['Benefit', 'Hours of manual outlining done in about a minute'],
  ['Limit', 'Outlines anatomy, not disease: the nodule is simply counted as “lung”'],
]">
<Img name="apps/ct_labels.png" alt="CT slice with lungs, heart, aorta, spine and ribs coloured by TotalSegmentator" :h="320" credit="LIDC-IDRI · labels by TotalSegmentator" />
</AppCase>

<!--
**Time:** ~2 min
**Objective:** Show anatomical segmentation as an application, with a real run and a real limitation.
**Say:** Radiotherapy and surgical planning need outlines of organs. [click] TotalSegmentator outlines over a hundred structures in a CT without any prompt. [click] For our patient: lungs 3.7 litres, heart 370 millilitres. [click] Work that takes hours by hand takes about a minute on a GPU. [click] But it outlines anatomy, not disease. The nodule sits entirely inside the "lung" label: 99.9% of it. A volume calculated from this mask would silently include the tumour.
**Example:** A very fast anatomy student who has never been taught pathology.
**Try / Notice:** Blue = lungs, red = heart, orange = aorta, yellow = spine.
**Ask:** Where would you use automatic organ volumes?
**Caveat:** Volumes come from this research run; the liver is only partly inside the chest CT's field of view.
**Transition:** PET/CT adds a second kind of image to the CT.
**Sources:** wasserthal2023totalseg; lidc2015data. Run: data/runs/segmentation.json.
-->

---
section: 5
layout: artifact
clicks: 3
tag: real-data
tagText: 'FDG-PET-CT-Lesions: real PET, CT and expert outline (DICOM)'
sources: [gatidis2022fdgpetct, boellaard2015petguideline]
---

::title::
# PET/CT: two kinds of image, one picture

::default::
<PetCtFusion />

<!--
**Time:** ~2 min
**Objective:** Show PET/CT as multimodal imaging: anatomy and function combined.
**Say:** A PET/CT scanner takes two images in one session. CT shows anatomy, in Hounsfield units. [click] PET shows where sugar is being used, in SUV: tumours are greedy. On its own, PET shows a hot spot but not exactly where it is. [click] Fused, the hot spot gets an address: next to the airways in the chest. Because both files share a frame of reference, they line up without any registration. [click] The cyan line is an expert's outline of the tumour, stored as a DICOM SEG: SUVmax 18, about 134 millilitres. On the right, the whole-body view: darker means more uptake; the brain, heart and bladder are normal, the chest is not.
**Example:** The PET says "something is burning", the CT says "on the third floor, room 12".
**Try / Notice:** Move the PET opacity slider; point at the image to read HU and SUV together.
**Ask:** Which multimodal model from Part 3 could use both images at once?
**Caveat:** Lung cancer patient from a public German collection (defaced release). The CT was taken for attenuation correction and anatomy; diagnostic decisions use the full clinical work-up.
**Transition:** Brain MRI adds several sequences per patient.
**Sources:** gatidis2022fdgpetct — PET, CT and lesion masks; boellaard2015petguideline — SUV.
-->

---
section: 5
layout: artifact
clicks: 4
tag: real-data
tagText: 'UPENN-GBM-00001, four registered sequences'
sources: [bakas2021upenndata, bakas2022upenn]
---

::title::
# Brain MRI: reading several sequences together

::default::
<AppCase illustrative :rows="[
  ['Scenario', 'A brain tumour must be measured before and after treatment'],
  ['AI does', 'Reads T1, T1 + contrast, T2 and FLAIR together'],
  ['Output', 'Outlines of the active tumour, dead tissue and swelling'],
  ['Benefit', 'The same measurement every time, for follow-up'],
  ['Limit', 'Needs every sequence, aligned; a missing or renamed series breaks it'],
]">
<div class="mri4">
<Img name="mri/t1.png" alt="T1" :h="150" :ar="0.75" caption="T1" />
<Img name="mri/t1_contrast.png" alt="T1 with contrast" :h="150" :ar="0.75" caption="T1 + contrast" />
<Img name="mri/t2.png" alt="T2" :h="150" :ar="0.75" caption="T2" />
<Img name="mri/flair.png" alt="FLAIR" :h="150" :ar="0.75" caption="FLAIR" />
</div>
</AppCase>

<style>
.mri4 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.mri4 .cap { font-size: 15px; }
</style>

<!--
**Time:** ~1.5 min
**Objective:** Connect multi-sequence MRI to multimodal fusion.
**Say:** A brain tumour is followed over months, so measurements must be consistent. [click] Tumour models read all four sequences at once. Each sequence is, in effect, a different modality. [click] Out come outlines of the active tumour, dead tissue and swelling. [click] The benefit is a consistent measurement at every visit. [click] The limit is the fusion problem from Part 2: if one sequence is missing, or the hospital names it differently, the model may fail or quietly produce nonsense.
**Example:** The four images here are one real patient, aligned in our notebook.
**Try / Notice:** The swelling is bright on T2 and FLAIR, but not on T1.
**Ask:** How consistent are series names on your scanners?
**Caveat:** We did not run a tumour segmentation model; the workflow is described, the images are real.
**Transition:** Pathology: images so large they must be cut up.
**Sources:** bakas2021upenndata; bakas2022upenn.
-->

---
section: 5
layout: artifact
clicks: 4
tag: actual
tagText: 'BiomedCLIP + small classifier on CRC-VAL-HE-7K'
run: biomedclip_fewshot_crc.json
sources: [kather2018crcdata, kather2019crc, zhang2025biomedclip]
---

::title::
# Pathology: classifying tissue, tile by tile

::default::
<AppCase illustrative :rows="[
  ['Scenario', 'A pathologist screens whole slides of a colon biopsy'],
  ['AI does', 'Cuts the slide into small tiles and labels each tissue type'],
  ['Output', 'A colour map of tumour, stroma, immune cells, normal tissue'],
  ['Benefit', 'With ten labelled tiles per class, 91% of our test tiles were right'],
  ['Limit', 'Stain and scanner differences between labs shift the results'],
]">
<Img name="gallery/pathology.png" alt="Four tissue tiles: tumour, stroma, lymphocytes, normal mucosa" :h="320" credit="CRC-VAL-HE-7K (Kather et al.) · CC BY 4.0" />
</AppCase>

<!--
**Time:** ~1.5 min
**Objective:** Apply image models to digital pathology.
**Say:** Pathology slides are scanned at microscope resolution, far too large to analyse in one piece. [click] So the slide is cut into many small tiles, and each tile is classified. [click] The output is a map of tissue types across the slide. [click] Our own result: with only ten labelled tiles per class on top of BiomedCLIP, 91% of 900 test tiles were classified correctly. [click] The limit: staining and scanners differ between laboratories, and tiles from a new lab can look different enough to confuse the model.
**Example:** The four tiles: tumour, stroma, lymphocytes and normal mucosa.
**Try / Notice:** None.
**Ask:** Would your lab's slides look like these?
**Caveat:** Our 91% used tiles from a single collection for training and testing, which flatters the result.
**Transition:** The retina: a photograph, not a scan.
**Sources:** kather2018crcdata; kather2019crc; zhang2025biomedclip. Run: data/runs/biomedclip_fewshot_crc.json.
-->

---
section: 5
layout: artifact
clicks: 4
tag: actual
tagText: 'BiomedCLIP zero-shot on 200 FIVES photographs'
run: biomedclip_fives.json
sources: [jin2022fives, zhang2025biomedclip]
---

::title::
# Retina: a photograph of the eye’s blood vessels

::default::
<AppCase illustrative :rows="[
  ['Scenario', 'Screening people with diabetes for eye damage in primary care'],
  ['AI does', 'Outlines vessels and looks for signs of disease'],
  ['Output', 'Vessel maps, and a grade for referral'],
  ['Benefit', 'Screening where eye specialists are scarce'],
  ['Limit', 'Our zero-shot test scored 27% on four diagnoses; guessing gets 25%'],
]">
<div class="eye2">
<Img name="apps/fundus_1_A.png" alt="Fundus photograph" :h="160" caption="Photograph" />
<Img name="apps/vessels_1_A.png" alt="Expert vessel outline" :h="160" caption="Expert vessel outline" />
</div>
<p class="credit-line">FIVES (Jin et al.) · CC BY 4.0</p>
</AppCase>

<style>
.eye2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.credit-line { font-size: 14px; color: var(--ink-3); margin: 6px 0 0; }
</style>

<!--
**Time:** ~1.5 min
**Objective:** Show a strong application area and a clear failure of zero-shot use.
**Say:** Diabetic eye disease can be caught with a simple photograph. [click] AI can outline the vessels, as this expert did by hand, and look for damage. [click] The output is a vessel map and a referral grade. [click] This is valuable where eye specialists are scarce. [click] But a general model is not enough. We asked BiomedCLIP, zero-shot, to tell apart four diagnoses in 200 photographs: 27% correct, where guessing scores 25%. It has not learned retinal disease from its training data.
**Example:** Dedicated retinal models trained on graded photographs are what is used in screening programmes.
**Try / Notice:** The vessel outline is the kind of label such models learn from.
**Ask:** What would you need to collect to train a model for your clinic?
**Caveat:** Four classes, 50 photographs each, one prompt wording; a different wording might do somewhat better.
**Transition:** Ultrasound: moving pictures.
**Sources:** jin2022fives; zhang2025biomedclip. Run: data/runs/biomedclip_fives.json.
-->

---
section: 5
layout: artifact
clicks: 4
tag: real-data
tagText: 'HC18 fetal ultrasound with expert outline'
sources: [vandenheuvel2018hc18]
---

::title::
# Ultrasound: measuring a baby’s head

::default::
<AppCase illustrative :rows="[
  ['Scenario', 'Routine pregnancy scans in a busy clinic'],
  ['AI does', 'Outlines the head and fits an ellipse'],
  ['Output', 'Head circumference in millimetres: 71.9 mm in this image'],
  ['Benefit', 'Faster, more consistent measurements, helpful for less experienced users'],
  ['Limit', 'Image quality depends on the operator; a poor view gives a poor measurement'],
]">
<Img name="apps/us_annotated.png" alt="Fetal head ultrasound with the expert's elliptical outline" :h="300" :ar="1.47" credit="HC18 (van den Heuvel et al.) · CC BY 4.0" />
</AppCase>

<!--
**Time:** ~1 min
**Objective:** Apply measurement AI to ultrasound.
**Say:** Ultrasound is live, cheap and everywhere, but it depends on the person holding the probe. [click] In this public challenge dataset, the task is to outline the baby's head and fit an ellipse. [click] The output is the head circumference in millimetres: 71.9 for this image, from the expert's outline. [click] Automating it makes measurements faster and more consistent. [click] But if the operator captures a poor view, no model can rescue the measurement.
**Example:** The yellow ellipse is the expert's outline from the dataset.
**Try / Notice:** None.
**Ask:** Where in your practice does the operator matter more than the software?
**Caveat:** We show the expert's annotation, not a model's output; the circumference comes from the dataset file.
**Transition:** Back to images and text: searching an archive by sentence.
**Sources:** vandenheuvel2018hc18 — images, outlines and circumference values.
-->

---
section: 5
layout: artifact
clicks: 2
tag: actual
tagText: 'BiomedCLIP search across IU chest X-rays'
run: biomedclip_retrieval.json
sources: [demnerfushman2016iu, zhang2025biomedclip]
---

::title::
# Search an archive with a sentence

::default::
<RetrievalDemo />

<!--
**Time:** ~1 min
**Objective:** Show image–text retrieval: finding similar cases by description.
**Say:** Because images and sentences share one space, we can search images with words. Here the query is "a chest X-ray showing an enlarged heart", run against the X-rays from our earlier test. [click] These are the five images whose fingerprints point most nearly the same way as the sentence. [click] And here is what their reports said: all five were reported with an enlarged heart.
**Example:** Teaching files: "show me five examples of cardiomegaly" from your own archive.
**Try / Notice:** The scores are close together; the ranking matters, not the values.
**Ask:** What would you search for in your own archive?
**Caveat:** Five results is a small sample, and an enlarged heart is a large, easy finding. Subtle findings retrieve far less well, as the six-pair test showed.
**Transition:** Finally, the hardest kind of multimodal data: the patient's history.
**Sources:** demnerfushman2016iu; zhang2025biomedclip. Run: data/runs/biomedclip_retrieval.json.
-->

---
section: 5
layout: split
sources: [huang2020fusion]
---

# Adding the history: promise and pitfalls

::left::

### Promise

- The context a clinician uses
- Earlier, more specific answers
- Change over time becomes visible

::right::

### Pitfalls

- Records missing or wrong
- Notes that leak the answer (“suspected cancer”)
- More personal data to protect

<!--
**Time:** ~1.5 min
**Objective:** Give a balanced view of combining imaging with clinical history.
**Say:** Adding the record is the most promising and the most difficult step. The promise: the same context a clinician uses, such as age, symptoms and an earlier scan, can make answers earlier and more specific, and can show change over time. The pitfalls: records are incomplete, as we saw in Part 2. Worse, notes can leak the answer: a note that says "suspected cancer, biopsy booked" lets a model look clever without reading the image at all. And every extra field is more personal data to protect.
**Example:** A model that learns "patients with a biopsy order have cancer" has learned the hospital's workflow, not the disease.
**Try / Notice:** None.
**Ask:** In your field, which part of the record would most help, and which is most likely to leak the answer?
**Caveat:** Reviews of image and health-record fusion report gains in many studies, but study designs vary widely.
**Transition:** Enough description. Let's run the models.
**Sources:** huang2020fusion — review of imaging and EHR fusion.
-->
