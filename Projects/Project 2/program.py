from collections import deque as LL

class VM_Manager:
    def __init__(self):
        self.s_size = 9
        self.p_size = 9
        self.w_size = 9

        self.PM = [None] * 2**19         # PM[524288]
        self.D = [[None] * 2**10] * 2**9 # D[1024][512]

        self.free_frames = LL([i for i in range(2**10)])
        self.occupied_frames = [0,1]

    def get_free_frame(self):
        while True:
            frame = self.free_frames.popleft()
            if frame not in self.occupied_frames:
                return frame

    def create_ST(self, s, z, f):
        if f >= 0:
            self.occupied_frames.append(f)
        self.PM[2 * s] = z
        PT_idx = 2 * s + 1
        self.PM[PT_idx] = f

    def create_PT(self, s, p, f):
        PT = self.PM[2 * s + 1]
        if PT < 0:
            self.D[-PT][p] = f
        else:
            self.occupied_frames.append(f)
            self.PM[PT * 512 + p] = f

    def translate_VA(self, VA):
        s = VA >> (self.p_size + self.w_size)
        p = (VA >> self.w_size) & 2 ** self.p_size - 1
        w = VA & 2 ** self.w_size - 1
        pw = VA & 2 ** (self.p_size + self.w_size) - 1
 
        return s, p, w, pw

    def PA(self, s, p, w, pw):
        if pw >= self.PM[2 * s]:
            return -1
        
        PT = self.PM[2 * s + 1]
        if PT < 0:
            f1 = self.get_free_frame()
            self.PM[f1 * 512 + p] = self.D[-PT][p]
            PT = f1
        
        pg = self.PM[PT * 512 + p]
        if pg < 0:
            f2 = self.get_free_frame()
            pg = f2

        return pg * 512 + w


def line_input(string):
    nested = []
    lis = []
    for idx, i in enumerate(string.split(), start=1):
        lis.append(int(i))
        if idx % 3 == 0:
            nested.append(lis)
            lis = []
    return nested


if __name__ == "__main__":
    manager_no_dp = VM_Manager()
    manager_dp = VM_Manager()

    init_dp = open('init-dp.txt','r')
    input_dp = open('input-dp.txt', 'r')
    init_no_dp = open('init-no-dp.txt','r')
    input_no_dp = open('input-no-dp.txt', 'r')
    
    STs_dp = line_input(init_dp.readline())
    for ST in STs_dp:
        manager_dp.create_ST(*ST)
    STs_no_dp = line_input(init_no_dp.readline())
    for ST in STs_no_dp:
        manager_no_dp.create_ST(*ST)

    PTs_dp = line_input(init_dp.readline())
    for PT in PTs_dp:
        manager_dp.create_PT(*PT)
    PTs_no_dp = line_input(init_no_dp.readline())
    for PT in PTs_no_dp:
        manager_no_dp.create_PT(*PT)

    VAs_dp = list(map(int, input_dp.readline().split()))
    VAs_no_dp = list(map(int, input_no_dp.readline().split()))

    PAs_dp = []
    for idx, address in enumerate(VAs_dp, start=1):
        spw_pw = manager_dp.translate_VA(address)
        PA = manager_dp.PA(*spw_pw)
        PAs_dp.append(PA)
    PAs_no_dp = []
    for idx, address in enumerate(VAs_no_dp, start=1):
        spw_pw = manager_no_dp.translate_VA(address)
        PA = manager_no_dp.PA(*spw_pw)
        PAs_no_dp.append(PA)
    print(*PAs_no_dp)
    print(*PAs_dp)

    with open('output.txt','w') as out:
        out.write(' '.join(map(str,PAs_no_dp)) + '\n')
        out.write(' '.join(map(str,PAs_dp)))