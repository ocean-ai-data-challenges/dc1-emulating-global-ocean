# DC 1: Emulation of Global Ocean Reanalyses

Data Challenge 1 (DC1) is an open benchmark for **emulating global ocean reanalyses at
the surface level**. Participants build neural emulators that reproduce the time evolution
of the global 2-D ocean state vector (latitude × longitude), given perfectly known initial
conditions and time-varying forcings.

Unlike [DC2](https://github.com/ppr-ocean-ia/dc2-forecasting-global-ocean-dynamics) which
evaluates forecasts across the full 3-D water column (latitude, longitude, depth), **DC1
focuses exclusively on surface-level (2-D) evaluation**. All predicted variables are
assessed at the ocean surface only.

DC1 is part of the [PPR Océan & Climat](https://www.ocean-climat.fr/) (*Projet Prioritaire
de Recherche*), a national research programme launched by the French government and managed
by CNRS and Ifremer.

```{toctree}
:maxdepth: 2
:caption: DC1 Challenge

content/task.md
content/data.md
content/metrics.md
content/leaderboard.md
content/submissions.md
content/references.md
content/api
```

```{toctree}
:maxdepth: 2
:caption: dc-tools Library

content/dctools_api
```
