<img src="../assets/pyomo.png" align="right" height="110"/>

# Farmshare Shift Assignment Service

[![test](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/test.yml)
[![nextmv](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml/badge.svg?event=push&branch=stable)](https://github.com/nextmv-io/farmshare/actions/workflows/nextmv.yml)

Example of solving a shift assignment problem using
[Pyomo](http://www.pyomo.org).

The app is hosted, managed and versioned by [Nextmv](https://nextmv.io/).

## Usage example (local)

Install requirements:

```bash
pip3 install -r requirements.txt
```

Run the command below to check that everything works as expected:

```bash
python3 main.py -input input.json -output output.json -duration 30 -provider cbc
```

A file `output.json` should have been created with the solution.

## Usage example (remote)

Push the app to Nextmv:

```bash
nextmv app push -a shift-assignment-pyomo
```

Make a run:

```bash
nextmv app run -a shift-assignment-pyomo -i input.json -w > output.json
```

Create a new instance with a new version of the app:

```bash
VERSION_ID=$(git rev-parse --short HEAD)
nextmv app version create \
    -a shift-assignment-pyomo \
    -n $VERSION_ID \
    -v $VERSION_ID
nextmv app instance create \
    -a shift-assignment-pyomo \
    -v $VERSION_ID \
    -i candidate-1 \
    -n "Test candidate 1"
```

Create an acceptance test:

```bash
NEXTMV_API_KEY="<YOUR-API-KEY>"
ACCEPTANCE_TEST_ID=$(git rev-parse --short HEAD)
INPUT_SET_ID="<AN-INPUT-SET-ID>"
python ci-cd-tests.py
```
