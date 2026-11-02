---
layout: opener
section: 6
---

# What happens when we run real models?

<p>Three workflows on our patient, run in the companion notebook. Every number is from that run.</p>

<!--
**Time:** ~0.5 min
**Objective:** Pose the question Part 6 answers, and switch to the notebook.
**Say:** Now we run things. I will switch between these slides and the notebook. Everything on the next slides is the real output of the notebook run on this machine; if the live run fails, the slides are the fallback.
**Transition:** Here is the plan.
**Sources:** None — section opener.
-->

---
section: 6
tag: actual
tagText: 'run times measured in the notebook'
run: notebook.json
sources: [lidc2015data, zhang2025biomedclip, wasserthal2023totalseg, ma2024medsam]
---

# Four workflows on real data

<DemoPlan />

<!--
**Time:** ~2 min
**Objective:** Set out the demos, the data, the models and real run times.
**Say:** Four workflows. The first three use our patient. A: open the DICOM CT and look at it properly; no AI yet. B: ask BiomedCLIP which description fits our patient's X-ray. C: outline the anatomy and the nodule with two segmentation models. D: open real DICOM files from six kinds of scanner, ending with a PET SUV calculation. The times are measured: BiomedCLIP takes about two hundredths of a second per image on this GPU and over a second on a laptop CPU.
**Example:** Participants can run A and B on a laptop; C is better on a GPU, and the notebook uses a fast mode on CPU.
**Try / Notice:** None.
**Ask:** None.
**Caveat:** TotalSegmentator's first run also downloads its weights, which takes longer.
**Steps:** Open notebook/multimodal-medical-imaging.ipynb; run the setup cell; confirm the "Running on …" line.
**Expected observations:** The setup cell prints the GPU name (or CPU).
**Likely failure modes:** Missing data folder (run download_data.py); no internet for first model download.
**Fallback:** Stay on the slides; they show the saved output of the same notebook.
**Sources:** lidc2015data; zhang2025biomedclip; wasserthal2023totalseg; ma2024medsam. Run: data/runs/notebook.json.
-->

---
section: 6
layout: artifact
clicks: 2
tag: actual
tagText: 'notebook cell A1, as run'
run: notebook.json
sources: [dicomstandard, lidc2015data]
---

::title::
# Demo A1: read the files, then sort them by position

::default::
<NotebookCell cell="A1" :lines="[4, 6, 7, 8, 11, 12, 13]" :steps="[[4, 6, 7, 8], [11, 12, 13]]" :out-lines="3" />

<!--
**Time:** ~2.5 min
**Objective:** Load a DICOM series correctly.
**Say:** First we read only the headers of all 133 files, not the pixels; that is fast. Then we print the first four file names with their instance number and their height in the body. [click] As we saw in Part 4, they are scrambled. So we sort by the height stored in each file, ImagePositionPatient. [click] Here is the real output: file 1 is instance 80 at minus 207.5 millimetres, and after sorting the series runs from minus 340 to minus 10.
**Example:** Rebuilding the dropped loaf of bread, slice by slice.
**Try / Notice:** The z values in the output jump around before sorting.
**Ask:** What would the volume look like if we sorted by file name?
**Caveat:** Some series are tilted or not axial; robust code projects positions onto the slice normal. SimpleITK does this for us in A3.
**Steps:** Run cell A1, then A1b to print key tags.
**Expected observations:** "133 slices, from z = -340.0 to -10.0 mm".
**Likely failure modes:** Wrong folder path (no files found); a non-image file in the folder.
**Fallback:** The output shown on the slide.
**Sources:** dicomstandard; lidc2015data.
-->

---
section: 6
layout: artifact
clicks: 2
tag: actual
tagText: 'notebook cell A2, figure as produced'
run: notebook.json
sources: [lidc2015data]
---

::title::
# Demo A2: units first, then a window

::default::
<NotebookCell cell="A2" :lines="[2, 3, 5, 6, 7]" :steps="[[2, 3], [5, 6, 7]]" figure />

