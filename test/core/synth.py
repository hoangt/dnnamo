import unittest
import nnmodel
import tensorflow as tf

from nnmodel.core.primop import Primop
from nnmodel.core.dgraph import DGraph

class Primop_example(Primop):
  def __init__(self):
    super(Primop_example,self).__init__()
    self.device = 'test'

class DGraphTestCase(unittest.TestCase):
  @staticmethod
  def synth_dgraph():
    DG = nnmodel
    DG = DGraph()
    # Add some nodes
    (p0,p1,p2) = [Primop_example() for _ in range(3)]
    [DG.add_primop(p) for p in (p0,p1,p2)]
    # Add a nice set of circular dependencies
    DG.add_dep(p0,p1)
    DG.add_dep(p1,p2)
    DG.add_dep(p2,p0)
    return DG

  def setUp(self):
    self.DG = self.synth_dgraph()

class TFTestCase(unittest.TestCase):
  @staticmethod
  def synth_ff_network():
    '''Synthetic feed-forward convnet for testing.
    Topology:
    13x16x16x1 --[3x3]-> 13x16x16x16 --[4:1]-> 13x4x4x16 --[softmax]-> 13x10'''
    g = tf.Graph()
    with g.device('/cpu:0'):
      with g.as_default():
        # conv
        cv_in = tf.placeholder(tf.float32, [13,16,16,1])
        cv_W = tf.Variable(tf.truncated_normal([3,3,1,16]))
        cv_B = tf.Variable(tf.truncated_normal([16]))
        cv_tmp = tf.nn.conv2d(cv_in, cv_W, [1,1,1,1], 'SAME')
        cv_out = tf.nn.bias_add(cv_tmp, cv_B)
        # 4:1 maxpool
        mp_out = tf.nn.max_pool(cv_out, [1,4,4,1], [1,4,4,1], 'SAME')
        # softmax
        sf_in = tf.reshape(mp_out, [13,4*4*16])
        sf_W = tf.Variable(tf.truncated_normal([4*4*16,10]))
        sf_B = tf.Variable(tf.truncated_normal([10]))
        sf_tmp0 = tf.matmul(sf_in, sf_W)
        sf_tmp1 = tf.add(sf_tmp0, sf_B)
        #pylint: disable=unused-variable
        sf_out = tf.nn.softplus(sf_tmp1)
    return g
