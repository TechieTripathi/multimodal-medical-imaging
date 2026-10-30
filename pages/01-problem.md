---
layout: cover
section: 1
tag: real-data
tagText: 'LIDC-IDRI-0001, TCIA · CC BY 3.0'
sources: [lidc2015data]
---

<div class="title-top">

# Multimodal AI for medical imaging

<p class="sub">How AI connects images, words and patient data, and how to read what it tells you</p>

</div>

<TitleVisual />

<style>
.title-top h1 { font-size: 46px; max-width: 18ch; }
.title-top .sub { max-width: 34ch; }
</style>

<!--
**Time:** ~1 min
**Objective:** Set expectations: a practical, honest two hours on how AI combines images with text and patient data.
**Say:** Welcome. Over the next two hours we will look at how AI systems can connect a medical image with the words a clinician writes about it and with the rest of what we know about a patient. We will follow one real, anonymised patient from a public research archive: their chest X-ray, their CT scan, and what four radiologists wrote about them. Everything you see labelled as real data or as a real model output was actually run for this session. You do not need any background in AI or programming.
**Example:** The three pieces at the bottom: an X-ray, one CT slice, and two phrases from a radiologist's structured report. By the end of the session you will know how a model can turn each of these into numbers and compare them.
**Try / Notice:** Nothing to click yet. Point to the three pieces of evidence.
**Ask:** Quick show of hands: who here works mostly with images, who mostly with text or data, and who with both?
**Caveat:** The patient is from LIDC-IDRI, a de-identified public research collection; no clinical history is available for them.
**Transition:** Let's start with the problem every clinician already solves.
**Sources:** lidc2015data — the patient's images and annotations.
-->

---
layout: opener
section: 1
---

# Why would a computer need more than the image?

<p>Clinicians never read a scan on its own. Should AI?</p>

<!--
**Time:** ~0.5 min
**Objective:** Pose the question Part 1 answers.
**Say:** Part one is about the problem. A radiologist looking at a scan always has more than the scan: a request form, a history, earlier images. We will see what an image alone can and cannot tell us, and what "multimodal" means.
**Transition:** Here is our patient.
**Sources:** None — section opener.
-->

---
section: 1
layout: artifact
clicks: 3
tag: real-data
tagText: 'LIDC-IDRI-0001 and its radiologist reports, TCIA · CC BY 3.0'
sources: [lidc2015data, fedorov2018lidcdicom]
---

::title::
# One patient, several kinds of evidence

::default::
<EvidenceCase />

<!--
**Time:** ~2 min
**Objective:** Show that even one patient arrives as several kinds of evidence, each answering different questions.
**Say:** This is a real, anonymised patient from a public archive. First, a chest X-ray. [click] Then a CT scan: 133 thin slices; this is the one through the widest part of a lump in the left lung, circled. [click] Four radiologists independently outlined the lump and filled in a structured form. This one wrote: solid nodule, about 32 millimetres, spiky edge, and rated it 5 out of 5 for suspicion of cancer. [click] And what is missing: the history. Symptoms, smoking, earlier scans, blood tests. A clinician would never decide without them, and the public data does not include them.
**Example:** Think of a detective with a photograph, a witness statement and a background file. Each one answers different questions.
**Try / Notice:** The yellow circle on the CT slice; the dashed card on the right is deliberately empty.
**Ask:** Before I reveal the rest: what would you want to see first: the image, the report, or the history?
**Caveat:** The report is a structured rating form from a research study, not a free-text clinical report. The 32 mm diameter was calculated from the reader's outline.
**Transition:** The modality here is CT, but medicine produces many kinds of images.
**Sources:** lidc2015data — images; fedorov2018lidcdicom — the readers' outlines and ratings in DICOM form.
-->

---
section: 1
layout: artifact
clicks: 6
tag: real-data
tagText: 'six public datasets, credits on click'
sources: [lidc2015data, bakas2021upenndata, vandenheuvel2018hc18, kather2018crcdata, jin2022fives]
---

::title::
# Medicine makes many kinds of images

::default::
<ModalityGallery />

<!--
**Time:** ~2 min
**Objective:** Recognise the main imaging modalities and that they are stored differently.
**Say:** X-ray: a shadow picture, cheap and fast. [click] CT: many X-ray slices stacked into a 3D volume, which is our patient. [click] MRI uses magnetism instead of radiation and can show the same tissue with different contrasts. [click] Ultrasound uses sound echoes and is live; this one is a baby's head. [click] Pathology: thin slices of tissue, stained and photographed under a microscope. [click] And the retina, photographed through the pupil. [click] Notice the stamps: radiology images are usually stored as DICOM, the hospital standard we will open up in Part 4. Microscope slides and eye photos often are not.
**Example:** All six images in this gallery come from public, openly licensed research datasets, and you will see several of them again later.
**Try / Notice:** Click any tile to enlarge it and see its source and licence.
**Ask:** Which of these do you work with?
**Caveat:** "Usually DICOM" is a generalisation; ultrasound clips are often exported as video, and whole-slide pathology increasingly has a DICOM option.
**Transition:** Whatever the modality, a clinician never looks at the image alone.
**Sources:** lidc2015data — X-ray and CT; bakas2021upenndata — MRI; vandenheuvel2018hc18 — ultrasound; kather2018crcdata — pathology; jin2022fives — retina.
-->

