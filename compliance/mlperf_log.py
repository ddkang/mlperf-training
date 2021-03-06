# Copyright 2018 MLBenchmark Group. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Convenience function for logging compliance tags to stdout.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect
import time
import json
import re
import uuid

from tags import *


PATTERN = re.compile('[a-zA-Z0-9]+')


def get_caller(stack_index=2):
  ''' Returns file.py:lineno of your caller. A stack_index of 2 will provide
      the caller of the function calling this function. Notice that stack_index
      of 2 or more will fail if called from global scope. '''
  caller = inspect.getframeinfo(inspect.stack()[stack_index][0])

  # Trim the filenames for readability.
  return "%s:%d" % (caller.filename, caller.lineno)


def _mlperf_print(key, value=None, benchmark=None, stack_offset=0,
                  tag_set=None, deferred=False):
  ''' Prints out an MLPerf Log Line.

  key: The MLPerf log key such as 'CLOCK' or 'QUALITY'. See the list of log keys in the spec.
  value: The value which contains no newlines.
  benchmark: The short code for the benchmark being run, see the MLPerf log spec.
  stack_offset: Increase the value to go deeper into the stack to find the callsite. For example, if this
                is being called by a wraper/helper you may want to set stack_offset=1 to use the callsite
                of the wraper/helper itself.
  tag_set: The set of tags in which key must belong.
  deferred: The value is not presently known. In that case, a unique ID will
            be assigned as the value of this call and will be returned. The
            caller can then include said unique ID when the value is known
            later.

  Example output:
    :::MLP-1537375353 MINGO[17] (eval.py:42) QUALITY: 43.7
  '''

  return_value = None

  if (tag_set is None and not PATTERN.match(key)) or key not in tag_set:
    raise ValueError('Invalid key for MLPerf print: ' + str(key))

  if value is not None and deferred:
    raise ValueError("deferred is set to True, but a value was provided")

  if deferred:
    return_value = str(uuid.uuid4())
    value = "DEFERRED: {}".format(return_value)

  if value is None:
    tag = key
  else:
    str_json = json.dumps(value)
    tag = '{key}: {value}'.format(key=key, value=str_json)

  callsite = get_caller(2 + stack_offset)
  now = int(time.time())

  message = ':::MLPv0.5.0 {benchmark} {secs} ({callsite}) {tag}'.format(
      secs=now, benchmark=benchmark, callsite=callsite, tag=tag)

  # And log to tensorflow too
  print()  # There could be prior text on a line
  print(message)

  return return_value


NCF_TAG_SET = set(NCF_TAGS)
def ncf_print(key, value=None, stack_offset=2, deferred=False):
  return _mlperf_print(key=key, value=value, benchmark=NCF,
                       stack_offset=stack_offset, tag_set=NCF_TAG_SET,
                       deferred=deferred)


if __name__ == '__main__':
  _mlperf_print('eval_accuracy', {'epoch': 7, 'accuracy': 43.7}, NCF)
  _mlperf_print('train_batch_size', 1024, NCF)
