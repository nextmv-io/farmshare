<img src="logo.svg" align="right" height="110"/>

# Farmshare Vehicle Routing Service

[![test](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml)
[![nextmv](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml)

Example of solving a Vehicle Routing Problem using [OR-Tools](https://developers.google.com/optimization/routing/vrp).

The app is hosted, managed and versioned by [Nextmv](https://nextmv.io/) ([link to app](https://cloud.nextmv.io/acc/1938e794-c31c-4e65-9d63-fa50be77a82a/app/farmshare-ortools)).

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
