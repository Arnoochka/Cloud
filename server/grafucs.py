import matplotlib.pyplot as plt
import numpy as np

if __name__=="__main__":
    n = int(input())
    answers = [0]*n
    num = [0]*n
    for i in range(n):
        num = i
        answers = float(input())
    plt.plot(answers,num)
    plt.show()