<!--
**Time:** ~1.5 min
**Objective:** Convert to Hounsfield units and apply windows in code; distinguish visualisation from inference.
**Say:** Two lines turn the stack of files into a volume in Hounsfield units: read the pixels, then multiply by the slope and add the intercept from the header. [click] And a window is just three lines: choose the lowest value to show, scale, and clip. [click] Here is the figure the notebook drew: lung, soft tissue and bone windows of the same slice. Nothing so far is AI. This is visualisation: it changes how we see, not what the data say.
**Example:** The sliders from Part 4, now as code.
**Try / Notice:** The nodule is visible in the lung and soft-tissue windows.
**Ask:** Which window would you give an AI model, and why?
**Caveat:** Notebook cell A3 also shows coronal and sagittal views with the correct spacing; not shown here for time.
**Steps:** Run A2, then A3 for the three planes, then A4 for the X-ray and MRI headers.
**Expected observations:** Three greyscale panels; "HU range on this slice: -2048 to 3071".
**Likely failure modes:** Out of memory on very small machines (the volume is about 140 MB as floats).
**Fallback:** The figure on the slide.
**Sources:** lidc2015data.
-->

---
section: 6
layout: artifact
clicks: 2
tag: actual
tagText: 'notebook cell B1, as run'
run: notebook.json
sources: [zhang2025biomedclip]
---

::title::
# Demo B1: the model never sees DICOM

::default::
<NotebookCell cell="B1" :lines="[5, 6, 7, 10, 11, 12, 13]" :steps="[[5, 6, 7], [10, 11, 12, 13]]" :out-lines="2" />

<!--
**Time:** ~1.5 min
**Objective:** Show the conversion from DICOM to a model input in code.
**Say:** Three lines load BiomedCLIP and its own preprocessing, downloaded from its public page. [click] BiomedCLIP was trained on ordinary pictures, so we must convert our 14-bit DICOM X-ray ourselves: choose a window that keeps 99% of the values, make an 8-bit image, then let the model's preprocessing resize it to 224 by 224 and normalise it. The output confirms the shape: one image, three colour channels, 224 by 224.
**Example:** The preparation pipeline from slide 40, in four lines of code.
**Try / Notice:** Line 11: the window is our choice, and it affects every score that follows.
**Ask:** What else could we have chosen for the window?
**Caveat:** The model expects colour images; the grey X-ray is copied into three identical channels.
**Steps:** Run B1.
**Expected observations:** "Model input: (1, 3, 224, 224)".
**Likely failure modes:** First run needs internet to download about 800 MB of weights; offline machines need the weights copied in advance.
**Fallback:** The output on the slide.
**Sources:** zhang2025biomedclip.
-->

---
section: 6
layout: artifact
clicks: 2
tag: actual
tagText: 'BiomedCLIP fingerprints, scores recomputed live'
run: biomedclip_ranking.json
sources: [zhang2025biomedclip, demnerfushman2016iu, lidc2015data]
---

::title::
# Demo B2: which description fits best?

::default::
<RankingViewer />

<!--
**Time:** ~3 min
**Objective:** Run image–text matching on real X-rays and read the ranking.
**Say:** For each X-ray, the model scores every description by cosine similarity. [click] The bars are real scores, recomputed in this page from the saved fingerprints. [click] Sorted, they become a ranking. For our patient, "a mass in the lung" comes first, but only just ahead of "normal". Switch to the IU X-rays: the normal one ranks "normal" first and the enlarged heart ranks "enlarged heart" first, but the effusions and the small pneumothorax are both called "normal".
**Example:** Remove a description with the × and watch the ranking re-sort: the model can only choose among the options we give it.
**Try / Notice:** Click the image buttons to switch X-rays; remove "a mass in the lung" for our patient and see what wins.
**Ask:** Predict, then reveal: which description will rank first for our patient?
**Caveat:** These scores come from the slides' preparation of the X-ray (a masked PNG); the notebook's DICOM path gives slightly different numbers, as the next slide shows. IU images are shown unmodified.
**Steps:** Run B2 in the notebook; compare with the bars here.
**Expected observations:** Top for our patient: "a chest X-ray showing a mass in the lung" (0.405 in the notebook).
**Likely failure modes:** Tokenizer download needs internet on first run.
**Fallback:** This interactive slide.
**Sources:** zhang2025biomedclip; demnerfushman2016iu; lidc2015data. Run: data/runs/biomedclip_ranking.json.
-->

