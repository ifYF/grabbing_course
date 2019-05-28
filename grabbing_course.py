from bs4 import BeautifulSoup as bs
from requests import Session
from time import sleep, time, localtime, strftime
import sys
import os

j_username = input('请输入一卡通账号：')
j_password = input('请输入一卡通密码：')
CID = []
TNo = []

for j in range(6):
    c_num = input('请输入第%d个课程号：' % (j + 1))
    if len(c_num) != 8:
        if len(c_num) != 0:
            raise NameError('课程号必须为8位')
    t_num = input('请输入第%d个教师号：' % (j + 1))
    if len(t_num) != 4:
        if len(t_num) != 0:
            raise NameError('教师号必须为4位')
    CID.append(c_num)
    TNo.append(t_num)

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
        # url = 'http://xk.autoisp.shu.edu.cn:8080'
        url = 'http://xk.autoisp.shu.edu.cn'
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
        # *************************************************************************************************************
        # sys.stdout.write('\rEpoch: %d\tStatus: Dead\tTimeUsed: %.fmin' % (epoch, t))
        # sys.stdout.write('.')
        #         # sys.stdout.flush()
        #         # sleep(1)

    def fast_input(self):
        # url = 'http://xk.autoisp.shu.edu.cn:8080/CourseSelectionStudent/FastInput'
        url = 'http://xk.autoisp.shu.edu.cn/CourseSelectionStudent/FastInput'
        # resp = self.sess.get(url)
        self.sess.get(url)

    def rock_n_roll(self):
        # url = 'http://xk.autoisp.shu.edu.cn:8080/CourseSelectionStudent/CtrlViewOperationResult'
        url = 'http://xk.autoisp.shu.edu.cn/CourseSelectionStudent/CtrlViewOperationResult'
        resp = self.sess.post(url, course_index)
        return resp


def kick_start(workers, sleep_time):
    # timing
    t0 = time()

    # employ workers
    # sys.stdout.write('connecting')
    # sys.stdout.flush()
    # worker = None
    worker = list()
    try:  # ************************************************************************************************************
        # worker = [Worker() for _ in range(workers)]
        print('\n线程准备中')
        for n in range(workers):
            worker.append(Worker())
            sys.stdout.write('\r线程已准备(%d/%d)' % (n + 1, workers))
            sys.stdout.flush()
            sleep(1)
        # print(worker)
    except Exception as err0:
        print('\n\nSomething error:', err0)
        x3 = localtime()
        now3 = strftime('%Y-%m-%d %H:%M:%S', x3)
        print('Now is %s' % now3)
        print('please wait for 40min')
        sleep(40 * 60)
        kick_start(workers, sleep_time)
    print('\nworkers already, start!')

    # let's rock n roll
    succeeded, dead, epoch = False, False, 0
    while not succeeded and not dead:
        for i in range(len(worker)):

            t1 = time()
            t = (t1 - t0) / 60.
            epoch += 1
            resp = None

            try:
                resp = worker[i].rock_n_roll()
            except ConnectionResetError:
                print('\nConnectionResetError!\tRestarting...\n')
                if t <= 40:
                    print('please wait for %.fmin' % (40 - t))
                    sleep((40 - t) * 60)
                kick_start(workers, sleep_time)
            except TimeoutError:
                print('\nTimeoutError!\tRestarting...\n')
                x2 = localtime()
                now2 = strftime('%Y-%m-%d %H:%M:%S', x2)
                print('Now is %s' % now2)
                if t <= 40:
                    print('please wait for %.fmin' % (40 - t))
                    sleep((40 - t) * 60)
                kick_start(workers, sleep_time)
            except Exception as err0:
                print('\n\nSomething error:', err0)
                x3 = localtime()
                now3 = strftime('%Y-%m-%d %H:%M:%S', x3)
                print('Now is %s' % now3)
                if t <= 40:
                    print('please wait for %.fmin' % (40 - t))
                    sleep((40 - t) * 60)
                kick_start(workers, sleep_time)

            if '选课成功课程' in resp.text:
                print('Epoch: %d\tWorker: %d\tStatus: Succeeded\tTimeUsed:%.f min\n' % (epoch, i, t))

                # with open(f'{epoch}_succeeded.html', 'wb+') as f:
                #    f.write(resp.content)
                if '选课失败课程' not in resp.text:
                    succeeded = True
                    os.system('pause')
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
            sleep(sleep_time)


if __name__ == '__main__':
    worker_num = 16
    delay_time = 1
    kick_start(worker_num, delay_time)
