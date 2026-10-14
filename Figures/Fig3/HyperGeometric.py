import math
import numpy as np
import itertools


def combinatoire(a, b):
    comb = math.factorial(a) / (math.factorial(b) * math.factorial(a - b))
    return comb


def hyper_gemotric_distribution(n, corrupt_count, w, k):
    first_term = combinatoire(corrupt_count, k)
    second_term = combinatoire(n - corrupt_count, w - k)
    third_term = combinatoire(n, w)
    prob = first_term * second_term / third_term
    return prob


def topologies():
    n = 100
    corrupt_count = 10
    l = 3
    w = n // l
    combinations = itertools.product(range(corrupt_count + 1), repeat=l)
    b = [
        np.array(tuple) for tuple in combinations if sum(tuple) == corrupt_count and max(tuple) <= w
    ]

    prob_path = math.pow(1 / w, l)
    summation = 0
    for i in range(len(b)):
        prod = 1
        st = corrupt_count
        ft = n
        for j in range(l - 1):
            prod *= b[i][j] * hyper_gemotric_distribution(ft, st, w, b[i][j])
            ft = ft - w
            st = st - b[i][j]

        prod *= b[i][-1]
        summation += prod
    pr_f = prob_path * summation
    return pr_f


if __name__ == "__main__":
    alpha_f = topologies()
    print("Geometric Distribution")
    print("alpha_F", alpha_f)
