#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import chainer
import chainer.functions as F
import chainer.links as L
import chainer.links as L
from chainer import optimizers
from chainer import serializers
import numpy as np

import json
import ikalog.constants as const
import sys

class MLP(chainer.Chain):

    """An example of multi-layer perceptron for MNIST dataset.

    This is a very simple implementation of an MLP. You can modify this code to
    build your own neural net.

    """
    def __init__(self, n_in, n_units, n_out):
        super(MLP, self).__init__(
            l1=L.Linear(n_in, n_units),
            l2=L.Linear(n_units, n_units),
            l3=L.Linear(n_units, n_units),
            l4=L.Linear(n_units, n_out),
        )

    def __call__(self, x):
        h1 = F.sigmoid(self.l1(x))
        h2 = F.sigmoid(self.l2(h1))
        h3 = F.sigmoid(self.l3(h2))
        return self.l4(h3)

class Hoge(object):

    def _stages(self):
        stages = sorted(const.stages.keys())
        return stages

    def _rules(self):
        rules= sorted(const.rules.keys())
        return rules 

    def _one_hot_encoding(self, l, key):
        assert isinstance(l, list)
        index = l.index(key)
        r = [0] * len(l)
        r[index] = 1
        return r

    def _decode_one_hot_encoding(self, l, vec):
        assert isinstance(l, list)
        assert isinstance(vec, list)
        assert len(l) == len(vec)

        r = {}
        for i in range(len(l)):
            r[l[i]] = vec[i]
        return r

    def _event_ranked_battle_event_to_vec(self, e):
        r = 0
        if e['value'] == 'they_got':
            r = -1

        elif e['value'] == 'they_lost':
            r = -0.5

        elif e['value'] == 'we_got':
            r = 1

        elif e['value'] == 'we_lost':
            r = 1

        return [r]

    def _event_splatzone_event_to_vec(self, e):
        tf = {True: 1, False: 0}

        return [
            1 - e['my_team_count'] * 0.01,
            1 - e['his_team_count'] * 0.01,
            (e['my_team_count'] - e['his_team_count']) ,
        ]

    def _event_aliveinklings_to_vec(self, e):
        r = [0] * 8
        for i in range(len(e['my_team'])):
            if e['my_team'][i]:
                r[i] = 1

        for i in range(len(e['his_team'])):
            if e['his_team'][i]:
                r[4 + i] = 1

        return r


    def _inklings_to_vec(self, d, at):
        # FIXME: Sort the array if needed
        inklings = [0] * 8
        since = [0] * 8

        for event in d['events']:
            if event['at'] > at:
                break

            if event['type'] == 'alive_inklings':
                inklings = self._event_aliveinklings_to_vec(event)

                for i in range(len(event['my_team'])):
                    if not event['my_team'][i]:
                        since[i] = None
                    elif since[i] is None:
                        since[i] = event['at']

                for i in range(len(event['his_team'])):
                    if not event['his_team'][i]:
                        since[4 + i] = None
                    elif since[4 + i] is None:
                        since[4 + i] = event['at']

        since2 = [0] * 8
        for i in range(8):
            if since[i] is not None:
                since2[i] = at - since[i]
                since2[i] = int(since2[i]) / 180.0
                if since2[i] > 1:
                    since2[i] = 1
                since2[i] = int(since2[i] * 100) / 100.0


        r= inklings
        r.extend(since2)
       
        return r

    def _stage_to_vec(self, d, at):
        return battle._one_hot_encoding(battle._stages(), d.get('map', {}).get('key'))

    def _rule_to_vec(self, d, at):
        return battle._one_hot_encoding(battle._rules(), d.get('rule', {}).get('key'))

    def _gametime_to_vec(self, d, at):
        at_offset = at / (1000.0 * 180)
        at_progress = at / self.get_max_at(d) / 1000.0

        return [at_offset, at_progress]

    def _ranked_objective_to_vec(self, d, at):
        obj_status = [0]
        obj_status2 = [0, 0, 0]
        # FIXME: Sort the array if needed
        for event in d['events']:
            if event['at'] > at:
                break

            if event['type'] == 'ranked_battle_event':
                obj_status = self._event_ranked_battle_event_to_vec(event)
            elif event['type'] == 'splatzone':
                obj_status2 = self._event_splatzone_event_to_vec(event)

        obj_status.extend(obj_status2)
        return obj_status



    vector_funcs = [
#        [ _stage_to_vec, None ],
#        [ _rule_to_vec, None ],
        [ _gametime_to_vec, None ],
        [ _inklings_to_vec, None ],
        [ _ranked_objective_to_vec, None ],
    ]


    def get_state_vector_at(self, d, at):
        r = []
        for funcs in self.vector_funcs:
            metric_to_vec = funcs[0]

            vec = metric_to_vec(self, d, at=at)

            if 0:
                r.append(vec)
            else:
                r.extend(vec)

        return r

    def get_max_at(self,d ):
        at = 0.0
        for event in d['events']:
            at = max(at, event['at'])
        return at



    def parse_statink_battle(self, json_data):
        return json_data

    def read_statink_battle_file(self, filename):
        f = open(filename, 'r')
        json_data = json.load(f)
        return self.parse_statink_battle(json_data)




