#/bin/bash

EMBEDDINGS_FILE="data/wiki2vec.txt.bz2"
if [[ -f $EMBEDDINGS_FILE ]]; then
    mkdir -p data
    wget "http://wikipedia2vec.s3.amazonaws.com/models/en/2018-04-20/enwiki_20180420_100d.txt.bz2" -O $EMBEDDINGS_FILE.bz2
    bunzip2 $EMBEDDINGS_FILE.bz2
else
    echo "\"$EMBEDDINGS_FILE\" already exists! Skipping..."

fi