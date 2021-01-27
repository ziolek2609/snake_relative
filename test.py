from snake_environment import SnakeEnvironment
from numpy import argmax
from keras.models import load_model

waitTime = 50
nSegments = 8
nAttempts = 100
model_name = 'abc.h5'
scoreSum = 0
maxMoves = 100

env = SnakeEnvironment(segments = nSegments, waitTime = waitTime, segmentSize = 40)
model = load_model(model_name)

for i in range(nAttempts):
    env.reset()
    currentState = env.newState(False)
    nextState = currentState
    gameOver = False
    while not gameOver:
        action = argmax(model.predict(currentState))
        nextState, reward, gameOver, win = env.step(action)
        env.drawScreen()
        currentState = nextState
        if env.moves > maxMoves:
            gameOver = True
    scoreSum += env.score
    print("Score:\t", env.score, "Moves:\t", env.moves)

print("Mean score in", nAttempts, "attempts:", scoreSum/nAttempts)


