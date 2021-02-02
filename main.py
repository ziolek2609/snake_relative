from numpy import argmax
from random import random, randint
import matplotlib.pyplot as plt
from dqn import Dqn
from neural_network import NeuralNetwork
from snake_environment import SnakeEnvironment

# STAŁE PARAMETRY UCZENIA

gamma = 0.9  # parametr dyskontujący do dqn
epsilon = 1  # prawdopodobieństwo podjęcia losowego ruchu przez snake'a w danej epoce
epsilonMultiplier = 0.999  # zmiana epsilon po każdej grze
minEpsilon = 0.05  # minimalna wartość prawdopodobnieństw ruchu losowego
epochs = 10000 # liczba epok (rozegranych gier)
waitTime = 0  # czas pomiędzy przesunięciami węża, gdy == 0, czas przesunięcia zależy od możliwości komputera
nSegments = 4  # ilość segmentów na jednym boku ekranu
cordinate = 2 # koordynaty względne
modelNum = 0  # numeracja tworzonych modeli
bestMeans = []  # przechowuje najlepsze srednie z 


for vision in [1,2]:
    for learningRate in [0.01, 0.005]:
        for batchSize in [128,256]:
            for maxMemory in [10000, 15000]:
                for rewards in [[-0.02,1,-2], [-0.1,1,-2], [-0.02,3,-2], [-0.02,1,-4]]:            

                    # STWORZENIE ŚRODOWISKA, MODELU SIECI ORAZ DQN
                    env = SnakeEnvironment(waitTime=waitTime, segments=nSegments,
                                           vision=vision, livingPenalty=rewards[0],
                                           posReward=rewards[1], negReward=rewards[2],
                                           cordinate = cordinate)
                    nn = NeuralNetwork(21, 3, learningRate)
                    model = nn.model
                    DQN = Dqn(gamma, maxMemory)
                    modelNum += 1
                    print(f"TRAINING MODEL {modelNum}/216 in progress")
                    
                    # ZMIENNE WYKORZYSTYWANE W PROCESIE UCZENIA
                    epoch = 1
                    scoreInEpochs = []
                    meanScore = 0
                    bestMeanScore = 0
                    bestScore = [0,0]
                    fullMemoryEpoch = 0
                    win = False
                    winNum = 0
                    
                    while epoch<=epochs:
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
                            
                            # zliczanie zwycięstw
                            if win:
                                winNum +=1
                    
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
                            #print("NEW BEST SCORE:",bestScore[0],"points in", bestScore[1], "moves")
                        #print("Epoch:\t", epoch, "Score:\t", env.score, "Moves:\t", env.moves, "Epsilon:\t", round(epsilon, 5), "Best score:", bestScore[0])
                        meanScore+=env.score
                    
                        # co 100 epok -- statystyka ze 100 epok
                        if epoch % 100 == 0:
                            scoreInEpochs.append(meanScore/100)
                            #print("MEAN SCORE IN LAST 100 EPOCHS:", meanScore/100, "ALL TIME BEST SCORE:", bestScore[0], "in", bestScore[1], "moves. ACTUAL MEMORY CAPACITY:", len(DQN.memory))
                            plt.plot(scoreInEpochs)
                            plt.xlabel('Epoki*100')
                            plt.ylabel('Średni wynik w 100 epokach')
                            plt_name = "wykresy/model"+str(modelNum)+".jpg"
                            plt.savefig(plt_name)
                            #plt.show()
                            plt.clf()
                            plt.cla()
                            
                            if meanScore/100 > bestMeanScore:
                                bestMeanScore = meanScore/100
                            meanScore = 0
                    
                        # zapisanie epoki, w której pamięć się zapełniła
                        if len(DQN.memory) < maxMemory:
                            fullMemoryEpoch = epoch+1
                    
                        epoch += 1
                    
                    # zapisanie modelu i edycja spisu modeli, zakończenie uczenia pojedynczego modelu
                    model_name = "modele/model"+str(modelNum)+".h5"
                    model.save(model_name)
                    file = open("spis_modeli.txt", "a")
                    string = f"MODEL {modelNum}\nVision: {vision}\nRewards: {rewards}\nMaxMemory: {maxMemory}\nBatchSize: {batchSize}\nLearningRate {learningRate}\nBest score: {bestScore[0]} in {bestScore[1]} moves \nFull memory in epoch: {fullMemoryEpoch}\nNumber of wins: {winNum} \nBest MeanScore: {bestMeanScore}\n\n"
                    file.write(string)
                    file.close()
                    bestMeans.append(bestMeanScore)


plt.plot(bestMeans)
plt.xlabel('Numer modelu')
plt.ylabel('Najlepszy wynik w 100 epokach w modelu')
plt_name = "wykresy/bestMeans.jpg"
plt.savefig(plt_name)
# plt.show()
file = open("spis_modeli.txt", "a")
file.write(str(bestMeans))

print("TRAINING MODELS COMPLETED!:)")