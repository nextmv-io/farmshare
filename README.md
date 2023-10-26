<img src="logo.svg" align="right" height="110"/>

# Farmshare Vehicle Routing Service

[![test](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml)
[![nextmv](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml)

Example of solving a Vehicle Routing Problem using [OR-Tools](https://developers.google.com/optimization/routing/vrp).

The app is hosted, managed and versioned by [Nextmv](https://nextmv.io/) ([link to app](https://cloud.nextmv.io/acc/3f62aeb3-6ba4-414b-9e0c-913e144e3afc/app/ortools)).

## Usage

Install requirements:

```bash
pip3 install -r requirements.txt
```

Run the command below to check that everything works as expected:

```bash
python3 main.py -input input.json -output output.json -duration 30
```

A file `output.json` should have been created with the solution.
