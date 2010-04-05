#!/bin/bash

sfood tooltest.py syspolicy/ | sfood-graph | dot -Tps2 | ps2pdf14 - depgraph.pdf
