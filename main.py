# ORBIT / The Quiet Station -- kangjiey
from cmu_graphics import *
from machine import *
from levels import LEVELS, SOLUTIONS, EXPLANATIONS, expectedFor

INK = rgb(37, 53, 65)
MUTED = rgb(108, 121, 127)
PAPER = rgb(250, 247, 237)
CREAM = rgb(235, 232, 219)
TEAL = rgb(39, 130, 129)
CORAL = rgb(207, 106, 81)
GOLD = rgb(228, 178, 80)
WHITE = rgb(255, 253, 246)
BLUE = rgb(66, 93, 118)
COLORS = [rgb(163, 210, 198), rgb(245, 188, 148), rgb(194, 205, 224),
          rgb(194, 205, 224), rgb(226, 211, 156), rgb(226, 211, 156),
          rgb(202, 190, 222), rgb(202, 190, 222), rgb(202, 190, 222)]
COMMANDS = ['READ', 'SEND', 'STORE', 'LOAD', 'ADD', 'SUB', 'JUMP', 'ZERO', 'NEG']
NOTES = ['take a packet', 'send held value', 'copy to memory', 'read from memory',
         'add memory', 'subtract memory', 'always jump', 'jump if zero', 'jump if negative']
SCALE = 0.9  # Fit a 1152 x 738 window; interaction coordinates remain logical.
VISIBLE = 15
ROW_Y = 182
ROW_H = 34


def onAppStart(app):
    app.stepsPerSecond = 30
    app.screen = 'map'
    app.answerLevel = 0
    app.answerScroll = 0
    app.level = 0
    app.case = 0
    app.programs = []
    app.certified = []
    app.bestSteps = []
    app.bestSizes = []
    for i in range(len(LEVELS)):
        app.programs.append([])
        app.certified.append(False)
        app.bestSteps.append(None)
        app.bestSizes.append(None)
    app.program = app.programs[0]
    app.nextId = 0
    app.scroll = 0
    app.selected = -1
    app.memoryChoice = 3
    app.dragKind = ''
    app.dragIndex = -1
    app.dragCommand = ''
    app.mouseX, app.mouseY = 0, 0
    app.pressX, app.pressY = 0, 0
    app.help = False
    app.hint = False
    app.fast = False
    app.ticks = 0
    app.result = False
    app.verifying = False
    app.verifyCase = 0
    app.verifyTotals = 0
    app.verifyOutputs = 0
    app.resultSteps = 0
    app.resultSize = 0
    app.resultRate = 0
    app.previousSteps = None
    resetRun(app)


def resetRun(app):
    values = LEVELS[app.level][3][app.case]
    app.state = newMachine(values)
    app.expected = expectedFor(app.level, values)
    app.running = False
    app.dragKind = ''
    app.anim = 0
    app.robotX, app.robotY = 331, 420
    app.targetX, app.targetY = 331, 420
    app.packet = None
    app.lastLine = -1
    app.result = False
    app.verifying = False
    app.message = 'Drag a command card into the program to begin.'


def openMission(app, level):
    app.level = level
    app.case = 0
    app.program = app.programs[level]
    app.scroll = 0
    app.selected = -1
    app.hint = False
    app.dragKind = ''
    app.screen = 'game'
    resetRun(app)


def changed(app):
    app.certified[app.level] = False
    resetRun(app)
    app.message = 'Program updated. Jump connections follow their target cards.'


def canEdit(app):
    return not app.running and not app.verifying and app.anim == 0


def insertCard(app, index, command):
    if len(app.program) >= 64:
        app.message = '64-card limit reached. Remove an unused card.'
        return
    operand = app.memoryChoice if command in MEMORY_OPS else None
    app.program.insert(index, [command, operand, app.nextId])
    app.nextId += 1
    app.selected = index
    changed(app)


def moveCard(app, oldIndex, newIndex):
    card = app.program.pop(oldIndex)
    if newIndex > oldIndex:
        newIndex -= 1
    app.program.insert(newIndex, card)
    app.selected = newIndex
    changed(app)


def deleteCard(app):
    if 0 <= app.selected < len(app.program) and canEdit(app):
        app.program.pop(app.selected)
        app.selected = -1
        app.scroll = min(app.scroll, max(0, len(app.program) - VISIBLE))
        changed(app)
        app.message = 'Card removed. Arrows to that card must be reconnected.'


def changeMemory(app, address):
    app.memoryChoice = address
    if 0 <= app.selected < len(app.program) and canEdit(app):
        if app.program[app.selected][0] in MEMORY_OPS:
            app.program[app.selected][1] = address
            changed(app)


