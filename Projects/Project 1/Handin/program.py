from collections import deque as LL
class Process:
    def __init__(self, parent, priority):
        self.state = 1 # State: 1=ready / 0=blocked
        self.parent = parent
        self.children = LL()
        self.resources = LL()
        self.priority = priority
        self.blocked_on = None


class Resource:
    def __init__(self):
        self.state = 1 # State: 1=ready / 0=allocated
        self.waitlist = LL() 


class PCB:
    def __init__(self, size=16):
        self.size = size    # Nr of processses in PCB
        self.priorities = 3 # Nr of priorties for RL
        self.resources = 4  # Nr of resources for RCB
        self.RL = [LL() for _ in range(3)] # RL with n priorities
        self.RCB = [Resource() for _ in range(4)] # RCB with n resources
        self.PCB = [None] * self.size # Empty PCB
        self.running = 0 # Running process, starts on 0

        self.PCB[0] = Process(None, 0)
        self.RL[0].append(0)

    def create(self, priority):
        for idx, process in enumerate(self.PCB):
            if process == None:
                self.PCB[idx] = Process(parent=self.running, priority=priority)
                self.PCB[self.running].children.append(idx)
                self.RL[priority].append(idx)
                self.scheduler()
                return f'process {idx} created'

    def scheduler(self):
        for priority in reversed(self.RL):
            if priority:
                self.running = priority[0]
                break

    def _destroy_recur(self, index):
        count = 1
        # Recur destroy children
        for child in list(self.PCB[index].children):
            count += self._destroy_recur(child)
        
        # Release all resources
        for resource in list(self.PCB[index].resources):
            self.release(resource, index)

        # Remove from ready list or from waitlist
        try:
            pri = self.PCB[index].priority
            self.RL[pri].remove(index)
        except ValueError:
            resource = self.PCB[index].blocked_on
            self.RCB[resource].waitlist.remove(index)

        # Remove parent
        parent = self.PCB[self.PCB[index].parent]
        parent.children.remove(index)

        self.PCB[index] = None
        return count

    def destroy(self, index):
        count = self._destroy_recur(index)
        self.scheduler()
        return f'{count} processes destroyed'

    def timeout(self):
        i = self.running
        ready_list = self.RL[self.PCB[i].priority]
        ready_list.remove(i)
        ready_list.append(i)
        self.scheduler()
        return f'process {self.running} running'

    def request(self, index_resource):
        resource = self.RCB[index_resource]
        running_process = self.PCB[self.running]
        if index_resource in running_process.resources:
            return f'process {self.running} already has resource'
        ready_list = self.RL[running_process.priority]
        if resource.state == 1:
            resource.state = 0
            running_process.resources.append(index_resource)
            return f'resource {index_resource} allocated'
        else:
            running_process.state = 0
            running_process.blocked_on = index_resource
            ready_list.remove(self.running)
            resource.waitlist.append(self.running)
            self.scheduler()
            return f'process {self.running} blocked'

    def release(self, index_resource, index=None):
        curr_process = self.PCB[index or self.running]
        resource = self.RCB[index_resource]
        curr_process.resources.remove(index_resource)
        if len(resource.waitlist) == 0:
            resource.state = 1
        else:
            index_process = resource.waitlist.popleft()
            process = self.PCB[index_process]
            self.RL[process.priority].append(index_process)
            process.state = 1
            process.resources.append(index_resource)
        return f'resource {index_resource} released'