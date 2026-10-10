# Small interpreter shared by animation and solution validation.
# State list: pc, held value, memory, unread input, output, steps, status, message.
PC, HELD, MEMORY, INPUT, OUTPUT, STEPS, STATUS, MESSAGE = range(8)
JUMPS = ['JUMP', 'ZERO', 'NEG']
MEMORY_OPS = ['STORE', 'LOAD', 'ADD', 'SUB']


def newMachine(values):
    return [0, None, [0, 1, 3, None, None, None, None, None],
            values[:], [], 0, 'ready', 'Ready for a new program.']


def findLine(program, identity):
    for i in range(len(program)):
        if program[i][2] == identity:
            return i
    return -1


def stopWithError(state, message):
    state[STATUS] = 'error'
    state[MESSAGE] = message


def finishMachine(state, expected):
    if state[OUTPUT] == expected and not state[INPUT]:
        state[STATUS] = 'success'
        state[MESSAGE] = 'Output verified.'
    else:
        stopWithError(state, 'Incomplete output or unread input. Check your loop.')


def stepMachine(program, state, expected):
    # Return an animation event: (command, memory address, packet value).
    if state[STATUS] in ['error', 'success']:
        return ('', 0, None)
    pc = state[PC]
    if pc == len(program):
        finishMachine(state, expected)
        return ('', 0, None)
    if pc < 0 or pc > len(program):
        stopWithError(state, 'Program counter is outside the program.')
        return ('', 0, None)
    command, operand, identity = program[pc]
    if command == 'READ' and not state[INPUT]:
        finishMachine(state, expected)
        return ('', 0, None)
    if state[STEPS] >= 5000:
        stopWithError(state, '5,000-step limit reached. Check for an endless loop.')
        return ('', 0, None)
    if command not in ['READ', 'SEND', 'STORE', 'LOAD', 'ADD', 'SUB'] + JUMPS:
        stopWithError(state, 'Unknown instruction.')
        return ('', 0, None)
    if command in ['SEND', 'STORE', 'ADD', 'SUB', 'ZERO', 'NEG']:
        if state[HELD] is None:
            stopWithError(state, command + ' needs a held value. READ or LOAD first.')
            return ('', 0, None)
    if command in MEMORY_OPS:
        if operand is None or not 0 <= operand < 8:
            stopWithError(state, 'Choose a memory address from 0 to 7.')
            return ('', 0, None)
        if command != 'STORE' and state[MEMORY][operand] is None:
            stopWithError(state, 'Empty memory. STORE a value before reading it.')
            return ('', 0, None)
    if command in JUMPS:
        target = findLine(program, operand)
        if target == -1:
            stopWithError(state, 'Unconnected jump. Drag its dot to a program row.')
            return ('', 0, None)
    state[STEPS] += 1
    state[STATUS] = 'active'
    state[MESSAGE] = 'Executed ' + command + ' on line ' + str(pc + 1)
    nextPC = pc + 1
    packet = state[HELD]
    if command == 'READ':
        state[HELD] = state[INPUT].pop(0)
        packet = state[HELD]
    elif command == 'SEND':
        state[OUTPUT].append(state[HELD])
        state[HELD] = None
        if state[OUTPUT] != expected[:len(state[OUTPUT])]:
            stopWithError(state, 'Wrong packet at output ' + str(len(state[OUTPUT])) + '.')
    elif command == 'STORE':
        state[MEMORY][operand] = state[HELD]
    elif command == 'LOAD':
        state[HELD] = state[MEMORY][operand]
    elif command == 'ADD':
        state[HELD] += state[MEMORY][operand]
    elif command == 'SUB':
        state[HELD] -= state[MEMORY][operand]
    elif command == 'JUMP':
        nextPC = target
    elif command == 'ZERO' and state[HELD] == 0:
        nextPC = target
    elif command == 'NEG' and state[HELD] < 0:
        nextPC = target
    state[PC] = nextPC
    return (command, operand, packet)
