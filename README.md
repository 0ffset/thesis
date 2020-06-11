# Data-Driven Procedural Audio: Procedural Engine Sounds Using Neural Audio Synthesis

## Introduction

This repository holds the source code for my M.Sc. thesis work on procedural engine sounds using neural audio synthesis. The implementation uses TensorFlow and builds on [DDSP](https://github.com/magenta/ddsp). The method works by training models to reconstruct audio examples of recorded engine sounds from fundamental frequency (f0) signals corresponding to the engine speed (RPM). My report will be publicly accessibly at the DiVA portal (*The report is still being reviewed and the link will be added as soon as the report has been published*) and online supplementary material is available at [here](https://0ffset.github.io/thesis/).

## Modules

The code is split into four modules:

1. `data`: Code related to data processing. Contains scripts for recording on-board diagnostics (OBD) data, processing audio and OBD recordings, and preparing `.tfrecord` files.
1. `docs`: Contains the online supplementary material of the report.
1. `evaluation`: Code for evaluating datasets, training processes and trained models.
1. `models`: Components of the models, including decoders, synthesizers and losses.