def train(files, epoch=100):
    global model
    global optimizer
    
    X = []
    T = []
    num_files = 0
    for f in files:
        try:
            a = battle.read_statink_battle_file(f)
    
            if a is None:
    #            print('None!')
                continue
    
            if a.get('agent', {}).get('name', '') != 'IkaLog':
    #            print('This is not IkaLog')
                continue
            if a.get('rule', {}).get('key', '') != 'area':
    #            print('This is not area')
                continue
    
            events = a.get('events', [])
            # check for splatzone data
            events2 = [e for e in events if e['type'] == 'splatzone']
            events3 = [e for e in events if e['type'] == 'alive_inklings']
            if len(events2) == 0:
                print('no splatzone data, skip')
                continue
            if len(events3) == 0:
                print('no inkling data, skip')
                continue
    
            print(f)
            num_files = num_files + 1
        
            for at in range(int(battle.get_max_at(a))):
                y = {'win': 1, 'lose': 0 }[a.get('result', {})]
                vec = battle.get_state_vector_at(a, at=at)
                #print(len(vec), vec, y)
        
                X.append(vec)
                T.append(y)
        
        except:
            print('Exception')
            continue

    print('loaded %d games' % num_files)

    for epoch_ in range(epoch):
        x = chainer.Variable(np.asarray(X, dtype=np.float32))
        t = chainer.Variable(np.asarray(T, dtype=np.int32))
        optimizer.update(model, x, t)
        print('epoch %d optimizer accuracy %f loss %f' % (epoch_, model.accuracy.data, model.loss.data))

    print('save the model')
    serializers.save_npz('mlp.model', model)
    print('save the optimizer')
    serializers.save_npz('mlp.state', optimizer)





battle = Hoge()
import pprint
n_units=22
model = L.Classifier(MLP(n_units, n_units, 2))

optimizer = optimizers.Adam()
optimizer.setup(model)

flag_train = False
if flag_train:
    train(sys.argv[2:],epoch=10000)
else:
    print('Load model from')
    serializers.load_npz('mlp.model', model)
    serializers.load_npz('mlp.state', optimizer)
    train(sys.argv[2:],epoch=10000)

X = []
files = sys.argv[1:]
for f in files:
    print(f)
    a = battle.read_statink_battle_file(f)
    for at in range(int(battle.get_max_at(a))):
#    for at in [1000]:
        vec = battle.get_state_vector_at(a, at=at)

        X.append(vec)
    x = chainer.Variable(np.asarray(X, dtype=np.float32))
    predict = model.predictor(x)
    data = np.asarray(F.softmax(predict).data, dtype=np.float)

    yy = {'win': 1, 'lose': 0 }[a.get('result', {})]
    #print(data, yy)
    import pylab as plt
    x = np.array(range(len(data)))
    plt.plot(x, data[:, 1],color="k", marker="o")
    plt.show()
    break

