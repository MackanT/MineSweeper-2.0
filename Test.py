import numpy as np
import matplotlib.pyplot as plt

TRIALS = int(1e4)
BETA = 2

RUN_TIME = 100
MU = np.zeros(RUN_TIME)

P = 7
N = 20


class Test():

    def __init__(self):
        self.run_test()

    def run_test(self):

        mu = np.zeros(RUN_TIME)

        for iter in range(1, RUN_TIME):

            pattern = self.generate_pattern(-1)
            weights = np.zeros([N, N])

            for i in range(1, np.size(weights, 0)):
                for j in range(1, np.size(weights, 1)):
                    w = 0

                    if i != j:
                        for k in range(1, np.size(pattern, 0)):
                            w = w + pattern[k, i]*pattern[k, j]
                    weights[i, j] = w/N

            rand_pos = np.random.randint(1, N, TRIALS)
            s_prime = pattern[1]

            for t in range(TRIALS):

                bM = np.sum(weights[rand_pos[t]]*s_prime)
                pB = 1 / (1+np.exp(-2*BETA*bM))

                if np.random.rand() < pB:
                    s_prime[rand_pos[t]] = 1
                else:
                    s_prime[rand_pos[t]] = -1

                n_sum = np.sum(s_prime * pattern) / N
                mu[iter] += n_sum/TRIALS

        plt.plot(mu)
        plt.show()

    def generate_pattern(self, replacement):

        pattern = np.random.randint(0, 2, [N, N])
        pattern[np.where(pattern == 0)] = replacement
        return pattern


run = Test()
