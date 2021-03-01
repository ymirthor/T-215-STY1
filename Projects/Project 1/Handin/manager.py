from program import PCB

def manager(debug=False, shell=False, read_from_file=False):
    import os
    iterator = range(99999999999999999999999)
    output_str = ''
    if read_from_file:
        while True:
            try:
                iterator = open(input('Enter filename: '))
                break
            except FileNotFoundError:
                print('Enter valid filename')        
        output = open('output.txt', 'w+')
    

    for i in iterator:
        if not shell and not read_from_file:
            print('Command: ', end='')
        if read_from_file:
            inp = i.strip()
            if not shell:
                input()
            if inp == '':
                print()
                continue
        else:
            inp = input()

        if not shell:
            os.system('cls')
        
        if inp.strip() == "in":
            print()
            if output_str:
                output.write(output_str + '\n')
            output_str = ''
            pcb = PCB()
            if not shell:
                print(f'New PCB[{len(pcb.PCB)}] created')
        
        elif inp == 'to':
            pcb.timeout()

        else:
            commands = {
                'cr': pcb.create,
                'de': pcb.destroy,
                'rq': pcb.request,
                'rl': pcb.release,
            }
            if debug and not shell:
                cmd, pri = inp.split()
                pri = int(pri)
                message = commands[cmd](pri)
                print(message)
            else:
                try:
                    cmd, pri = inp.split()
                    pri = int(pri)
                    message = commands[cmd](pri)
                    if not shell:
                        print(message)
                except Exception:
                    output_str += '-1 '
                    print('-1', end=' ')
                    if not shell:
                        print()
                    else:
                        continue
        try:
            pcb
        except UnboundLocalError:
            continue

        if not shell:
            width = 100

            # Ready list
            print('Ready List'.center(width), sep='')
            for idx, i in enumerate(pcb.RL):
                print(f'( Priority {idx}:', f'{list(i)}',')', end=' ')
            print()
            print('—'*(width))

            # RCB
            print('Resource Control Block'.center(width))
            for idx, i in enumerate(pcb.RCB):
                m = str(f'Resource {idx}: ' + f'State={str(i.state)}, ')
                m += str(f'Waitlist={list(i.waitlist)}')
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
                    children.append(", ".join(map(str, i.children)))
                    resources.append(', '.join(map(str, i.resources)))

                    max_column[idx] = max(max_column[idx], len(", ".join(map(str, i.children))))
                    max_column[idx] = max(max_column[idx], len(', '.join(map(str, i.resources))))
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
        
        else:
            output_str += str(pcb.running) + ' '
            print(pcb.running, end=" ")
    output.write(output_str)
    output.close()

if __name__ == "__main__":
    print('USER INPUT [0]')
    print('READ FILE  [1]')
    while True:
        try:
            choice = int(input())
            assert(0 <= choice <= 1)
            break
        except (ValueError, AssertionError):
            print('choose from list')
    manager(debug=0, shell=choice, read_from_file=choice)