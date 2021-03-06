from __future__ import absolute_import

import argparse
import logging
import re

from past.builtins import unicode

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions


def run(argv=None):
  """Main entry point; defines and runs the wordcount pipeline."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      default='./data/miserables.txt',
      help='Input file to process.')
  parser.add_argument(
      '--output',
      dest='output',
      default='./outputs/part',
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)

  with beam.Pipeline(options=PipelineOptions(pipeline_args)) as p:

    def format_result(word_count):
      (word, count) = word_count
      return '%s: %s' % (word, count)

    (p
     # Read the text file into a PCollection with each line being an element of the PCollection.
     | 'ReadText' >> ReadFromText(known_args.input)
     | 'Split' >> (beam.FlatMap(lambda x: re.findall(r'[A-Za-z\']+', x)).with_output_types(unicode))
     # Associate each word with a count of 1
     | 'PairWithOne' >> beam.Map(lambda x: (x, 1))
     # Count the occurrences of each word.
     | 'GroupAndSum' >> beam.CombinePerKey(sum)
     | 'Format' >> beam.Map(format_result)
     | 'WriteText' >> WriteToText(known_args.output)
     )


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
