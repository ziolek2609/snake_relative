from numpy import argmax
from random import random, randint
import matplotlib.pyplot as plt
from dqn import Dqn
from neural_network import NeuralNetwork
from snake_environment import SnakeEnvironment

# STAŁE PARAMETRY UCZENIA
learningRate = 0.01  # współczynnik uczenia
gamma = 0.9  # parametr dyskontujący do dqn
batchSize = 128  # wielkość wkładu do sieci
epsilon = 1  # prawdopodobieństwo podjęcia losowego ruchu przez snake'a w danej epoce
epsilonMultiplier = 0.999  # zmiana epsilon po każdej grze
minEpsilon = 0.05  # minimalna wartość prawdopodobnieństw ruchu losowego
epochs = 40000  # liczba epok (rozegranych gier)
maxMemory = 15000 # pojemność pamięci
waitTime = 0  # czas pomiędzy przesunięciami węża, gdy == 0, czas przesunięcia zależy od możliwości komputera
nSegments = 4  # ilość segmentów na jednym boku ekranu
vision = 2  # wizja odległoci/obecnosci


# STWORZENIE ŚRODOWISKA, MODELU SIECI ORAZ DQN
env = SnakeEnvironment(waitTime = waitTime, segmentSize = 50, segments = nSegments, vision = vision)
nn = NeuralNetwork(21, 3, learningRate)
model = nn.model
DQN = Dqn(gamma, maxMemory)

# ZMIENNE WYKORZYSTYWANE W PROCESIE UCZENIA
epoch = 1
scoreInEpochs = []
meanScore = 0
bestScore = [0,0]
fullMemoryEpoch = 0
win = False

while epoch<=epochs and not win:
    # NOWA GRA -- reset środowiska, i początkowy input
    env.reset()
    currentState = env.newState(False)
    nextState = currentState
    gameOver = False

    while not gameOver:
        # ustalenie czy podejmowana akcja będzie losowa czy predykowane przez sieć (prawdopodobieństwo = epsilon)
        if random() <= epsilon:
            action = randint(0, 2)
        else:
            action = argmax(model.predict(currentState))

        # podjęcie akcji
        nextState, reward, gameOver, win = env.step(action)
        env.drawScreen()

        # umieszczenie ruchu w pamięci i trening sieci na pobranym batchu
        DQN.remember([currentState, action, reward, nextState], gameOver)
        inputs, targets = DQN.getBatch(model, batchSize)
        model.train_on_batch(inputs, targets)

        currentState = nextState

    # zmniejszenie prawdopodobieństwa losowości
    if epsilon > minEpsilon:
        epsilon *= epsilonMultiplier
    else:
        epsilon = minEpsilon

    # statystyki z pojedynczej gry
    if env.score > bestScore[0] or (env.score == bestScore[0] and env.moves < bestScore[1]):
        bestScore = [env.score,env.moves]
        print("NEW BEST SCORE:",bestScore[0],"points in", bestScore[1], "moves")
    print("Epoch:\t", epoch, "Score:\t", env.score, "Moves:\t", env.moves, "Epsilon:\t", round(epsilon, 5), "Best score:", bestScore[0])
    meanScore+=env.score

    # co 100 epok -- statystyka ze 100 epok
    if epoch % 100 == 0:
        scoreInEpochs.append(meanScore/100)
        print("--------------------------------------------------------------------------------------------------")
        print("MEAN SCORE IN LAST 100 EPOCHS:", meanScore/100, "ALL TIME BEST SCORE:", bestScore[0], "in", bestScore[1], "moves. ACTUAL MEMORY CAPACITY:", len(DQN.memory))
        plt.plot(scoreInEpochs)
        plt.xlabel('Epoki*100')
        plt.ylabel('Średni wynik w 100 epokach')
        plt_name = 'model.vision_'+str(vision)+'.cordinate_'+str(cordinate)+'.jpg'
        plt.savefig(plt_name)
        plt.show()
        plt.clf()
        plt.cla()
        print("--------------------------------------------------------------------------------------------------")
        meanScore = 0

    # zapisanie epoki, w której pamięć się zapełniła
    if len(DQN.memory) < maxMemory:
        fullMemoryEpoch = epoch+1

    epoch += 1

model_name = 'model.vision_'+str(vision)+'.cordinate_'+str(cordinate)+'.h5'
model.save(model_name)