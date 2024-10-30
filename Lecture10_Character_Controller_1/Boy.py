from pico2d import load_image, get_time

from state_machine import (StateMachine, space_down, time_out, right_down, left_down,
                           left_up, right_up, start_event, key_a_down)


class Idle:
    @staticmethod
    def enter(boy, e):
        if left_up(e) or right_down(e):
            boy.face_dir = -1
        elif right_up(e) or left_down(e) or start_event(e):
            boy.face_dir = 1
        if boy.face_dir == 1:
            boy.action = 3
        elif boy.face_dir == -1:
            boy.action = 2
        boy.dir = 0
        boy.frame = 0
        boy.wait_time = get_time()
        print('Boy Idle Enter')

    @staticmethod
    def exit(boy, e):
        print('Boy Idle Exit')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.wait_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class Sleep:
    @staticmethod
    def enter(boy, e):
        boy.face_dir = 0
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                                3.141592 / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100,
                                -3.141592 / 2, '', boy.x + 25, boy.y - 25, 100, 100)

class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            boy.dir, boy.action = 1, 1
            boy.face_dir = 1
        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            boy.dir, boy.action = -1, 0
            boy.face_dir = -1
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class AutoRun:
    @staticmethod
    def enter(boy, e):
        if boy.face_dir == 1:
            boy.action, boy.dir = 1, 1
        elif boy.face_dir == -1:
            boy.action, boy.dir = 0, -1
        boy.frame = 0
        boy.wait_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 10
        if get_time() - boy.wait_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))
        if boy.x > 800 and boy.dir == 1:
            boy.dir = -1
            boy.action = 0
        elif boy.x < 0 and boy.dir == -1:
            boy.dir = 1
            boy.action = 1

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 50, 200, 200)
        else:
            boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 50, 200, 200)

class Boy:
    image = None

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.action = 3
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            # 상태 변환 표기
            {
                Idle : {right_down: Run, left_down: Run, left_up: Run, right_up: Run,
                        time_out: Sleep, space_down: Idle, key_a_down: AutoRun},
                Run : {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, space_down: Run},
                Sleep: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, space_down: Idle},
                AutoRun: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Idle}
            }
        )
        if Boy.image is None:
            Boy.image = load_image('animation_sheet.png')

    def update(self):
        self.state_machine.update()
        self.frame = (self.frame + 1) % 8

    def start(self, state):
        self.cur_state = state
        self.cur_state.enter(self.o, ('START', 0))

    def handle_event(self, event):
        self.state_machine.add_event(
            ('INPUT', event)
        )
        # INPUT : 실제입력이벤트값
        # TIME_OUT : 시간 종료
        # NONE : 없음..? 즉 IDLE상태인듯

    def draw(self):
        self.state_machine.draw()
