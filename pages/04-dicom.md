---
layout: opener
section: 4
---

# How are medical images stored?

<p>DICOM: the hospital format that keeps pixels, units, position and the patient together.</p>

<!--
**Time:** ~0.5 min
**Objective:** Pose the question Part 4 answers.
**Say:** Every model we have seen needs images as input. In a hospital, those images live in DICOM files. Understanding DICOM is what separates a demo that works on a website from one that works on real data.
**Transition:** What is DICOM, and why not just use JPEG?
**Sources:** None — section opener.
-->

---
section: 4
layout: artifact
clicks: 2
tag: real-data
tagText: 'one CT file of LIDC-IDRI-0001'
sources: [dicomstandard, lidc2015data]
---

::title::
# A DICOM file carries the facts, not just the picture

::default::
<DicomVsPng />

<!--
**Time:** ~2 min
**Objective:** Explain why medicine uses DICOM rather than ordinary image files.
**Say:** On the left, a slice saved as an ordinary picture: brightness from 0 to 255, no units, no size, no position. [click] On the right, the same slice as it really arrived: a DICOM file. Alongside the pixels it carries tags: who the patient is, how the scan was made, where the slice sits in the body, and how to turn the stored numbers into real units. Our file has 89 tags. [click] The pixel values are in Hounsfield units, and each pixel is 0.7 millimetres wide. The pixels take 99.6% of the file; the tags are tiny but essential.
**Example:** A photograph versus a photograph with its full lab notebook stapled on.
**Try / Notice:** None.
**Ask:** What could go wrong if a model is trained on JPEG copies of DICOM images?
**Caveat:** DICOM (Digital Imaging and Communications in Medicine) is also a network protocol for sending images between machines; we focus on the file.
**Transition:** One file is one image. How are files organised?
**Sources:** dicomstandard — the standard; lidc2015data — the file.
-->

---
section: 4
layout: artifact
clicks: 3
tag: real-data
tagText: 'LIDC-IDRI-0001 as stored at TCIA'
sources: [dicomstandard, lidc2015data, fedorov2018lidcdicom, clark2013tcia]
---

::title::
# Patient, study, series, file

::default::
<DicomHierarchy />

<!--
**Time:** ~2 min
**Objective:** Explain the DICOM hierarchy with a real patient.
**Say:** DICOM organises images in four levels. At the top, the patient. [click] A study is one visit to the scanner: our patient has two, a chest CT and a chest X-ray. [click] A series is one set of images made together. The CT study holds the CT images, plus four outline series and four rating series added later by four radiologists. [click] And at the bottom, instances: one file each. The CT series is 133 files, one per slice.
**Example:** Patient = a folder per person; study = one appointment; series = one stack; instance = one page.
**Try / Notice:** Click any box to see its details on the right.
**Ask:** Why might a model need to know which series to use?
**Caveat:** Study dates in this dataset are shifted to 1 January 2000 as part of de-identification. Long identifiers (UIDs) are shortened for display.
**Transition:** What is inside one of those files?
**Sources:** dicomstandard; lidc2015data; fedorov2018lidcdicom — the outline and rating series; clark2013tcia — TCIA, the archive.
-->

---
section: 4
layout: artifact
clicks: 3
tag: real-data
tagText: 'tags read from one CT file of LIDC-IDRI-0001'
sources: [dicomstandard, lidc2015data]
---

::title::
# Inside a file: who, how, where, and how to read it

::default::
<DicomTags />

<!--
**Time:** ~2 min
**Objective:** Show real metadata and its privacy implications.
**Say:** These are real tags from our patient's file, in four groups. The first group is about who: name, birth date and accession number are empty, the patient ID is a code, and the date is shifted. That was done by the archive before release; in a hospital file, these fields hold real identities. [click] How it was acquired: GE scanner, 120 kV, 2.5 mm slices. [click] Where in space: 512 by 512 pixels, each 0.70 mm, and the exact position of this slice. [click] And how to read the pixels: 16 bits, and a slope and intercept, which we need on the next slide.
**Example:** The privacy group is why you must never email a hospital DICOM file without de-identifying it.
**Try / Notice:** Click the group buttons to move between them.
**Ask:** Which of these would you remove before sharing data?
**Caveat:** De-identification is more than blanking tags: identities can also hide in burned-in text, in private tags, or in a face reconstructed from a head CT.
**Transition:** Those last two tags turn stored numbers into real units.
**Sources:** dicomstandard; lidc2015data.
-->

---
section: 4
layout: artifact
clicks: 2
tag: real-data
tagText: 'stored values of our patient’s CT and X-ray'
sources: [dicomstandard, lidc2015data]
---

::title::
# Stored numbers become real units

::default::
<StoredVsDisplayed />

<!--
**Time:** ~1.5 min
**Objective:** Distinguish stored values, physical units and displayed grey levels.
**Say:** Point anywhere on the scan to read the number stored in the file. At the centre of the nodule it is 1,107. [click] That stored number is not yet meaningful. The file tells us to multiply by 1 and subtract 1,024, which gives Hounsfield units: 83 here, which is soft tissue. Air is around −1000, water 0, bone several hundred. [click] And metadata can be wrong. Our X-ray file carries window settings that look copied from a CT. Apply them as written and the image turns white.
**Example:** Like a thermometer reading that needs a conversion formula printed on its side.
**Try / Notice:** Move the pointer over air, lung, the nodule and bone; watch the units change.
**Ask:** If a model is fed stored values from one scanner and HU from another, what happens?
**Caveat:** For CT the conversion gives physical units; MRI values have no standard units and vary between scanners.
**Transition:** So which Hounsfield units should be black, and which white? That is windowing.
**Sources:** dicomstandard — rescale slope and intercept, window tags; lidc2015data.
-->

