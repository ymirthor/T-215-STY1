class Error(Exception): pass

class PCB:
    class Process:
        def __init__(self, parent):
            self.state = 1
            self.parent = parent
            self.children = LL()
            self.resources = LL()

    def __init__(self, size=16):
        self.size = size
        self.PCB = [None] * self.size
        self.PCB[0] = self.Process(None)
        self.running = 0
        self.RL = RL()
        self.RCB = RCB()

    def create(self, priority):
        if priority == 0:
            print('Only process 0 can have priority 0')
            raise Error()
        if priority > self.RL.levels:
            print('Priority level does not exist')
            raise Error()
        # Allocate space for new process
        for i, slot in enumerate(self.PCB):
            if slot == None:
                idx = i
                break
        else:
            print("list is full")
            return
        
        # Create new process, state = 1
        self.PCB[idx] = self.Process(self.running)
        
        # Put new process in children of running
        self.PCB[self.running].children.add(idx)
        
        # Insert new process to ready list
        self.RL.add(idx, priority)
        print(f"process {idx} created")
        self.scheduler()

    def scheduler(self):
        for ll in self.RL.RL[::-1]:
            if ll.head.data != None:
                self.running = ll.head.data
                break

    def _delete(self, idx):
        n = 1
        children = self.PCB[idx].children
        resources = self.PCB[idx].resources
        self.PCB[idx] = None
        self.RL.remove(idx)
        for i in resources:
            self.release(i.data)
        
        for child in children:
            if child != None:
                n += self._delete(child)

        return n

    def delete(self, idx):
        # Prevent deletion of process 0
        if idx == 0:
            print('cannot delete process 0')
            return
        
        # Delete process i and all children processes
        n = self._delete(idx)

        # Remove process i from children in parent
        for process in self.PCB:
            if process == None:
                continue
            if idx in process.children:
                process.children.remove(idx)    
        
        print(f'{n} processes destroyed')


        self.scheduler()

    def request(self, idx):
        # If resource is free
        if self.RCB.RCB[idx].state:
            self.RCB.RCB[idx].state = 0
            self.PCB[self.running].resources.add(idx)
            print(f'resource {idx} allocated')
            return
        # If resource is allocated
        self.PCB[self.running].state = 0
        # Remember priority
        for idx, i in enumerate(self.RL.RL):
            if self.running in i:
                pri = idx
        self.RCB.RCB[idx].waitlist.add((self.running,pri))
        self.RL.remove(self.running)
        print(f'process {self.running} blocked')
        self.scheduler()

    def release(self, resource):
        # Remove resource from process
        if resource in self.PCB[self.running].resources:
            self.PCB[self.running].resources.remove(resource)
        else:
            raise Error()
        
        # Check if waitlist is empty
        if len(self.RCB.RCB[resource].waitlist) == 0:
            self.RCB.RCB[resource].state = 1
        else:
            process, pri = self.RCB.RCB[resource].waitlist.head.data
            self.RCB.RCB[resource].waitlist.remove(process)
            self.RL.add(process, pri)
        
        print(f'resource {resource} released')

    def timeout(self):
        self.RL.timeout(self.running)
        self.scheduler()
        print(f'process {self.running} running')


class RCB:
    class Resource():
        def __init__(self):
            self.state = 1
            self.waitlist = LL()
    
    def __init__(self, resources=4):
        self.recources = resources
        self.RCB = [self.Resource() for _ in range(self.recources)]


class RL:
    def __init__(self, levels=3):        
        self.levels = levels
        self.RL = [LL() for _ in range(self.levels)]
        self.add(0,0)

    def add(self, idx, priority):
        self.RL[priority].add(idx)

    def remove(self, idx):
        for level in self.RL:
            level.remove(idx)

    def timeout(self, idx):
        for pri, level in enumerate(self.RL):
            if idx in level:
                self.remove(idx)
                self.add(idx, pri)
            

