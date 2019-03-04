# Fairway

Software to create fair [Best Ball](https://en.wikipedia.org/wiki/Four-ball_golf) teams.

_Fairway: The center, short-mown portion of a golf hole in between the teeing ground and the green_

## Usage
```
$ ./bin/todo add --name foo
```
Usage: fairway [OPTIONS] PLAYERS_FILE COMMAND [ARGS]...

  Program to create fair Best Ball teams, evaluate their fairness, and
  predict their scores.

Options:
  -i, --iterations INTEGER RANGE  the number of simulations to be performed
  -f, --full-handicap             Full handicap will be used to estimate the
                                  fairness of the teams
  -n, --no-handicap               No handicap will be used to estimate the
                                  fairness of the teams
  -a, --allowance INTEGER RANGE   handicap adjustment (it must be a value
                                  within 0 and 100)
  -b, --best-balls INTEGER RANGE  number of best balls
  -d, --distributions PATH        the file containing the handicap
                                  distributions file
  -l, --logging-level [info|warn|debug]
  --help                          Show this message and exit.

Commands:
  assign    Assign the input players to the desired...
  estimate  Estimate the probabilities of winning, and...
```
