# Airplane Boarding Model
Project Computational Science [5062PRCS6Y] - Project Team 5

## Installation

To install the dependencies use pip and the requirements.txt in this directory:

```
    $ pip install -r requirements.txt
```

## How to run interactive server

To launch the interactive server:

```
    $ solara run app.py
```

## How to collect the results

To collect the results for the validation plots:

```
    $ python batch_run_validation.py
```

Validation results are outputted to a csv file in results/validation folder.

To collect the results for the experiment plots:

```
    $ python batch_run_experiment.py
```

Experiment results are outputted to a csv file in results/experiment folder.

## How to plot the results

To plot the validation results:

```
    $ python analysis_validation.py
```

To plot the experiment results:

```
    $ python analysis_experiment.py
```


## How to run tests

```
    $ python -m unittest -v tests/*.py
```

## References

- Schultz, Michael (Mar. 2018). “Field Trial Measurements to Validate a Stochastic Aircraft Boarding Model”. In: Aerospace 5.1 Number: 1 Publisher: Multidisciplinary Digital Publishing Institute, p. 27. issn: 2226-4310. doi: 10.3390/aerospace5010027.
- Schultz, Michael, Thomas Kunze, and Hartmut Fricke (June 2013). “Boarding on the critical path of the turnaround”. In: Proceedings of the 10th USA/Europe Air Traffic Management Research and Development Seminar, ATM 2013.
- Schultz, Michael, Christian Schulz, and Hartmut Fricke (June 2008). “Efficiency of Aircraft Boarding Procedures”. In: ICRAT - International Conference on Research in Airport Transportation.