---
section: 6
layout: artifact
clicks: 2
tag: actual
tagText: 'from the notebook run and the slides’ run'
run: notebook.json
sources: [zhang2025biomedclip, demnerfushman2016iu]
---

::title::
# Demo B3: three ways a score misleads

::default::
<FailureCases />

<!--
**Time:** ~2.5 min
**Objective:** Show failure and ambiguity in real outputs.
**Say:** First, our patient. The top two descriptions differ by four thousandths. That is a coin toss, even though the top one happens to be right. [click] Second, an X-ray whose report describes fluid around both lungs. The model's top choice is "normal": confidently wrong. [click] Third, the same image prepared two ways, a PNG for the slides and the DICOM in the notebook, gives two different scores. Preparation is part of the model.
**Example:** Three questions to ask of any AI score: how big is the gap, what does the report say, and how was the image prepared?
**Try / Notice:** None.
**Ask:** Why did the model miss the effusions?
**Caveat:** These are three cases, not a performance estimate.
**Steps:** Run B3 (softmax) and B4 (the effusion X-ray) in the notebook.
**Expected observations:** B4's top line is "a normal chest X-ray".
**Likely failure modes:** B4 needs the optional IU download.
**Fallback:** This slide.
**Sources:** zhang2025biomedclip; demnerfushman2016iu. Runs: data/runs/notebook.json, biomedclip_ranking.json.
-->

---
section: 6
layout: artifact
clicks: 3
tag: actual
tagText: 'TotalSegmentator labels for our patient’s CT'
run: segmentation.json
sources: [wasserthal2023totalseg, lidc2015data]
---

::title::
# Demo C1: outline the anatomy

::default::
<SegOverlay />

<!--
**Time:** ~2.5 min
**Objective:** Run whole-CT segmentation and read its output.
**Say:** TotalSegmentator reads the DICOM folder directly and outlines 117 structures. On this GPU it takes about a minute. [click] The lungs: 3.7 litres. [click] The heart, aorta and airway. [click] The spine, ribs and the top of the liver. Each colour is a real outline from the run, and every volume on the right was measured from it.
**Example:** Scroll through the slices: the outlines follow the anatomy up and down the chest.
**Try / Notice:** Use the slice slider, switch structures on and off, and change the opacity.
**Ask:** Which of these volumes would be useful in your work?
**Caveat:** Shown on a 2.5 mm grid for speed; volumes were measured at full resolution. Research software, not a medical device.
**Steps:** Run C1. If the result file exists, the run is skipped and the saved output is loaded.
**Expected observations:** Volumes printed for four structures; an overlay figure.
**Likely failure modes:** First run downloads weights; CPU runs take several minutes even in fast mode.
**Fallback:** This slide; the result file is included.
**Sources:** wasserthal2023totalseg; lidc2015data. Run: data/runs/segmentation.json.
-->

---
section: 6
layout: artifact
clicks: 2
tag: actual
tagText: 'radiologists’ outlines, MedSAM and TotalSegmentator'
run: segmentation.json
sources: [fedorov2018lidcdicom, ma2024medsam, wasserthal2023totalseg]
---

::title::
# Demo C2: check the outlines against people

::default::
<SegChecks />