---
section: 1
layout: artifact
clicks: 3
tag: teaching
---

::title::
# Clinicians join images, words and the patient

::default::
<ClinicianFlow />

<!--
**Time:** ~1.5 min
**Objective:** Make explicit the integration clinicians already do in their heads.
**Say:** A radiologist reading a scan has three streams of information. The images: what is there, where, and how big. [click] The words: the referral letter that says why the scan was done, previous reports, notes. [click] And the patient: history, symptoms, blood tests, earlier scans. [click] All three flow into one judgement: is this a follow-up scan in three months, a biopsy, or surgery?
**Example:** "Cough for three months, ex-smoker" on a referral changes how you read a lung nodule.
**Try / Notice:** Each lane lights up in turn; then they join.
**Ask:** In your own field, which stream do people most often forget to use?
**Caveat:** This is a simplified picture of clinical reasoning, not a description of any guideline.
**Transition:** So what happens when an AI system sees only the first lane?
**Sources:** None — conceptual.
-->

---
section: 1
layout: artifact
clicks: 4
tag: real-data
tagText: 'LIDC-IDRI-0001, TCIA · CC BY 3.0'
sources: [lidc2015data]
---

::title::
# An image alone answers only some questions

::default::
<ImageOnlyLimits />

<!--
**Time:** ~1.5 min
**Objective:** Show concretely what image-only AI can and cannot know.
**Say:** An image-only system can be very good at the first kind of question: where is the abnormality and how big is it. Here, a lump about three centimetres across. But look at what the pixels cannot tell us. [click] Is it new, or has it been there unchanged for years? [click] Does the patient have symptoms? [click] Smoking or other risks? [click] And why was the scan done in the first place? Each of these changes what the finding means.
**Example:** A 3 cm nodule unchanged for five years and a 3 cm nodule that was not there last year are very different stories, yet the single image looks the same.
**Try / Notice:** The box marks the nodule; the list grows with each click.
**Ask:** Which of these questions matters most in your speciality?
**Caveat:** Image-only models can still be very useful, for example for detection and measurement; the point is what they cannot know.
**Transition:** Multimodal AI is an attempt to give the model the other lanes too.
**Sources:** lidc2015data — the CT slice.
-->

---
section: 1
layout: artifact
clicks: 3
tag: teaching
sub: 'AI that learns from more than one kind of data at once'
---

::title::
# What is multimodal AI?

::default::
<ModalityInputs />

<!--
**Time:** ~1.5 min
**Objective:** Define multimodal AI in one plain sentence.
**Say:** "Modality" here just means a kind of data. Images are one modality. [click] Text, such as reports and notes, is another. [click] Numbers, such as lab results, vital signs and history, are a third. [click] A multimodal model takes in more than one of these and, crucially, learns how they relate: which words go with which image patterns. What comes out might be an answer, a score, or an outline on the image.
**Example:** A chest X-ray plus the words "fever and cough" plus a high white-cell count points somewhere different from the X-ray alone.
**Try / Notice:** The three inputs join into one model.
**Ask:** None.
**Caveat:** The values on the "numbers" chip are examples of the kind of data, not this patient's.
**Transition:** Let's compare the two approaches on our patient.
**Sources:** None — conceptual.
-->

---
section: 1
layout: artifact
clicks: 2
tag: real-data
tagText: 'LIDC-IDRI-0001 and its four radiologist reports'
sources: [lidc2015data, fedorov2018lidcdicom]
---

::title::
# Each kind of evidence adds a different answer

::default::
<UniMultiCompare />

<!--
**Time:** ~1.5 min
**Objective:** Feel the difference between image-only and image-plus-context reasoning on a real case.
**Say:** On the left, only the image. What can we say? A round lump, three centimetres, spiky edge. [click] Add the report text: three of the four radiologists rated it highly suspicious for cancer. That is information a model can learn to connect with how the image looks. [click] Add the history, and a new kind of question becomes answerable: has it grown? That needs an earlier scan, which is exactly the kind of data multimodal systems try to bring in.
**Example:** This is what the rest of the session is about: how a model can connect the left side with the right side.
**Try / Notice:** Toggle the evidence on and off with the buttons to show what each piece contributes.
**Ask:** Predict, then reveal: which answer would you trust more, image only or image plus report? Why?
**Caveat:** The sentences are written by us to summarise each source; they are not the output of an AI model. The ratings come from the real reports.
**Transition:** Here is the plan for the rest of the session.
**Sources:** lidc2015data — CT; fedorov2018lidcdicom — the four readers' ratings.
-->

---
section: 1
---

# Seven questions in two hours

<Roadmap />

<!--
**Time:** ~0.5 min
**Objective:** Give the audience the map.
**Say:** We will answer seven questions in order. Why combine images with words and data, which we just did. How a computer reads an X-ray and a report. How models are trained and tested. How medical images are actually stored, which is DICOM. Where this is used today. Then we run real models on real data. And finally what can go wrong and who is responsible.
**Example:** The times on the right are a promise: we will stop for questions at the end.
**Try / Notice:** None.
**Ask:** None.
**Caveat:** None.
**Transition:** Let's start with how a computer reads an image.
**Sources:** None — roadmap.
-->
