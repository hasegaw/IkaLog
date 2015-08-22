#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import unittest
from IkaScene_ResultDetail import *

class IkaLogUnitTest(unittest.TestCase):
    pass

def generateTest(filename, expected):
    def t(self):
        target = cv2.imread(filename)
        obj = IkaScene_ResultDetail()
        
        context = {
		    'engine': { 'frame': target },
		    'game': {},
	    }
        
        matched = obj.match(context)
        analyzed = obj.analyze(context)
        for i in range(0, 8):
            self.assertEqual(context['game']['players'][i]['weapon'], expected['players'][i]['weapon'])
    return t

if __name__ == "__main__":
	if len(sys.argv) > 2:
		jsonfilename = sys.argv[1]
	else:
		jsonfilename = 'tests/testcases.json'

	json_file = open(jsonfilename, 'r', encoding = 'utf-8')
	testcases = json.load(json_file)
	json_file.close
	del json_file

	for case in testcases:
		filename = case['filename']
		testname = 'test_' + filename
		testfunc = generateTest(filename, case['expected'])
		setattr(IkaLogUnitTest, testname, testfunc)

	unittest.main()