class LL:
    class Node:
        def __init__(self, data):
            self.data = data
            self.next = None
    
    def __init__(self):
        self.head = self.tail = self.Node(None)
        self.length = 0
    
    def __iter__(self):
        if self.head.data == None:
            return
        
        curr = self.head
        while curr != None:
            yield curr.data
            curr = curr.next

    def __str__(self):
        ret_list = []
        for i in self:
            ret_list.append(str(i))
        return ", ".join(ret_list)

    def __in__(self, item):
        for i in self:
            if i == item:
                return True
        return False

    def __len__(self):
        return self.length

    def add(self, idx):
        self.length += 1
        if self.tail.data == None and idx != None:
            self.tail.data = idx
            return
        new_node = self.Node(idx)
        self.tail.next = new_node
        self.tail = new_node

    def remove(self, idx):
        if idx == self.head.data:
            if self.head.next == None:
                self.head.data = None
            else:
                self.head = self.head.next
            self.length -= 1
            return

        prev = self.head
        curr = self.head.next
        while curr != None:
            if curr.data == idx:
                prev.next = curr.next
                self.length -= 1
                return
            prev = curr
            curr = curr.next


def manager():
    import os
    # for inp in open('input.txt'):
    #     inp = inp.strip()
    while True:
        inp = input('Command: ')
        os.system('cls')
        if inp.strip() == "in":
            pcb = PCB()
            print(f'New PCB[{len(pcb.PCB)}] created')
        
        elif inp == 'to':
            pcb.timeout()

        else:
            try:
                commands = {
                    'cr': pcb.create,
                    'de': pcb.delete,
                    'rq': pcb.request,
                    'rl': pcb.release,
                }
                cmd, pri = inp.split()
                pri = int(pri)
                commands[cmd](pri)
                
            except Exception:
                print('-1')
        try:
            pcb
        except UnboundLocalError:
            continue
            
        width = 70
        # Ready list
        print('Ready List'.center(width), sep='')
        for idx, i in enumerate(pcb.RL.RL):
            print(f'( Priority {idx}:', f'[{str(i)}]',')', end=' ')
        print()
        print('—'*(width))

        # RCB
        print('Resource Control Block'.center(width))
        for idx, i in enumerate(pcb.RCB.RCB):
            m = str(f'Resource {idx}: ' + f'State={str(i.state)}, ')
            m += str(f'Waitlist=[{i.waitlist}]')
            print(m.ljust(width))
        print('—'*(width))

        # PCB
        print('Process Control Block'.center(width))
        length = len(pcb.PCB)
        state = []
        parent = []
        children = []
        max_column = [1 for i in range(length)]
        resources = []

        for idx, i in enumerate(pcb.PCB):
            if i:
                state.append(i.state)
                parent.append(i.parent)
                children.append(str(i.children))
                resources.append(str(i.resources))

                max_column[idx] = max(max_column[idx], len(str(i.children)))
                max_column[idx] = max(max_column[idx], len(str(i.resources)))
            else:
                state.append('-')
                parent.append('-')
                children.append('-')
                resources.append('-')
        running = ['x' if i==pcb.running else '-' for i in range(length)]
        pcb_list = [state, parent, children, resources, running]
        line_names = ['State', 'Parent', 'Children', 'Resources', 'Running']
        line_names_space = 10
        min_column = 3
        line_length = line_names_space
        
        print(' ' * line_names_space, end='|')

        for i in range(length):
            line_length += max(min_column, max_column[i])
            print(str(i).center(max(min_column, max_column[i])), end=' | ')
        print()
        line_length += length * 3
        print('—' * line_length)

        for idx, line in enumerate(pcb_list):
            print(f'{line_names[idx]:{line_names_space}}', end='|')
            for idx2, i in enumerate(line):
                if i == None or str(i) == '':
                    i = '-'
                print(f'{str(i):^{max(min_column, max_column[idx2])}}', end=' | ')
            print()
        print()

if __name__ == "__main__":
    manager()
    
    # for idx, i in enumerate(pcb.PCB):
    #     print(f"{idx:2}", "p:", i.parent, "c:", i.children)
    