---
section: 4
layout: artifact
clicks: 3
tag: real-data
tagText: 'Hounsfield units of our patient’s CT slice'
sources: [lidc2015data]
---

::title::
# Windowing decides what you can see

::default::
<WindowingSlider />

<!--
**Time:** ~2.5 min
**Objective:** Explain window level and width with real HU data.
**Say:** A CT slice holds values from about −1000 to over 1,000 HU, but a screen shows only 256 greys. The window picks which part of the range to spread across those greys. Showing everything, the lungs and soft tissue look flat. [click] The lung window, level −600, width 1,500: now the lung detail and the nodule's spiky edges appear. [click] Soft tissue, level 40, width 400: the heart, vessels and the nodule's solid core. [click] Bone: the spine and ribs. Same numbers in the file every time; only the display changed. A model must be given the right window, or the full range.
**Example:** Like adjusting brightness and contrast, but in real units.
**Try / Notice:** Drag Level and Width; watch the blue band on the histogram move over the tissue labels.
**Ask:** Predict, then reveal: which window will show the lung nodule best?
**Caveat:** Preset values vary between institutions; these are common choices.
**Transition:** One slice is one picture. CT is a whole volume.
**Sources:** lidc2015data — the HU values.
-->

---
section: 4
layout: artifact
clicks: 2
tag: real-data
tagText: 'LIDC-IDRI-0001 CT volume, resampled to 2.5 mm'
sources: [dicomstandard, lidc2015data]
---

::title::
# Slices stack into a volume, in the right order

::default::
<VolumeExplorer />

<!--
**Time:** ~2 min
**Objective:** Explain slice ordering and 3D geometry; show multiplanar views.
**Say:** A CT is 133 slices, 2.5 mm apart. [click] But look at the file names: file 1 is slice 80, file 2 is slice 52. File names do not tell you where a slice is. Software must sort by the position stored in each file. Get this wrong and the body is scrambled. [click] Once stacked correctly, the volume can be cut in any direction: across, as scanned; from the front, coronal; and from the side, sagittal. The yellow lines show where the three cuts meet, on the nodule.
**Example:** A sliced loaf of bread dropped on the floor: you need the slice positions to rebuild it.
**Try / Notice:** Drag the three sliders, or click the axial view to move the crosshair.
**Ask:** Why do coronal views look blurrier than axial ones here?
**Caveat:** For display, the volume was resampled to 2.5 mm cubes in the notebook; the original pixels are 0.70 mm in-plane. The orientation tags also matter: not every scan is axial.
**Transition:** MRI adds another twist: many kinds of image of the same slice.
**Sources:** dicomstandard — ImagePositionPatient and orientation; lidc2015data.
-->

---
section: 4
layout: artifact
clicks: 3
tag: real-data
tagText: 'UPENN-GBM-00001, four sequences registered'
sources: [bakas2021upenndata, bakas2022upenn]
---

::title::
# MRI sequences show different tissue properties

::default::
<MriSequences />

<!--
**Time:** ~2 min
**Objective:** Explain why MRI comes as several sequences and why that matters for AI.
**Say:** This is a different patient: a brain tumour from another public collection. MRI does not take one picture; it takes several, each tuned to a different tissue property. T1 shows anatomy. [click] T1 after contrast injection: leaky vessels and the tumour's edge light up. [click] T2: fluid is bright, so the swelling around the tumour shows. [click] FLAIR: like T2, but normal fluid is made dark, so the swelling stands out. A model that expects FLAIR but is given T2 is looking at a different picture.
**Example:** Like photographing the same street in daylight, at night and in infrared.
**Try / Notice:** Use the slider to wipe between the current sequence and the previous one.
**Ask:** If a hospital names its series differently, how would software know which is FLAIR?
**Caveat:** The four series were registered (aligned) to the T1 series in our notebook, and the slice was chosen by eye through the lesion. Diffusion-weighted imaging (DWI) is another common sequence, not shown.
**Transition:** Finally, how does a DICOM image become a model's input?
**Sources:** bakas2021upenndata — the data; bakas2022upenn — the collection.
-->

---
section: 4
layout: artifact
clicks: 3
tag: real-data
tagText: 'our patient’s X-ray at each preparation step'
sources: [zhang2025biomedclip, lidc2015data]
---

::title::
# Every preparation step keeps something and loses something

::default::
<PrepPipeline />

<!--
**Time:** ~1.5 min
**Objective:** Show the preparation pipeline from DICOM to model input, and what is lost.
**Say:** Here is exactly what happened to our patient's X-ray before BiomedCLIP saw it. One: the DICOM pixels, 14-bit, 2022 pixels square. [click] Two: windowed to 8 bits, the 256 grey levels a picture can hold. [click] Three: resized to 224 by 224, the model's fixed input. That throws away almost 99% of the pixels, and the size in millimetres. [click] Four: normalised to the range of numbers the model was trained on. Each step is a choice, and each loses something. Small findings can vanish at step three.
**Example:** Photocopying a photocopy: each copy is fine for some purposes and useless for others.
**Try / Notice:** The red "lost" line under each step.
**Ask:** Which step worries you most for a 5 mm nodule?
**Caveat:** Different models need different preparation; always follow the model's documented preprocessing. The notebook does these steps in code.
**Transition:** With images ready, where are these models being applied?
**Sources:** zhang2025biomedclip — the model's input size and normalisation; lidc2015data — the X-ray.
-->
