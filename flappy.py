from itertools import cycle # 반복 가능하게, 예를 들면 새의 날갯짓
import random
import time # 시간 측정을 위해 사용(승훈)
import sys # 게임 종료 시킬 때 사용
import pygame
from pygame.locals import * # pygame 사용 시 입력 및 이벤트 관리



FPS = 30 # 게임의 프레임 설정
SCREENWIDTH  = 288 # 화면 너비
SCREENHEIGHT = 512 # 화면 높
PIPEGAPSIZE  = 100 # 파이프 사이 간격
BASEY        = SCREENHEIGHT * 0.79 # 바닥의 높이
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# 난이도에 따라 파이프의 수평 간격 조절 (준영)
EASY_PIPE_SPACING = 50
HARD_PIPE_SPACING = 0
pipeSpacing = EASY_PIPE_SPACING # 초기값을 easy로 설정

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range


def main():
    global SCREEN, FPSCLOCK, startTime      #시작시간 측정을 위한 전역변수 선언 (승훈)
    pygame.init() # Pygame 라이브러리 초기화
    FPSCLOCK = pygame.time.Clock() # Pygame 시계 객체, 프레임 속도를 제어
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) # Pygame 화면 객체, 창의 픽셀 크기 정의
    pygame.display.set_caption('Flappy Bird') # 게임 창의 상단에 표시될 제목
    

    # numbers sprites for score display, convert_alpha()를 사용하여 이미지 객체로 변환, 투명도 관리
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()
    #별모양 아이템 이미지 추가함(기영)
    item_image = pygame.image.load('assets/sprites/star.png').convert_alpha()
    item_size = (item_image.get_width() // 8, item_image.get_height() // 8)  # 이미지 크기 조절
    IMAGES['item'] = pygame.transform.scale(item_image, item_size)
    #생명모양 하트 이미지 추가(영섭)
    IMAGES['life'] = pygame.image.load('assets/sprites/life.png').convert_alpha()
    IMAGES['modilife'] = pygame.transform.scale(IMAGES['life'], (20, 20)) 
    #콜론 이미지 추가 (승훈)
    colon_image = pygame.image.load('assets/sprites/colon.png').convert_alpha()
    colon_size = (colon_image.get_width() // 2, colon_image.get_height() // 3.5)
    IMAGES['colon'] = pygame.transform.scale(colon_image, colon_size)

    # sounds, 윈도우인경우 wav, 그 외엔 ogg
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hitmask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )
        
        startTime = time.time()

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation(): # 게임 시작 전 환영 화면
    """Shows welcome screen animation of flappy bird"""
    global pipeSpacing
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1]) # 새 날갯짓 순환
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    # 새 시작 위치
    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    # 메세지 위치
    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12) 

    # 배경 위치 조절
    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen(상하 움직임 제어)
    playerShmVals = {'val': 0, 'dir': 1}

    # pygame.font.init() # 난이도 설정하는 문구 표시 (준영)
    pygame.font.init()
    font = pygame.font.Font(None, 18)
    text = "Press 'E' for Easy mode, 'H' for Hard mode"
    shadow_color = (0, 0, 0)  # 검정색 그림자 생성
    text_color = (255, 255, 255)  # 흰색 텍스트 설정
    shadow_offset = 2  # 그림자의 오프셋

    # 그림자 텍스트 생성, 위치 설정
    shadow_surface = font.render(text, True, shadow_color)
    shadow_rect = shadow_surface.get_rect(center=(SCREENWIDTH / 2, SCREENHEIGHT * 0.81 + shadow_offset)) #글씨가 잘 안보이면 0.77로 수정 가능

    # 실제 텍스트 생성, 위치 설정
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(SCREENWIDTH / 2, SCREENHEIGHT * 0.81))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN and event.key == K_e: # e key를 누르면 easy mode 로 게임 시작 (준영)
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                pipeSpacing = EASY_PIPE_SPACING
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }
            if event.type == KEYDOWN and event.key == K_h: # h key를 누르면 hard mode로 게임 시작
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                pipeSpacing = HARD_PIPE_SPACING
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # adjust playery, playerIndex, basex, 새의 애니메이션 상태와 위치 업데이트
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites, 화면에 배경, 새등 나타내기
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        # 텍스트의 정보 및 이미지를 게임화면에 나타냄
        # 텍스트 그림자 그리기
        SCREEN.blit(shadow_surface, shadow_rect)
        # 실제 텍스트 그리기
        SCREEN.blit(text_surface, text_rect)

        # 변경된 사항 게임에 반영
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0 #점수, 플레이어 인덱스, 루프 반복자 초기화
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2) + pipeSpacing, 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2) + pipeSpacing, 'y': newPipe2[1]['y']},
    ]

    # 아이템 생성하는 코드, 아이템 생성 확률은 20%(기영)
    item = None
    item_spawn_chance = 0.2

    # 게임 물리 및 환경 설정
    dt = FPSCLOCK.tick(FPS)/1000
    pipeVelX = -128 * dt

    # player velocity, max velocity, downward acceleration, acceleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward acceleration
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9   # players speed on flapping
    playerFlapped = False # True when player flaps
    #목숨 추가, 무적 상태와 시간, 깜빡거림 상태와 빈도 프레임 단위(영섭)
    playerLives         =   3   
    invincible          = False 
    blink_visible       = True                                                                    
    invincible_duration =   30                                                                
    blink_frequency     =   3                                                                    
      

    while True:
        for event in pygame.event.get():# 게임 종료 이벤트
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): # 키 다운 이벤트
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS['wing'].play()

        # check for crash here 충돌 검사
        if not invincible:    #무적이 아닌경우 충돌 무시(영섭)
            crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},        
                               upperPipes, lowerPipes)
            if crashTest[0]:            #충돌 시 (영섭)     
                SOUNDS['hit'].play()    #충돌 소리 발생
                playerLives -= 1        #목숨 감소
                invincible = True       #무적 상태 활성화                              

        else :
            if invincible_duration % blink_frequency == 0:         #무적기간 / 무적빈도 의 값이 0일때만(영섭)
                blink_visible = not blink_visible                  #not blink_visible으로 정의함으로써 true일땐 flase , false일땐 true로 변하여 밑의 조건문의 조건에 걸려서 깜빡거리도록함

            invincible_duration -= 1                               #프레임마다 while문이 한번 씩 돌고 이때마다 1씩 감소
            
            if invincible_duration <= 0:                           #만약 남은 무적시간이 0보다 작다면 
                invincible = False                                 #설정 값들 초기화(무적 해제, 무적시간 초기화, 깜빡거림 초기화)
                invincible_duration = 30
                blink_visible = True

        if playerLives == 0:    #목숨이 0개라면 종료(영섭)
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # 아이템 충돌 확인 함수 추가(기영)
        if item and checkItemCollision({'x': playerx, 'y': playery, 'index': playerIndex}, item):
            score += 1
            SOUNDS['point'].play()
            item = None

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2 # 캐릭터의 중앙 위치 계산
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2 # 파이프의 중앙 위치 계산
            if pipeMidPos < playerMidPos and not pipe.get('scored', False): # 캐릭터가 파이프의 중심을 지났는지 체크, 해당 파이프를 통과했을때 점수를 계산했는지 체크.
                score += 1 #위 조건을 모두 만족할때 점수를 1 올림
                pipe['scored'] = True  # 점수가 계산되면 True로 설정, 해당 파이프에 대해 점수가 계산되는 것 방지
                SOUNDS['point'].play()
                if random.random() < item_spawn_chance: #확률 로직 추가(기영)
                    item = getRandomItem(lowerPipes, upperPipes, playerx)
 
        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player, 새의 각도 조절
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement, 새의 움직임 조절
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left, 파이프 이동
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen, 파이프 생성
        if 0 < len(upperPipes) and upperPipes[-1]['x'] < SCREENWIDTH - (SCREENWIDTH / 2 + pipeSpacing): # 파이프 개수에 상관 없이 마지막 파이프가 화면 중간을 넘어설때 새 파이프 추가
            newPipe = getRandomPipe()
            newPipeX = upperPipes[-1]['x'] + SCREENWIDTH / 2 + pipeSpacing
            upperPipes.append({'x': newPipeX, 'y': newPipe[0]['y'], 'scored': False})  # 새 파이프에 scored : False 속성 추가. 캐릭터가 해당 파이프를 지나게 될때 점수를 체크 하고 True로 변환
            lowerPipes.append({'x': newPipeX, 'y': newPipe[1]['y']})

        # remove first pipe if its out of the screen, 파이프 제거
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites. 배경 표시
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        # Player rotation has a threshold, 회전 표시
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        #blink_visible 상태라면 이미지가 나타나지않도록 하는 조건문(영섭)
        if blink_visible : 
            playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
            SCREEN.blit(playerSurface, (playerx, playery))

        # 아이템 그리기 추가(기영)
        if item:
            item['x'] += pipeVelX
            if item['x'] < -IMAGES['item'].get_width():
                item = None
            else:
                SCREEN.blit(IMAGES['item'], (item['x'], item['y']))

        #목숨 개수 표시(영섭)
        ShowplayerLives(playerLives)

        # 화면 업데이트 및 프레임 속도 조절
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo): # 게임 오버 화면
    """crashes the player down and shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7
    soundToggle = False             # whlie True에서 die sound를 한 번만 출력하기 위한 토글 변수 생성

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds -> hit
    SOUNDS['hit'].play()

    # 게임 시간 출력
    playTime = time.time() - startTime  #시작부터 게임 오버까지 플레이한 시간을 저장함 (승훈)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:

            # this play die sound / 'die' 출력 부분 수정 if문 (승훈)
            if playerRot <= -30 and soundToggle == False:   #사운드 수정사항, 새의 각도가 -30이하이고 soundToggle이 False일 때
                    SOUNDS['die'].play()
                    soundToggle = True                      #soundToggle은 True상태가 되며 다시 실행되기 전까지는 이 상태를 유지함
            
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playTimecheck(playTime)          #게임 오버시 시간 출력해주는 함수 (승훈)
        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


# 아이템을 생성하는 함수 추가(기영)
def getRandomItem(lowerPipes, upperPipes, playerx):
    """returns a randomly generated item between the pipes"""
    # Choose a random pipe pair
    pipe_idx = random.randint(0, len(lowerPipes) - 1)
    lowerPipe = lowerPipes[pipe_idx]
    upperPipe = upperPipes[pipe_idx]
    
    # Generate an item between the pipes
    itemX = max(lowerPipe['x'], playerx + 50) + 50 # 항상 아이템을 캐릭터보다 앞에, 파이프 사이에 위치
    itemY = random.randint(int(upperPipe['y'] + IMAGES['pipe'][0].get_height() + PIPEGAPSIZE / 2),
                           int(lowerPipe['y'] - PIPEGAPSIZE / 2))  # y좌표는 항상 위 파이프와 아래 파이프 사이에 나오도록 설정
    
    return {'x': itemX, 'y': itemY}

#플레이 시간 출력해주는 함수 (승훈)
def playTimecheck(playTime):                            # 'MM' 'SS'로 출력하기 위해 리스트에 시간값을 다 분해함
    timeArr = [
        int((playTime // 60) // 10), 
        int((playTime // 60) % 10), 
        int((playTime % 60) // 10), 
        int((playTime % 60) % 10)
    ]

    x_offset = SCREENWIDTH // 2 - 75                                    #x위치 최적 75
    y_offset = SCREENHEIGHT // 2 - 20                                   #y위치 최적 20
    
    for coln, seg in enumerate(timeArr):                                #인덱스랑 값을 같이 가져옴
        if coln == 2:
            SCREEN.blit(IMAGES['colon'], (x_offset, y_offset + 3))      #콜론 출력
            x_offset += int(IMAGES['colon'].get_width()) + 10
        
        SCREEN.blit(IMAGES['numbers'][seg], (x_offset, y_offset))
        x_offset += int(IMAGES['numbers'][seg].get_width()) + 10   


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes): # 새와 파이프가 충돌했을 때

    """returns True if player collides with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2): # 픽셀로 봤을 때 두 객체가 겹치는지 확인
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image): #이미지와 겹쳤을 때 충돌
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

#아이템과 캐릭터가 충돌하는지 확인하는 함수 추가(기영)
def checkItemCollision(player, item):
    playerRect = pygame.Rect(player['x'], player['y'], IMAGES['player'][0].get_width(), IMAGES['player'][0].get_height())
    itemRect = pygame.Rect(item['x'], item['y'], IMAGES['item'].get_width(), IMAGES['item'].get_height())
    return playerRect.colliderect(itemRect)

#목숨의 개수를 보여주는 함수 추가(영섭)
def ShowplayerLives(playerLives):      
    for i in range(playerLives):                                                        
        SCREEN.blit(IMAGES['modilife'],(10+i*25,10))   

if __name__ == '__main__':
    main()
