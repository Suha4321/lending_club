#!/bin/bash
# script to download the data in S3 bucket

pip install kaggle-cli
echo "installing kaggle cli"

export KAGGLE_USERNAME=username
export KAGGLE_KEY=pw

mkdir lending_club

~/.local/bin/kaggle datasets download wendykan/lending-club-loan-data -p /Users/ubuntu/lending_club --unzip
