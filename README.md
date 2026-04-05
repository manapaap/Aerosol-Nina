# Aerosol-Nina

Examining the role of the 2019–2020 Australian wildfire aerosol forcing on the subsequent La Niña event through an observational lens.

---

## Table of Contents

1. [Project overview](#project-overview)
2. [Repository structure](#repository-structure)
3. [Getting started](#getting-started)
4. [How to contribute](#how-to-contribute)
5. [GitHub basics for scientists](#github-basics-for-scientists)

---

## Project overview

The 2019–2020 Australian wildfires injected an unprecedented amount of aerosol into the Southern Hemisphere stratosphere. This project investigates whether that forcing played a role in initiating or intensifying the 2020–2022 triple-dip La Niña, using observational datasets. 

---

## Repository structure

```
Aerosol-Nina/
├── data/           # Input data files (CSVs, etc.)
├── notebooks/      # Jupyter notebooks for exploration and figures
├── src/            # Source code: reusable functions and processing scripts
├── work/           # Scratch space for in-progress or personal working files
├── README.md       # This file
└── pyproject.toml  # Python package configuration and dependencies
```

### `data/`
Contains input data files used across the project. Currently includes:
- `RONI_timeseries.csv` — the Relative Oceanic Niño Index (RONI) in a long-format monthly timeseries, derived from the [NOAA CPC RONI page](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/).

Large reanalysis files (e.g. NetCDF datasets) are **not** tracked by Git due to their size.

### `notebooks/`
Jupyter notebooks used for exploratory analysis and generating figures. Notebooks should be treated as outputs — runnable from top to bottom using the functions in `src/`. They are a good place to look if you want to understand what the code produces.

### `src/`
The core codebase. Functions here are designed to be importable and reusable across notebooks and scripts. Key files:
- `nina_composites.py` — reads the RONI index, identifies La Niña events by the standard ONI threshold criteria, and constructs SST composites for all events and multi-year events separately.

When adding new functionality, please put reusable functions here rather than in notebooks.

### `work/`
A personal scratch directory for in-progress code, quick tests, and anything not yet ready for `src/` or `notebooks/`. Files here are not expected to be clean or reproducible. Feel free to create a subdirectory with your name (e.g. `work/your_name/`) to keep things organised.

---

## Getting started

### 1. Clone the repository

Open a terminal and run:

```bash
git clone https://github.com/manapaap/Aerosol-Nina.git
cd Aerosol-Nina
```

This downloads a full copy of the repository to your machine.

### 2. Set up your Python environment

I recommend using a dedicated conda environment to avoid conflicts with other projects. With conda installed, run:

```bash
conda create -n aerosol-nina python=3.11
conda activate aerosol-nina
pip install -e .
```

The last command installs the project and its dependencies as listed in `pyproject.toml`.

### 3. Obtain the reanalysis data

Large datasets are not stored in the repository. You will need to download them separately and place them in the expected locations. 

### 4. Run the code

Once data is in place, you try to run my example code stored in work/Aakash/nina_demo.py. It shows off how to use the nina_composites function, complemented with some simple plotting code. 

Or open any notebook in `notebooks/` using JupyterLab. You can import modules in a similar way to nina_demo.py. 

```bash
jupyter lab
```

---

## How to contribute

### The basic workflow

When working on something new, **do not edit the `main` branch directly**. Instead:

1. **Create a branch** for your work:
   ```bash
   git checkout -b your-name/description-of-change
   ```
   For example: `git checkout -b alice/add-precipitation-composites`

2. **Make your changes**, then stage and commit them:
   ```bash
   git add src/my_new_file.py
   git commit -m "Add precipitation compositing function"
   ```
   Write commit messages that describe *what* changed and *why*, not just *what files* changed.

3. **Push your branch** to GitHub:
   ```bash
   git push origin your-name/description-of-change
   ```

4. **Open a Pull Request** on GitHub. Go to the repository page, click "Compare & pull request", and write a short description of what your changes do. The project maintainer will review and merge it.

### Keeping your local copy up to date

Before starting new work, make sure you have the latest version of `main`:

```bash
git checkout main
git pull
```

### Guidelines

- Keep functions in `src/` general and well-documented. If a function only makes sense for one specific notebook, it can live in that notebook, but anything reused should go in `src/`.
- Do not commit large data files (NetCDF, large CSVs). Add them to `.gitignore` if needed.
- If you are experimenting, use the `work/` directory rather than modifying existing `src/` files directly.

---

## GitHub basics for scientists

If you are new to Git, here is a minimal mental model:

- **Repository (repo):** the project folder, including its full history of changes.
- **Commit:** a saved snapshot of your changes, with a message describing what you did. Think of it like saving a version of a document, but with a log entry.
- **Branch:** an independent line of development. Working on a branch means your changes do not affect anyone else's work until they are reviewed and merged.
- **Pull request (PR):** a request to merge your branch into `main`. It is also an opportunity for collaborators to review your changes before they become part of the shared codebase.
- **Push / Pull:** pushing sends your local commits to GitHub; pulling fetches new commits from GitHub to your local machine.

A good rule of thumb: **commit often, push before you stop working for the day, and never force-push to `main`.**

For a more thorough introduction, the [Software Carpentry Git lesson](https://swcarpentry.github.io/git-novice/) is written with scientists in mind and takes about two hours to work through.
