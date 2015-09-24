import sys
sys.path.append('.')
from ikalog.scenes.result_detail import *

if __name__ == "__main__":
    obj = IkaKdRecoginizer()
    obj.loadModelFromFile('data/kd.model')
    obj.train()
    files = sys.argv[1:]

    list = []
    for file in files:
        img = cv2.imread(file)
        num = obj.match(img)
        t = (num, file)
        list.append(t)

    n = 0
    last_num = -1
    print('<table>')
    tr = False
    max_n = 35
    for e in sorted(list):
        if last_num != e[0]:
            if tr:
                print('</tr>')
                tr = False
                n = 0

        if (n % max_n == 0):
            print('<tr>')
            tr = True

        print('<td>%d <img src=%s></td>' % (e[0], e[1]))
        last_num = e[0]

        n = n + 1

        if n % max_n == 0:
            print('</tr>')
            tr = False

    if tr:
        print('</tr>')
    print('</table>')
