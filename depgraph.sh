#!/bin/bash

sfood tooltest.py syspolicy/ | sfood-graph | dot -Tps > depgraph.ps
