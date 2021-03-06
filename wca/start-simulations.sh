#!/bin/sh

set -ev

cargo build --release

rq run -J wca-1-1-0.5 -- ../target/release/energy-wca --reduced-density 1 --N 32 --sad-min-T 0.5 --energy-bin 1.0 --max-allowed-energy 640 --acceptance-rate 0.5 --movie-time '10^(1/4)' --save-time 0.5 --save-as sad-n1.0-de1.0-minT-0.5.yaml

rq run -J wca-1-0.1-0.5 -- ../target/release/energy-wca --reduced-density 1 --N 32 --sad-min-T 0.5 --energy-bin 0.1 --max-allowed-energy 640 --acceptance-rate 0.5 --movie-time '10^(1/4)' --save-time 0.5 --save-as sad-n1.0-de0.1-minT-0.5.yaml

rq run -J wca-1-0.01-0.5 -- ../target/release/energy-wca --reduced-density 1 --N 32 --sad-min-T 0.5 --energy-bin 0.01 --max-allowed-energy 640 --acceptance-rate 0.5 --movie-time '10^(1/4)' --save-time 0.5 --save-as sad-n1.0-de0.01-minT-0.5.cbor
