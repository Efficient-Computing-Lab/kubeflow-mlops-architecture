#!/bin/bash

# Copy and move dataset
cp -r /datasets/epos/training_set /app/datasets/carObj12/
mv /app/datasets/carObj12/training_set /app/datasets/carObj12/train_primesense

python epos/scripts/create_example_list.py --dataset=carObj12 --split=train --split_type=primesense
python epos/scripts/create_tfrecord.py --dataset=carObj12 --split=train --split_type=primesense --examples_filename=carObj12_train-primesense_examples.txt --add_gt=True --shuffle=True --rgb_format=png
python epos/scripts/train.py --model=obj12

cp -r /app/store/tf_models /trained_models/epos