<!--
**Time:** ~2.5 min
**Objective:** Validate segmentation output against human references, and find where it fails.
**Say:** How good is good? First, the four radiologists against each other over the whole nodule: Dice between 0.84 and 0.90. That is our ceiling. [click] MedSAM, given a box, scores about 0.75 to 0.77 against each of them on the nodule slice, where the readers agree with each other at 0.91 or more. MedSAM drew the nodule too small. [click] And TotalSegmentator does not mark the nodule at all: 99.9% of it sits inside its "lung" label. Neither model is wrong for what it was built to do, but neither replaces the reader.
**Example:** Always compare a model with the spread between experts, not with perfection.
**Try / Notice:** Darker cells = more agreement.
**Ask:** What Dice would you accept before using a model's outline for treatment planning?
**Caveat:** One nodule, one patient; this shows how to check, not how good the models are in general.
**Steps:** Run C2 and C3.
**Expected observations:** "Nodule voxels inside the TotalSegmentator lung label: 99.9%"; MedSAM Dice 0.75–0.77.
**Likely failure modes:** MedSAM download needs internet; GPU memory is enough on most laptops' CPUs, just slower.
**Fallback:** This slide.
**Sources:** fedorov2018lidcdicom; ma2024medsam; wasserthal2023totalseg. Run: data/runs/segmentation.json.
-->

---
section: 6
layout: artifact
clicks: 2
tag: actual
tagText: 'notebook cell D3, as run'
run: notebook.json
sources: [gatidis2022fdgpetct, dicomstandard]
---

::title::
# Demo D: real DICOM from six scanners

::default::
<NotebookCell cell="D3" :lines="[3, 4, 5, 6, 7]" :steps="[[3, 4, 5], [6, 7]]" :out-lines="2" />

<!--
**Time:** ~2 min
**Objective:** Read the sample pack in code, ending with the SUV calculation.
**Say:** Workflow D in the notebook opens every file in the sample pack and prints the tags that matter for each kind of scanner: units for CT and PET, frames for ultrasound, laterality for the mammogram. This cell is the PET one. [click] It reads the timing and dose from the file. [click] And turns becquerels into SUV. The output matches the slide we saw in Part 4, because it is the same file.
**Example:** Four lines of arithmetic, but every input comes from the DICOM header.
**Try / Notice:** None.
**Ask:** Which tag would you double-check first if an SUV looked wrong?
**Caveat:** The notebook also draws the PET on the CT in millimetres (cell D4).
**Steps:** Run D1 (all files), D2 (mammogram and ultrasound), D3 (SUV), D4 (fusion figure).
**Expected observations:** D3 prints 300 MBq, 60.1 min, 205.3 MBq left, and a maximum SUV of 14.2 on this slice (18.1 over the whole tumour in 3D).
**Likely failure modes:** Running from another folder: the pack is at ../public/dicom/ relative to the notebook.
**Fallback:** This slide.
**Sources:** gatidis2022fdgpetct; dicomstandard.
-->

---
section: 6
layout: artifact
clicks: 3
tag: actual
tagText: 'values from the notebook run'
run: notebook.json
sources: [radford2021clip, zhang2025biomedclip]
---

::title::
# A score is not a diagnosis

::default::
<OutputLadder />

<!--
**Time:** ~2.5 min
**Objective:** Separate scores, probabilities, findings and diagnoses.
**Say:** Let's climb from what the model gave us to what a patient needs. The bottom rung: a similarity score, 0.405. It only ranks options for this one image. [click] Turn the scores into "probabilities" with softmax, as many tools do, and the top description gets 0.42, even though it beat the next one by four thousandths. It looks like confidence; it is not calibrated. [click] A finding needs a threshold tested on local data, with known sensitivity and specificity. [click] And a diagnosis needs a clinician, all the evidence, and often a biopsy. Our patient's nodule was rated highly suspicious by radiologists; no model output here changes that.
**Example:** A weather app's "70% chance of rain" has been checked against years of real rain. These numbers have not.
**Try / Notice:** None.
**Ask:** Which rung do vendors' marketing materials usually show?
**Caveat:** Calibration can be measured and improved, but that is a separate study.
**Steps:** Notebook cell B3 shows the softmax calculation.
**Expected observations:** "After softmax (x85): 0.42 vs 0.29".
**Likely failure modes:** None.
**Fallback:** This slide.
**Sources:** radford2021clip — softmax over cosine similarities with a learned temperature; zhang2025biomedclip. Run: data/runs/notebook.json.
-->