def takeStep(app):
    if app.anim or app.state[STATUS] in ['error', 'success']:
        return
    app.lastLine = app.state[PC]
    command, operand, packet = stepMachine(app.program, app.state, app.expected)
    app.message = app.state[MESSAGE]
    if command:
        app.targetX, app.targetY = 331, 420
        if command == 'READ':
            app.targetX = 146
        elif command == 'SEND':
            app.targetX = 522
        elif command in MEMORY_OPS:
            app.targetX, app.targetY = 84 + operand * 70, 470
        app.packet = packet
        app.anim = 4 if app.fast else 15
    if app.state[STATUS] in ['error', 'success']:
        app.running = False
        if app.state[STATUS] == 'success':
            app.message = 'Sample passed! VERIFY ALL measures your complete solution.'
    if app.state[PC] < len(app.program):
        if app.state[PC] < app.scroll or app.state[PC] >= app.scroll + VISIBLE:
            app.scroll = max(0, app.state[PC] - VISIBLE // 2)


def toggleRun(app):
    if not app.program:
        app.message = 'Drag READ from the toolbox into the program.'
    elif app.state[STATUS] in ['error', 'success']:
        app.message = 'RESET to replay, or VERIFY ALL to measure the solution.'
    else:
        app.running = not app.running


def startVerification(app):
    if not app.program:
        app.message = 'Build a program before verifying it.'
        return
    app.running = False
    app.anim = 0
    app.packet = None
    app.verifying = True
    app.verifyCase = 0
    app.verifyTotals = 0
    app.verifyOutputs = 0
    app.verifyState = newMachine(LEVELS[app.level][3][0])
    app.previousSteps = app.bestSteps[app.level]
    app.message = 'Verifying all three queues...'


def verificationFrame(app):
    # Bounded work per frame keeps the interface responsive even for bad loops.
    for i in range(100):
        expected = expectedFor(app.level, LEVELS[app.level][3][app.verifyCase])
        stepMachine(app.program, app.verifyState, expected)
        if app.verifyState[STATUS] == 'error':
            app.verifying = False
            app.certified[app.level] = False
            app.case = app.verifyCase
            app.state = app.verifyState
            app.expected = expected
            app.scroll = max(0, app.state[PC] - VISIBLE // 2)
            app.message = 'Test ' + str(app.case + 1) + ': ' + app.state[MESSAGE]
            return
        if app.verifyState[STATUS] == 'success':
            app.verifyTotals += app.verifyState[STEPS]
            app.verifyOutputs += len(app.verifyState[OUTPUT])
            app.verifyCase += 1
            if app.verifyCase == 3:
                app.verifying = False
                app.certified[app.level] = True
                app.resultSteps = app.verifyTotals
                app.resultSize = len(app.program)
                app.resultRate = 100 * app.verifyOutputs / max(1, app.verifyTotals)
                old = app.bestSteps[app.level]
                if old is None or app.verifyTotals < old:
                    app.bestSteps[app.level] = app.verifyTotals
                oldSize = app.bestSizes[app.level]
                if oldSize is None or len(app.program) < oldSize:
                    app.bestSizes[app.level] = len(app.program)
                app.result = True
                app.message = 'All three queues passed. Performance report ready.'
                return
            app.verifyState = newMachine(LEVELS[app.level][3][app.verifyCase])


def onStep(app):
    app.ticks += 1
    if app.screen != 'game' or app.help or app.result:
        return
    if app.verifying:
        verificationFrame(app)
    elif app.anim > 0:
        app.robotX += (app.targetX - app.robotX) / app.anim
        app.robotY += (app.targetY - app.robotY) / app.anim
        app.anim -= 1
        if app.anim == 0:
            app.packet = None
    elif app.running:
        takeStep(app)
    # Hold a dragged card near a viewport edge to reach off-screen lines.
    if app.dragKind and app.ticks % 5 == 0 and 850 <= app.mouseX <= 1260:
        if app.mouseY < ROW_Y + 18:
            scrollProgram(app, -1)
        elif app.mouseY > ROW_Y + VISIBLE * ROW_H - 18:
            scrollProgram(app, 1)


def inside(x, y, left, top, width, height):
    return left <= x <= left + width and top <= y <= top + height


def rowAt(app, y):
    return app.scroll + int((y - ROW_Y) // ROW_H)


def scrollProgram(app, amount):
    app.scroll = max(0, min(max(0, len(app.program) - VISIBLE + 1), app.scroll + amount))


def openAnswers(app, level):
    app.answerLevel = level
    app.answerScroll = 0
    app.running = False
    app.verifying = False
    app.screen = 'answers'


def loadAnswer(app):
    level = app.answerLevel
    openMission(app, level)
    app.program.clear()
    base = app.nextId
    for command, operand, identity in SOLUTIONS[level]:
        if command in JUMPS:
            operand += base
        app.program.append([command, operand, identity + base])
    app.nextId += len(SOLUTIONS[level])
    changed(app)
    app.message = 'Reference loaded. STEP through it to understand each instruction.'


def onMousePress(app, x, y):
    x, y = x / SCALE, y / SCALE
    app.mouseX, app.mouseY = x, y
    app.pressX, app.pressY = x, y
    if app.help:
        app.help = False
        return
    if app.result:
        if inside(x, y, 368, 570, 235, 46):
            app.result = False
        elif inside(x, y, 627, 570, 285, 46):
            if app.level < len(LEVELS) - 1:
                openMission(app, app.level + 1)
            else:
                app.result = False
                app.screen = 'map'
        return
    if app.screen == 'answers':
        if inside(x, y, 28, 25, 106, 36):
            app.screen = 'map'
        elif inside(x, y, 47, 175, 90, 37):
            app.answerLevel = max(0, app.answerLevel - 1)
            app.answerScroll = 0
        elif inside(x, y, 149, 175, 90, 37):
            app.answerLevel = min(len(LEVELS) - 1, app.answerLevel + 1)
            app.answerScroll = 0
        elif inside(x, y, 1120, 173, 46, 32):
            app.answerScroll = max(0, app.answerScroll - 10)
        elif inside(x, y, 1178, 173, 46, 32):
            app.answerScroll = min(max(0, len(SOLUTIONS[app.answerLevel]) - 20), app.answerScroll + 10)
        elif inside(x, y, 48, 636, 224, 47):
            loadAnswer(app)
        elif inside(x, y, 289, 636, 240, 47):
            openMission(app, app.answerLevel)
        return
    if app.screen == 'map':
        if inside(x, y, 1055, 34, 155, 37):
            openAnswers(app, app.level)
            return
        for i in range(len(LEVELS)):
            nx, ny = ROUTE[i]
            if (x - nx) ** 2 + (y - ny) ** 2 <= 32 ** 2 or inside(x, y, nx - 100, ny + 34, 200, 46):
                openMission(app, i)
                return
        return
    if inside(x, y, 27, 25, 104, 36):
        app.running = False
        app.verifying = False
        app.dragKind = ''
        app.screen = 'map'
        return
    if inside(x, y, 1055, 26, 100, 34):
        openAnswers(app, app.level)
        return
    if inside(x, y, 1169, 26, 84, 34):
        app.help = True
        app.running = False
        return
    if app.verifying:
        if inside(x, y, 262, 753, 102, 42):
            resetRun(app)
        return
    for i in range(3):
        if inside(x, y, 430 + i * 74, 76, 65, 27):
            app.case = i
            resetRun(app)
            return
    if inside(x, y, 30, 753, 104, 42):
        toggleRun(app)
        return
    if inside(x, y, 146, 753, 104, 42):
        app.running = False
        takeStep(app)
        return
    if inside(x, y, 262, 753, 102, 42):
        resetRun(app)
        return
    if inside(x, y, 376, 753, 104, 42):
        app.fast = not app.fast
        return
    if inside(x, y, 492, 753, 166, 42):
        startVerification(app)
        return
    if inside(x, y, 700, 751, 140, 43):
        app.hint = not app.hint
        return
    if inside(x, y, 1170, 139, 33, 28):
        scrollProgram(app, -5)
        return
    if inside(x, y, 1210, 139, 33, 28):
        scrollProgram(app, 5)
        return
    if inside(x, y, 867, 752, 125, 40):
        deleteCard(app)
        return
    if not canEdit(app):
        app.message = 'Pause and finish the current movement before editing.'
        return
    for i in range(8):
        if inside(x, y, 700 + (i % 4) * 36, 669 + (i // 4) * 34, 30, 27):
            changeMemory(app, i)
            return
        if inside(x, y, 55 + i * 70, 520, 58, 41):
            changeMemory(app, i)
            return
    for i in range(len(COMMANDS)):
        if inside(x, y, 700, 179 + i * 49, 142, 40):
            app.dragKind = 'new'
            app.dragCommand = COMMANDS[i]
            app.dragIndex = -1
            return
    if inside(x, y, 861, ROW_Y, 390, VISIBLE * ROW_H):
        row = rowAt(app, y)
        if 0 <= row < len(app.program):
            app.selected = row
            app.dragIndex = row
            if app.program[row][0] in JUMPS and x >= 1100:
                app.dragKind = 'wire'
            elif x < 1135:
                app.dragKind = 'move'


def onMouseDrag(app, x, y):
    x, y = x / SCALE, y / SCALE
    app.mouseX, app.mouseY = x, y


def onMouseRelease(app, x, y):
    x, y = x / SCALE, y / SCALE
    kind = app.dragKind
    app.dragKind = ''
    if not kind or app.screen != 'game' or not canEdit(app):
        return
    if kind == 'move' and inside(x, y, 867, 752, 125, 40):
        deleteCard(app)
        return
    if not inside(x, y, 861, ROW_Y, 390, VISIBLE * ROW_H):
        return
    row = rowAt(app, y)
    if kind == 'wire':
        if row < len(app.program):
            app.program[app.dragIndex][1] = app.program[row][2]
            changed(app)
            app.message = 'Jump connected to line ' + str(row + 1) + '.'
    elif kind == 'new':
        insertCard(app, min(len(app.program), row), app.dragCommand)
    elif kind == 'move':
        if abs(x - app.pressX) + abs(y - app.pressY) > 7:
            # Drop in the upper/lower half of a row to insert before/after it.
            if (y - ROW_Y) % ROW_H > ROW_H / 2:
                row += 1
            moveCard(app, app.dragIndex, min(len(app.program), row))


def onKeyPress(app, key):
    if key == 'escape':
        app.help = False
        app.result = False
        app.dragKind = ''
        app.running = False
        return
    if app.screen == 'answers':
        if key in ['up', 'down']:
            amount = -1 if key == 'up' else 1
            app.answerScroll = max(0, min(max(0, len(SOLUTIONS[app.answerLevel]) - 20), app.answerScroll + amount))
        return
    if app.screen != 'game' or app.help or app.result:
        return
    if key == 'h':
        app.help = True
        app.running = False
    elif key == 'r':
        resetRun(app)
    elif not app.verifying:
        if key == 'space':
            toggleRun(app)
        elif key == 's':
            app.running = False
            takeStep(app)
        elif key == 'v':
            startVerification(app)
        elif key in ['backspace', 'delete']:
            deleteCard(app)
        elif key in ['up', 'down']:
            scrollProgram(app, -1 if key == 'up' else 1)
        elif key in ['0', '1', '2', '3', '4', '5', '6', '7'] and canEdit(app):
            changeMemory(app, int(key))


# VIEW: every function below reads the model without changing it.
def text(value, x, y, size=13, color=INK, bold=False, align='left'):
    drawLabel(value, (x) * SCALE, (y) * SCALE, size=(size) * SCALE, fill=color, bold=bold, align=align, font='arial')


def panel(x, y, w, h, fill=PAPER, border=None):
    drawRect((x) * SCALE, (y + 4) * SCALE, (w) * SCALE, (h) * SCALE, fill=INK, opacity=8)
    drawRect((x) * SCALE, (y) * SCALE, (w) * SCALE, (h) * SCALE, fill=fill, border=border)


def button(title, x, y, w, h, active=False):
    panel(x, y, w, h, TEAL if active else WHITE)
    text(title, x + w / 2, y + h / 2, 12, WHITE if active else INK, True, 'center')


def planet(x, y, radius):
    drawCircle((x) * SCALE, (y) * SCALE, (radius + 12) * SCALE, fill=rgb(173, 214, 207), opacity=10)
    drawCircle((x) * SCALE, (y) * SCALE, (radius) * SCALE, fill=rgb(237, 179, 131))
    drawCircle((x - radius * .18) * SCALE, (y - radius * .15) * SCALE, (radius * .81) * SCALE, fill=rgb(249, 204, 155))
    drawOval((x) * SCALE, (y + radius * .12) * SCALE, (radius * 3.1) * SCALE, (radius * .56) * SCALE,
             fill=None, border=rgb(255, 225, 176), borderWidth=(6) * SCALE, rotateAngle=-25)
    drawCircle((x + radius * .28) * SCALE, (y - radius * .25) * SCALE, (radius * .12) * SCALE,
               fill=rgb(226, 157, 119), opacity=65)


ROUTE = [(105, 590), (228, 449), (125, 300), (299, 225),
         (464, 327), (558, 495), (706, 635), (856, 483),
         (790, 292), (992, 223), (1133, 414)]


def drawMap(app):
    drawRect((0) * SCALE, (0) * SCALE, (1280) * SCALE, (820) * SCALE, fill=CREAM)
    panel(28, 25, 1224, 137, rgb(31, 67, 79))
    text('ORBIT', 56, 78, 46, WHITE, True)
    text('THE QUIET STATION', 59, 120, 15, rgb(166, 216, 207), True)
    text('Eleven missions. One winding journey.', 371, 75, 20, WHITE)
    text(str(app.certified.count(True)) + ' / 11 systems restored', 372, 111, 13, rgb(166, 216, 207))
    button('ANSWER ARCHIVE', 1055, 34, 155, 37)
    text('Choose a station on the orbital route.', 46, 190, 12, MUTED)
    # A route of circular stations, with dotted paths instead of a card grid.
    for i in range(len(ROUTE) - 1):
        x1, y1 = ROUTE[i]
        x2, y2 = ROUTE[i + 1]
        for dot in range(1, 15):
            t = dot / 15
            drawCircle((x1 + (x2 - x1) * t) * SCALE, (y1 + (y2 - y1) * t) * SCALE, (2) * SCALE,
                       fill=TEAL, opacity=28)
    drawCircle((628) * SCALE, (295) * SCALE, (66) * SCALE, fill=rgb(213, 215, 194), opacity=35)
    drawOval((628) * SCALE, (295) * SCALE, (173) * SCALE, (34) * SCALE, fill=None, border=rgb(194, 201, 180),
             borderWidth=(3) * SCALE, rotateAngle=-24)
    text('DEEP SPACE', 619, 300, 10, MUTED, align='center')
    for i in range(len(LEVELS)):
        x, y = ROUTE[i]
        color = TEAL if i < 3 else BLUE if i < 8 else CORAL
        drawCircle((x) * SCALE, (y + 5) * SCALE, (31) * SCALE, fill=INK, opacity=9)
        drawCircle((x) * SCALE, (y) * SCALE, (30) * SCALE, fill=WHITE, border=color, borderWidth=(2) * SCALE)
        drawCircle((x) * SCALE, (y) * SCALE, (24) * SCALE, fill=color if app.certified[i] else PAPER)
        if app.certified[i]:
            drawStar((x) * SCALE, (y) * SCALE, (13) * SCALE, 5, fill=WHITE)
        else:
            text(str(i + 1).zfill(2), x, y, 20, color, True, 'center')
        text(LEVELS[i][0], x, y + 47, 13, INK, True, 'center')
        difficulty = 'FOUNDATIONS' if i < 3 else 'ENGINEERING' if i < 8 else 'EXPERT'
        text(difficulty, x, y + 65, 9, color, align='center')
    text('01-03 / Learn the language', 46, 758, 13, TEAL, True)
    text('04-08 / Build the machinery', 464, 758, 13, BLUE, True)
    text('09-11 / Master the system', 891, 758, 13, CORAL, True)
    text('Select a circle or mission title. Programs and bests last for this session.', 46, 792, 12, MUTED)


def wrapped(message, x, y, width=65, size=14, color=INK):
    line = ''
    for word in message.split():
        if len(line) + len(word) > width:
            text(line, x, y, size, color)
            y += 23
            line = ''
        line += word + ' '
    if line:
        text(line, x, y, size, color)


def drawAnswers(app):
    level = app.answerLevel
    solution = SOLUTIONS[level]
    drawRect((0) * SCALE, (0) * SCALE, (1280) * SCALE, (820) * SCALE, fill=CREAM)
    button('< MISSIONS', 28, 25, 106, 36)
    text('ANSWER ARCHIVE', 158, 45, 22, INK, True)
    text('Read it. Trace it. Improve it.', 848, 45, 13, TEAL)
    text(str(level + 1).zfill(2) + ' / ' + LEVELS[level][0], 47, 116, 28, INK, True)
    button('< PREV', 47, 175, 90, 37)
    button('NEXT >', 149, 175, 90, 37)
    text(str(level + 1) + ' of 11', 266, 194, 12, MUTED)
    text('THE IDEA', 48, 251, 11, TEAL, True)
    for i in range(3):
        wrapped(EXPLANATIONS[level][i], 48, 282 + i * 67, 62, 14)
    panel(47, 489, 482, 108, WHITE)
    text('MEASURED REFERENCE', 65, 513, 11, TEAL, True)
    text(str(LEVELS[level][4]) + ' cards', 66, 553, 25, INK, True)
    average = int(LEVELS[level][5] / 3 * 10 + .5) / 10
    text(str(average) + ' avg steps', 258, 553, 25, INK, True)
    button('LOAD THIS SOLUTION', 48, 636, 224, 47, True)
    button('RETURN TO MY PROGRAM', 289, 636, 240, 47)
    wrapped("Loading replaces this mission's current program. Viewing an answer does not change it.",
            48, 711, 68, 12, MUTED)
    wrapped('These are tested, efficient reference solutions. Global optimality is not proven; you may beat them.',
            48, 759, 68, 12, TEAL)
    panel(630, 158, 623, 624, WHITE)
    text('REFERENCE PROGRAM', 650, 188, 13, INK, True)
    button('^', 1120, 173, 46, 32)
    button('v', 1178, 173, 46, 32)
    for i in range(app.answerScroll, min(len(solution), app.answerScroll + 20)):
        command, operand, identity = solution[i]
        y = 227 + (i - app.answerScroll) * 25
        drawRect((648) * SCALE, (y) * SCALE, (582) * SCALE, (22) * SCALE, fill=COLORS[COMMANDS.index(command)], opacity=35)
        text(str(i + 1).zfill(2), 659, y + 11, 11, MUTED)
        text(command, 701, y + 11, 13, INK, True)
        if command in JUMPS:
            text('-> line ' + str(findLine(solution, operand) + 1), 819, y + 11, 13, TEAL)
        elif command in MEMORY_OPS:
            text('memory [' + str(operand) + ']', 819, y + 11, 13, BLUE)
    text('Up/down scrolls. Targets are shown as human-readable line numbers.', 650, 757, 11, MUTED)


def drawDrone(app):
    bob = abs(app.ticks % 60 - 30) / 10 - 1.5
    x, y = app.robotX, app.robotY + bob
    drawOval((x) * SCALE, (y + 51) * SCALE, (98) * SCALE, (20) * SCALE, fill=rgb(49, 71, 73), opacity=25)
    drawPolygon((x - 13) * SCALE, (y + 30) * SCALE, (x) * SCALE, (y + 49 + app.ticks % 6) * SCALE,
                (x + 13) * SCALE, (y + 30) * SCALE, fill=rgb(146, 233, 211), opacity=80)
    drawOval((x - 38) * SCALE, (y + 10) * SCALE, (17) * SCALE, (32) * SCALE, fill=rgb(56, 101, 108))
    drawOval((x + 38) * SCALE, (y + 10) * SCALE, (17) * SCALE, (32) * SCALE, fill=rgb(56, 101, 108))
    drawOval((x) * SCALE, (y - 16) * SCALE, (73) * SCALE, (57) * SCALE, fill=rgb(255, 243, 212), border=rgb(60, 91, 95), borderWidth=(2) * SCALE)
    drawRect((x - 36) * SCALE, (y - 18) * SCALE, (72) * SCALE, (48) * SCALE, fill=rgb(255, 243, 212))
    drawOval((x) * SCALE, (y + 26) * SCALE, (72) * SCALE, (29) * SCALE, fill=rgb(218, 208, 179))
    drawRect((x - 28) * SCALE, (y - 15) * SCALE, (56) * SCALE, (31) * SCALE, fill=rgb(34, 67, 78))
    drawLine((x - 22) * SCALE, (y - 11) * SCALE, (x + 21) * SCALE, (y - 11) * SCALE, fill=rgb(73, 109, 119))
    for eye in [-13, 13]:
        if app.state[STATUS] == 'error':
            drawLine((x + eye - 4) * SCALE, (y - 4) * SCALE, (x + eye + 4) * SCALE, (y + 4) * SCALE, fill=rgb(255, 160, 132), lineWidth=(3) * SCALE)
            drawLine((x + eye - 4) * SCALE, (y + 4) * SCALE, (x + eye + 4) * SCALE, (y - 4) * SCALE, fill=rgb(255, 160, 132), lineWidth=(3) * SCALE)
        elif app.ticks % 120 < 7:
            drawLine((x + eye - 4) * SCALE, (y + 2) * SCALE, (x + eye + 4) * SCALE, (y + 2) * SCALE, fill=rgb(153, 237, 209), lineWidth=(3) * SCALE)
        else:
            drawOval((x + eye) * SCALE, (y) * SCALE, (8) * SCALE, (12) * SCALE, fill=rgb(153, 237, 209))
    drawLine((x + 7) * SCALE, (y - 39) * SCALE, (x + 15) * SCALE, (y - 53) * SCALE, fill=WHITE, lineWidth=(3) * SCALE)
    drawCircle((x + 16) * SCALE, (y - 56) * SCALE, (6) * SCALE, fill=GOLD)
    drawCircle((x) * SCALE, (y + 29) * SCALE, (5) * SCALE, fill=CORAL)
    if app.packet is not None:
        panel(x + 45, y - 16, 44, 36, rgb(250, 207, 148))
        text(str(app.packet), x + 67, y + 2, 17, INK, True, 'center')


def drawStation(app):
    # The large observation window is never covered by queues or editor controls.
    panel(26, 155, 636, 424, rgb(215, 210, 189))
    drawRect((43) * SCALE, (170) * SCALE, (602) * SCALE, (240) * SCALE, fill=rgb(28, 65, 79))
    drawRect((54) * SCALE, (180) * SCALE, (580) * SCALE, (219) * SCALE, fill=rgb(40, 87, 101))
    for i in range(34):
        x, y = 66 + (i * 97) % 556, 193 + (i * 43) % 185
        drawCircle((x) * SCALE, (y) * SCALE, (1 if i % 4 else 2) * SCALE, fill=WHITE, opacity=40 + (i % 3) * 15)
    drawCircle((200) * SCALE, (277) * SCALE, (80) * SCALE, fill=rgb(70, 130, 136), opacity=25)
    planet(464, 273, 66)
    drawCircle((553) * SCALE, (211) * SCALE, (10) * SCALE, fill=rgb(165, 214, 197))
    drawPolygon((56) * SCALE, (364) * SCALE, (159) * SCALE, (326) * SCALE, (255) * SCALE, (368) * SCALE, (354) * SCALE, (344) * SCALE, (444) * SCALE, (379) * SCALE, (634) * SCALE, (337) * SCALE,
                (634) * SCALE, (399) * SCALE, (56) * SCALE, (399) * SCALE, fill=rgb(40, 71, 84))
    drawLine((344) * SCALE, (180) * SCALE, (344) * SCALE, (399) * SCALE, fill=rgb(143, 173, 169), lineWidth=(7) * SCALE)
    drawLine((57) * SCALE, (191) * SCALE, (327) * SCALE, (191) * SCALE, fill=WHITE, opacity=15, lineWidth=(3) * SCALE)
    # Inset structural beams and warm floor provide depth.
    drawRect((43) * SCALE, (399) * SCALE, (602) * SCALE, (12) * SCALE, fill=rgb(103, 125, 118))
    drawPolygon((43) * SCALE, (411) * SCALE, (645) * SCALE, (411) * SCALE, (645) * SCALE, (507) * SCALE, (43) * SCALE, (507) * SCALE, fill=rgb(194, 184, 150))
    for i in range(9):
        drawLine((74 + i * 64) * SCALE, (411) * SCALE, (max(43, min(645, 37 + i * 80))) * SCALE, (507) * SCALE, fill=rgb(165, 159, 131))
    for y in [435, 469, 504]:
        drawLine((44) * SCALE, (y) * SCALE, (644) * SCALE, (y) * SCALE, fill=rgb(165, 159, 131))
    for x, color in [(138, TEAL), (530, CORAL)]:
        drawOval((x) * SCALE, (465) * SCALE, (122) * SCALE, (37) * SCALE, fill=rgb(95, 115, 105))
        drawOval((x) * SCALE, (455) * SCALE, (122) * SCALE, (37) * SCALE, fill=rgb(224, 222, 192), border=color, borderWidth=(3) * SCALE)
        drawOval((x) * SCALE, (455) * SCALE, (90) * SCALE, (21) * SCALE, fill=None, border=color, opacity=65)
    text('RECEIVE', 138, 488, 10, TEAL, True, 'center')
    text('TRANSMIT', 530, 488, 10, CORAL, True, 'center')
    # Side consoles and an original small plant in the workshop.
    drawRect((64) * SCALE, (336) * SCALE, (77) * SCALE, (63) * SCALE, fill=rgb(76, 107, 111))
    drawRect((70) * SCALE, (342) * SCALE, (64) * SCALE, (34) * SCALE, fill=rgb(27, 60, 72))
    for i in range(4):
        drawLine((78) * SCALE, (350 + i * 6) * SCALE, (105 + (i % 2) * 17) * SCALE, (350 + i * 6) * SCALE, fill=rgb(130, 216, 182))
    drawCircle((82) * SCALE, (387) * SCALE, (3) * SCALE, fill=GOLD)
    drawCircle((98) * SCALE, (387) * SCALE, (3) * SCALE, fill=CORAL)
    drawPolygon((586) * SCALE, (399) * SCALE, (576) * SCALE, (374) * SCALE, (617) * SCALE, (374) * SCALE, (609) * SCALE, (399) * SCALE, fill=rgb(204, 128, 94))
    drawLine((596) * SCALE, (376) * SCALE, (596) * SCALE, (341) * SCALE, fill=rgb(157, 199, 143), lineWidth=(3) * SCALE)
    drawOval((584) * SCALE, (352) * SCALE, (30) * SCALE, (12) * SCALE, fill=rgb(137, 187, 141), rotateAngle=30)
    drawOval((605) * SCALE, (343) * SCALE, (27) * SCALE, (13) * SCALE, fill=rgb(172, 209, 152), rotateAngle=-35)
    drawDrone(app)
    for i in range(8):
        x = 55 + i * 70
        panel(x, 520, 58, 41, rgb(248, 242, 220), TEAL if app.memoryChoice == i else None)
        text(str(i), x + 7, 531, 9, MUTED, True)
        value = app.state[MEMORY][i]
        text('--' if value is None else str(value), x + 31, 545, 15, TEAL, True, 'center')
    text('O-7 / MAINTENANCE UNIT', 72, 208, 10, rgb(174, 215, 207), True)


def queue(values, x, y, color):
    if not values:
        text('empty', x, y + 13, 12, MUTED)
    for i in range(min(len(values), 11)):
        panel(x + i * 41, y, 35, 27, color)
        text(str(values[i]), x + i * 41 + 17, y + 14, 12, INK, True, 'center')
    if len(values) > 11:
        text('+' + str(len(values) - 11), x + 454, y + 14, 11, MUTED)


def drawLiveData(app):
    panel(27, 595, 635, 139, WHITE)
    text('INPUT', 43, 619, 10, TEAL, True)
    queue(app.state[INPUT], 113, 605, COLORS[0])
    text('OUTPUT', 43, 659, 10, CORAL, True)
    queue(app.state[OUTPUT], 113, 645, COLORS[1])
    text('HELD', 43, 704, 10, MUTED, True)
    text('--' if app.state[HELD] is None else str(app.state[HELD]), 85, 704, 16, TEAL, True)
    text('STEPS  ' + str(app.state[STEPS]), 175, 704, 12, INK, True)
    text('CODE  ' + str(len(app.program)), 310, 704, 12, INK, True)
    status = 'CHECKING ' + str(app.verifyCase + 1) + '/3' if app.verifying else app.state[STATUS].upper()
    text(status, 641, 704, 11, TEAL if app.state[STATUS] != 'error' else CORAL, True, 'right')


def drawCard(command, operand, x, y, width, selected=False):
    color = COLORS[COMMANDS.index(command)]
    panel(x, y, width, 28, color, TEAL if selected else None)
    text('::', x + 10, y + 14, 12, INK)
    text(command, x + 29, y + 14, 13, INK, True)
    if command in MEMORY_OPS:
        text('[' + str(operand) + ']', x + width - 17, y + 14, 13, INK, True, 'right')
    if command in JUMPS:
        drawCircle((x + width - 12) * SCALE, (y + 14) * SCALE, (6) * SCALE, fill=WHITE, border=BLUE, borderWidth=(2) * SCALE)


def drawWires(app):
    for i in range(app.scroll, min(len(app.program), app.scroll + VISIBLE)):
        command, operand, identity = app.program[i]
        if command not in JUMPS:
            continue
        sy = ROW_Y + (i - app.scroll) * ROW_H + 14
        target = findLine(app.program, operand)
        if target == -1:
            text('link', 1170, sy, 10, CORAL)
            continue
        ty = ROW_Y + (target - app.scroll) * ROW_H + 14
        ty = max(ROW_Y + 3, min(ROW_Y + VISIBLE * ROW_H - 3, ty))
        lane = 1160 + (i % 5) * 15
        color = TEAL if i == app.selected else BLUE
        opacity = 95 if i == app.selected else 42
        drawLine((1128) * SCALE, (sy) * SCALE, (lane) * SCALE, (sy) * SCALE, fill=color, opacity=opacity, lineWidth=(2) * SCALE)
        if abs(sy - ty) < 1:
            drawLine((lane) * SCALE, (sy) * SCALE, (lane) * SCALE, (sy + 10) * SCALE, fill=color, lineWidth=(2) * SCALE)
            drawLine((lane) * SCALE, (sy + 10) * SCALE, (1140) * SCALE, (sy + 10) * SCALE, fill=color, lineWidth=(2) * SCALE)
            drawLine((1140) * SCALE, (sy + 10) * SCALE, (1131) * SCALE, (sy) * SCALE, fill=color, arrowEnd=True, lineWidth=(2) * SCALE)
        else:
            drawLine((lane) * SCALE, (sy) * SCALE, (lane) * SCALE, (ty) * SCALE, fill=color, opacity=opacity, lineWidth=(2) * SCALE)
            drawLine((lane) * SCALE, (ty) * SCALE, (1131) * SCALE, (ty) * SCALE, fill=color, opacity=opacity, arrowEnd=True, lineWidth=(2) * SCALE)
        if target < app.scroll or target >= app.scroll + VISIBLE:
            text(str(target + 1), lane, ty, 9, color, True, 'center')
    if app.dragKind == 'wire':
        sy = ROW_Y + (app.dragIndex - app.scroll) * ROW_H + 14
        sy = max(ROW_Y, min(ROW_Y + VISIBLE * ROW_H, sy))
        drawLine((1128) * SCALE, (sy) * SCALE, (app.mouseX) * SCALE, (app.mouseY) * SCALE, fill=TEAL, lineWidth=(3) * SCALE, arrowEnd=True)


def drawEditor(app):
    text('TOOLBOX', 700, 153, 11, MUTED, True)
    for i in range(9):
        y = 179 + i * 49
        panel(700, y, 142, 40, COLORS[i])
        text('::', 708, y + 14, 12, INK)
        text(COMMANDS[i], 729, y + 13, 13, INK, True)
        text(NOTES[i], 729, y + 29, 9, INK)
    text('MEMORY ADDRESS', 700, 645, 10, MUTED, True)
    for i in range(8):
        button(str(i), 700 + (i % 4) * 36, 669 + (i // 4) * 34, 30, 27, app.memoryChoice == i)
    panel(860, 117, 394, 616, WHITE)
    text('YOUR PROGRAM', 878, 146, 14, INK, True)
    text(str(len(app.program)) + ' / 64', 1101, 146, 11, MUTED)
    button('^', 1170, 139, 33, 28)
    button('v', 1210, 139, 33, 28)
    for i in range(VISIBLE):
        row = app.scroll + i
        y = ROW_Y + i * ROW_H
        text(str(row + 1).zfill(2), 870, y + 14, 10, MUTED)
        if row < len(app.program):
            command, operand, identity = app.program[row]
            drawCard(command, operand, 891, y, 249, row == app.selected)
            if row == app.lastLine:
                drawRect((885) * SCALE, (y) * SCALE, (3) * SCALE, (28) * SCALE, fill=GOLD)
            if row == app.state[PC]:
                drawPolygon((866) * SCALE, (y + 8) * SCALE, (873) * SCALE, (y + 14) * SCALE, (866) * SCALE, (y + 20) * SCALE, fill=TEAL)
        else:
            drawLine((894) * SCALE, (y + 28) * SCALE, (1138) * SCALE, (y + 28) * SCALE, fill=CREAM)
    if not app.program:
        text('Drag your first card here', 1015, 211, 14, MUTED, align='center')
        text('Start with READ', 1015, 238, 11, TEAL, align='center')
    drawWires(app)
    text('Drag dots to connect jumps. Up/down to scroll.', 878, 716, 10, MUTED)
    if app.dragKind in ['new', 'move']:
        if inside(app.mouseX, app.mouseY, 861, ROW_Y, 390, VISIBLE * ROW_H):
            row = min(len(app.program), rowAt(app, app.mouseY))
            iy = ROW_Y + (row - app.scroll) * ROW_H
            drawLine((890) * SCALE, (iy - 3) * SCALE, (1140) * SCALE, (iy - 3) * SCALE, fill=TEAL, lineWidth=(3) * SCALE)
        command = app.dragCommand
        arg = app.memoryChoice
        if app.dragKind == 'move':
            command, arg, identity = app.program[app.dragIndex]
        drawCard(command, arg, app.mouseX - 65, app.mouseY - 14, 180, True)


def drawHelp():
    drawRect((0) * SCALE, (0) * SCALE, (1280) * SCALE, (820) * SCALE, fill=INK, opacity=65)
    panel(245, 115, 790, 590, PAPER)
    text('A small language. A lot of possibilities.', 281, 161, 25, INK, True)
    lines = ['Drag a TOOLBOX card into YOUR PROGRAM. Drop between cards to insert.',
             'Drag an existing card to reorder it, or onto DELETE to remove it.',
             'Drag a JUMP / ZERO / NEG dot to the row it should jump to.',
             'Connections follow cards when reordered. Deleted targets must be reconnected.',
             'For memory commands: select a card, then click an address or press 0-7.',
             'Cells start as: [0, 1, 3, empty, empty, empty, empty, empty]. All are writable.',
             'READ replaces the hand. SEND empties it. STORE and LOAD copy values.',
             'ZERO tests for 0; NEG tests for a negative value. Both need a held value.',
             'Empty READ ends the run. All input must be consumed; output must match.',
             'RUN/Space   STEP/S   RESET/R   VERIFY ALL/V   HELP/H   Esc closes overlays.',
             'Up/down buttons or keys scroll. Hold a drag at an edge to auto-scroll.',
             'VERIFY ALL runs 3 queues and reports animation-independent instruction cost.',
             'Best scores are session-only. They may come from different program versions.',
             '64 instructions maximum. Each test has a 5,000-instruction safety limit.',
             'Click anywhere to return.']
    for i in range(len(lines)):
        text(lines[i], 281, 216 + i * 30, 12, TEAL if i == 14 else INK)


def drawResults(app):
    drawRect((0) * SCALE, (0) * SCALE, (1280) * SCALE, (820) * SCALE, fill=INK, opacity=65)
    panel(306, 162, 668, 483, PAPER)
    drawCircle((640) * SCALE, (204) * SCALE, (25) * SCALE, fill=GOLD)
    drawStar((640) * SCALE, (204) * SCALE, (14) * SCALE, 5, fill=WHITE)
    text('SYSTEM RESTORED', 640, 254, 29, TEAL, True, 'center')
    text(LEVELS[app.level][0] + ' / all 3 queues passed', 640, 287, 14, MUTED, align='center')
    labels = ['CODE SIZE', 'AVG STEPS / TEST', 'PACKETS / 100 STEPS']
    values = [str(app.resultSize), str(int(app.resultSteps / 3 * 10 + 0.5) / 10), str(int(app.resultRate * 10 + 0.5) / 10)]
    for i in range(3):
        x = 342 + i * 203
        panel(x, 321, 189, 105, WHITE)
        text(labels[i], x + 94, 344, 10, MUTED, True, 'center')
        text(values[i], x + 94, 385, 31, TEAL, True, 'center')
    targetSize, targetSteps = LEVELS[app.level][4:6]
    text('REFERENCE  ' + str(targetSize) + ' cards / ' + str(int(targetSteps / 3 * 10 + 0.5) / 10) + ' avg steps',
         367, 456, 13, INK, True)
    text('SESSION BEST  ' + str(app.bestSizes[app.level]) + ' cards / ' +
         str(int(app.bestSteps[app.level] / 3 * 10 + 0.5) / 10) + ' avg steps', 367, 484, 13, INK)
    previous = app.previousSteps
    message = 'First measured solution. Try fewer instructions or a shorter path.'
    if previous is not None:
        saved = previous - app.resultSteps
        message = str(abs(saved)) + (' fewer total steps than your previous best.' if saved > 0 else
                                     ' more total steps than your best.' if saved < 0 else ' step change from your best.')
    text(message, 367, 514, 12, TEAL)
    text('Reference scores are verified examples, not proven optimal scores.', 367, 540, 11, MUTED)
    button('KEEP OPTIMIZING', 368, 570, 235, 46)
    button('NEXT MISSION' if app.level < len(LEVELS) - 1 else 'MISSION MAP', 627, 570, 285, 46, True)


def redrawAll(app):
    if app.screen == 'map':
        drawMap(app)
        return
    if app.screen == 'answers':
        drawAnswers(app)
        return
    drawRect((0) * SCALE, (0) * SCALE, (1280) * SCALE, (820) * SCALE, fill=CREAM)
    button('< MISSIONS', 27, 25, 104, 36)
    text('ORBIT', 153, 43, 27, INK, True)
    text('THE QUIET STATION', 250, 45, 11, TEAL, True)
    text('MISSION ' + str(app.level + 1).zfill(2) + ' / 11', 868, 43, 11, TEAL, True)
    button('ANSWERS', 1055, 26, 100, 34)
    button('HELP', 1169, 26, 84, 34)
    text(LEVELS[app.level][0], 28, 94, 26, INK, True)
    text(LEVELS[app.level][1], 28, 119, 12, INK)
    # Long objectives sit above the scene; sample buttons occupy a separate strip.
    for i in range(3):
        button('TEST ' + str(i + 1), 430 + i * 74, 76, 65, 27, app.case == i)
    drawStation(app)
    drawLiveData(app)
    drawEditor(app)
    button('PAUSE' if app.running else 'RUN', 30, 753, 104, 42, True)
    button('STEP', 146, 753, 104, 42)
    button('RESET', 262, 753, 102, 42)
    button('FAST' if app.fast else 'SLOW', 376, 753, 104, 42)
    button('VERIFY ALL', 492, 753, 166, 42, True)
    button('HINT', 700, 751, 140, 43)
    button('DELETE', 867, 752, 125, 40)
    text('Drag a card here to remove it', 1007, 772, 11, MUTED)
    message = LEVELS[app.level][2] if app.hint else app.message
    text(message, 30, 809, 11, CORAL if app.state[STATUS] == 'error' else TEAL)
    if app.help:
        drawHelp()
    if app.result:
        drawResults(app)


def main():
    runApp(width=1152, height=738)


if __name__ == '__main__':
    main()
