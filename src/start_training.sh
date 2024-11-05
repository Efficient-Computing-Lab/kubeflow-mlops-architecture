#!/bin/bash
cp -r /datasets/epos/training_set /app/datasets/carObj12/
mv /app/datasets/carObj12/training_set /app/datasets/carObj12/train_primesense
# Ensure unbuffered output for Python and Bash

python -c "print('-----create a list of images to include in the TFRecord file-----')"
python epos/scripts/create_example_list.py --dataset=carObj12 --split=train --split_type=primesense
python -c "print('')"  # Empty line
python -c "print('-----create the TFRecord file-----')"
python epos/scripts/create_tfrecord.py --dataset=carObj12 --split=train --split_type=primesense --examples_filename=carObj12_train-primesense_examples.txt --add_gt=True --shuffle=True --rgb_format=png
python -c "print('')"  # Empty line
python -c "print('-----train the model-----')"
python epos/scripts/train.py --model=obj12
python -c "print('Training finished')"

# Copy the contents from source to destination
cp -r /app/store/tf_models /trained_models/epos


