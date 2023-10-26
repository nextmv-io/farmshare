<img src="logo.svg" align="right" height="110"/>

# Farmshare Vehicle Routing Service

[![test](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml)
[![nextmv](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml)

Example of solving a Vehicle Routing Problem using [OR-Tools](https://developers.google.com/optimization/routing/vrp).

The app is hosted, managed and versioned by [Nextmv](https://nextmv.io/) ([link to app](https://cloud.nextmv.io/acc/1938e794-c31c-4e65-9d63-fa50be77a82a/app/farmshare-ortools)).

## Usage example (local)

Install requirements:

```bash
pip3 install -r requirements.txt
```

Run the command below to check that everything works as expected:

```bash
python3 main.py -input input.json -output output.json -duration 30
```

A file `output.json` should have been created with the solution.

## Usage example (remote)

Push the app to Nextmv:

```bash
nextmv app push -a farmshare-ortools
```

Make a run:

```bash
nextmv app run -a farmshare-ortools -i input.json -w > output.json
```

Create a new instance with a new version of the app:

```bash
VERSION_ID=$(git rev-parse --short HEAD)
nextmv app version create -a farmshare-ortools -name $VERSION_ID -version $VERSION_ID
nextmv app instance create -a farmshare-ortools -v $VERSION_ID -i candidate-1 -n "Test candidate 1"
```
