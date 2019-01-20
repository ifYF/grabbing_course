from bs4 import BeautifulSoup as bs
from requests import Session
from time import sleep
import sys
import time

j_username = input('请输入一卡通账号：')
j_password = input('请输入一卡通密码：')
CID = []
TNo = []


for i in range(6):
    CID.append(input('请输入第%d个课程号：' % (i + 1)))
    TNo.append(input('请输入第%d个教师号：' % (i + 1)))
    
course_index = {
    'IgnorClassMark': 'False',
    'IgnorCourseGroup': 'False',
    'IgnorCredit': 'False',
    'StudentNo': j_username,

    'ListCourse[0].CID': CID[0],
    'ListCourse[0].TNo': TNo[0],
    'ListCourse[0].NeedBook': 'false',

    'ListCourse[1].CID': CID[1],
    'ListCourse[1].TNo': TNo[1],
    'ListCourse[1].NeedBook': 'false',

    'ListCourse[2].CID': CID[2],
    'ListCourse[2].TNo': TNo[2],
    'ListCourse[2].NeedBook': 'false',

    'ListCourse[3].CID': CID[3],
    'ListCourse[3].TNo': TNo[3],
    'ListCourse[3].NeedBook': 'false',

    'ListCourse[4].CID': CID[4],
    'ListCourse[4].TNo': TNo[4],
    'ListCourse[4].NeedBook': 'false',

    'ListCourse[5].CID': CID[5],
    'ListCourse[5].TNo': TNo[5],
    'ListCourse[5].NeedBook': 'false'
}

auth = {
    'j_username': j_username,
    'j_password': j_password
}


class Worker(object):
    def __init__(self):
        self.sess = Session()
        self.login()
        self.fast_input()

    def zustand_eins(self):
        url = 'http://xk.autoisp.shu.edu.cn:8080'
        resp = self.sess.get(url)
        soup = bs(resp.content, 'lxml')
        saml_request = soup.input['value']
        relay_state = soup.input.find_next()['value']
        data = {
            'SAMLRequest': saml_request,
            'RelayState': relay_state
        }
        return data

    def zustand_zwei(self, data):
        url = 'https://sso.shu.edu.cn/idp/profile/SAML2/POST/SSO'
        # resp = self.sess.post(url, data)
        self.sess.post(url, data)

    def zustand_drei(self):
        url = 'https://sso.shu.edu.cn/idp/Authn/UserPassword'
        resp = self.sess.post(url, auth)
        soup = bs(resp.content, 'lxml')
        relay_state = soup.input['value']
        saml_request = soup.input.find_next()['value']
        data = {
            'RelayState': relay_state,
            'SAMLRequest': saml_request
        }
        return data

    def zustand_vier(self, data):
        url = 'http://oauth.shu.edu.cn/oauth/Shibboleth.sso/SAML2/POST'
        resp = self.sess.post(url, data)
        # soup = bs(resp.content, 'lxml')
        bs(resp.content, 'lxml')

    def login(self):
        data = self.zustand_eins()
        self.zustand_zwei(data)
        data = self.zustand_drei()
        self.zustand_vier(data)
        sys.stdout.write('.')
        sys.stdout.flush()

    def fast_input(self):
        url = 'http://xk.autoisp.shu.edu.cn:8080/CourseSelectionStudent/FastInput'
        # resp = self.sess.get(url)
        self.sess.get(url)

    def rock_n_roll(self):
        url = 'http://xk.autoisp.shu.edu.cn:8080/CourseSelectionStudent/CtrlViewOperationResult'
        resp = self.sess.post(url, course_index)
        return resp


def kick_start():
    # timing
    t0 = time.time()

    # employ workers
    sys.stdout.write('connecting')
    sys.stdout.flush()
    worker = [Worker() for _ in range(16)]
    print('\nworkers already, start!')

    # let's rock n roll
    succeeded, dead, epoch = False, False, 0
    while not succeeded and not dead:
        for i in range(len(worker)):
            t1 = time.time()
            t = (t1 - t0) / 60.
            epoch += 1
            resp = None

            try:
                resp = worker[i].rock_n_roll()
            except ConnectionResetError:
                print('\nConnectionResetError!\tRestarting...\n')
                if t <= 120:
                    sleep((120-t) * 60)
                    print('please wait for %.fmin' % (120-t))
                kick_start()

            if '选课成功课程' in resp.text:
                print('Epoch: %d\tWorker: %d\tStatus: Succeeded\tTimeUsed:%.f min\n' % (epoch, i, t))
                
                # with open(f'{epoch}_succeeded.html', 'wb+') as f:
                #    f.write(resp.content)
                if '选课失败课程' not in resp.text:
                    succeeded = True
                    break
            elif '选课失败课程' in resp.text:
                sys.stdout.write('\rEpoch: %d\tStatus: Failed\tTimeUsed: %.fmin' % (epoch, t))
                sys.stdout.flush()
                # with open(f'{epoch}_failed.html', 'wb+') as f:
                #    f.write(resp.content)
            else:
                sys.stdout.write('\rEpoch: %d\tStatus: Dead\tTimeUsed: %.fmin' % (epoch, t))
                sys.stdout.flush()
                # with open(f'{epoch}_dead.html', 'wb+') as f:
                #    f.write(resp.content)
                # dead = True
                # break
            # time.sleep(.3)
            sleep(1)
    return not succeeded


if __name__ == '__main__':
    while True:
        ret = False
        try:
            ret = kick_start()
        except Exception as err:
            print('\nSome error:', err)
            sleep(120 * 60)
        if ret:
            break

