# Airplane Boarding Model
 Project Computational Science [5062PRCS6Y] - Project Team 5

## Installation

To install the dependencies use pip and the requirements.txt in this directory:

```
    $ pip install -r requirements.txt
```

## How to Run

To launch the interactive server, run:

```
    $ solara run app.py
```

## Run tests

```
    $ python -m unittest tests/*.py

    For test_random_method.py

    $ python -m unittest tests.test_random_method.SeatsRandomTestCase 

    For test_backtofront_method.py

    $ python -m unittest tests.test_backtofront_method.SeatsBackToFrontTestCase

    For test_steffenperfect_method.py

    $ python -m unittest tests.test_steffenperfect_method.SeatsSteffenPerfectTestCase

    For test_outsidein_method.py

    $ python -m unittest tests.test_outsidein_method.SeatsOutsideInTestCase

    For test_segmentedrandom_method.py

    $ python -m unittest tests.test_segmentedrandom_method.SeatsSegmentedRandomTestCase

```

## Grid

![Grid-based simulation environment - Airbus A320 as reference](Grid-based%20simulation%20environment%20-%20Airbus%20A320%20as%20reference.png)